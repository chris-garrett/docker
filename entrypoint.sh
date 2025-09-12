#!/usr/bin/env bash
set -Eeuo pipefail

PUID="${PUID:-1000}"
PGID="${PGID:-1000}"

# Ensure we're running as root
if [ "$(id -u)" -ne 0 ]; then
  echo "This entrypoint must be run as root. Current UID: $(id -u)" >&2
  exit 1
fi

# If 'sprout' exists but IDs don't match, delete and recreate
if id -u sprout &>/dev/null; then
  CURRENT_UID="$(id -u sprout)"
  CURRENT_GID="$(id -g sprout)"
  if [ "$CURRENT_UID" != "$PUID" ] || [ "$CURRENT_GID" != "$PGID" ]; then
    echo "Recreating user 'sprout' with UID=$PUID and GID=$PGID (was UID=$CURRENT_UID GID=$CURRENT_GID)"
    userdel -r -f sprout >/dev/null 2>&1 || true
    if getent group sprout >/dev/null; then
      groupdel sprout >/dev/null 2>&1 || true
    fi
  fi
fi

# Ensure group 'sprout' with PGID exists
if ! getent group sprout >/dev/null; then
  groupadd -g "$PGID" sprout
else
  CURRENT_GID="$(getent group sprout | cut -d: -f3)"
  if [ "$CURRENT_GID" != "$PGID" ]; then
    groupdel sprout >/dev/null 2>&1 || true
    groupadd -g "$PGID" sprout
  fi
fi

# Ensure user 'sprout' with PUID exists
HOME_DIR="/home/sprout"
if ! id -u sprout &>/dev/null; then
  if [ -d "$HOME_DIR" ]; then
    # Home already exists (maybe from base image or a mounted volume) -> don't create, just use it
    useradd -M -d "$HOME_DIR" -u "$PUID" -g sprout -s /bin/bash sprout
  else
    # Create the home directory
    useradd -m -d "$HOME_DIR" -u "$PUID" -g sprout -s /bin/bash sprout
    echo "alias l='ls -laFHh'" >> /home/sprout/.bashrc
    echo "export PATH=\"/work/opt/bin:\$$PATH\"" >> /home/sprout/.bashrc
  fi
else
  CURRENT_UID="$(id -u sprout)"
  if [ "$CURRENT_UID" != "$PUID" ]; then
    usermod -u "$PUID" sprout
  fi
fi

# Fix ownership of required paths
mkdir -p "$HOME_DIR" /work
chown -R sprout:sprout "$HOME_DIR" /work

# Execute the passed command as 'sprout'
if [ "$#" -eq 0 ]; then
  exec gosu sprout /bin/bash
else
  exec gosu sprout "$@"
fi
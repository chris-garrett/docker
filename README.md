# Docker

Kitchen sink developer images. These are intended for use with docker compose.

[![Python: Build](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml) [![Python: Version](https://img.shields.io/github/v/tag/chris-garrett/docker?filter=python%2Fv*&label=version)](https://github.com/chris-garrett/docker/pkgs/container/python)
[![Rust: Build](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml) [![Rust: Version](https://img.shields.io/github/v/tag/chris-garrett/docker?filter=rust%2Fv*&label=version)](https://github.com/chris-garrett/docker/pkgs/container/rust)
[![Node: Build](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml) [![Node: Version](https://img.shields.io/github/v/tag/chris-garrett/docker?filter=node%2Fv*&label=version)](https://github.com/chris-garrett/docker/pkgs/container/node)
[![Postgres: Build](https://github.com/chris-garrett/docker/actions/workflows/build-postgres.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-postgres.yaml) [![Postgres: Version](https://img.shields.io/github/v/tag/chris-garrett/docker?filter=postgres%2Fv*&label=version)](https://github.com/chris-garrett/docker/pkgs/container/postgres)
[![Devops: Build](https://github.com/chris-garrett/docker/actions/workflows/build-devops.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-devops.yaml) [![Devops: Version](https://img.shields.io/github/v/tag/chris-garrett/docker?filter=devops%2Fv*&label=version)](https://github.com/chris-garrett/docker/pkgs/container/devops)
[![Keycloak: Build](https://github.com/chris-garrett/docker/actions/workflows/build-keycloak.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-keycloak.yaml) [![Keycloak: Version](https://img.shields.io/github/v/tag/chris-garrett/docker?filter=keycloak%2Fv*&label=version)](https://github.com/chris-garrett/docker/pkgs/container/keycloak)
[![Java: Build](https://github.com/chris-garrett/docker/actions/workflows/build-java.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-java.yaml) [![Java: Version](https://img.shields.io/github/v/tag/chris-garrett/docker?filter=java%2Fv*&label=version)](https://github.com/chris-garrett/docker/pkgs/container/java)


## Versions

### Python 26.49.0

`docker pull ghcr.io/chris-garrett/python:26.49.0`

- Act_runner: **5.4.1**
- Actions_runner: **2.338.2**
- Curl: **8.23.0-1**
- Dockerize: **0.16.0**
- Python: **3.15.2**
- Uv: **0.13.7**
- Watchexec: **2.8.0**

### Rust 26.54.0

`docker pull ghcr.io/chris-garrett/rust:26.54.0`

- Act_runner: **5.4.1**
- Actions_runner: **2.338.2**
- Curl: **8.23.0-1**
- Dockerize: **0.16.0**
- Rust: **1.99.1**
- Sccache: **0.19.0**
- Watchexec: **2.8.0**

### Node 26.50.0

`docker pull ghcr.io/chris-garrett/node:26.50.0`

- Act_runner: **5.4.1**
- Actions_runner: **2.338.2**
- Bun: **1.4.4**
- Corepack: **0.36.0**
- Curl: **8.23.0-1**
- Dockerize: **0.16.0**
- Fnm: **1.39.0**
- Node: **26.13.0**
- Vite_plus: **1.5.1**
- Watchexec: **2.8.0**

### Postgres 26.29.0

`docker pull ghcr.io/chris-garrett/postgres:26.29.0`

- Cnpg_postgis: **17.12-3.7.0-202611201731-standard-trixie**
- Pgvector: **0.8.7**
- Postgis: **3.7.0**
- Postgres: **17.12**

### Devops 26.48.0

`docker pull ghcr.io/chris-garrett/devops:26.48.0`

- Act_runner: **5.4.1**
- Actions_runner: **2.338.2**
- Aws: **2.39.7**
- Azure_cli: **2.92.0-1~bookworm**
- Curl: **8.23.0-1**
- Dockerize: **0.16.0**
- Duckdb: **2.0.0**
- Easyrsa: **3.2.2-1**
- Jq: **1.7.1-6+deb13u4**
- K9s: **0.51.0**
- Kubectl: **1.37.2**
- Kubelogin: **0.2.22**
- Neovim: **0.10.4-8+deb13u1**
- Openssh_server: **1:10.0p1-7+deb13u4**
- Openvpn: **2.6.14-1+deb13u3**
- Psql17: **17.11-1.pgdg13+2**
- Psql18: **18.6-1.pgdg13+2**
- Sqlite3: **3.46.1-7+deb13u2**
- Tini: **0.19.0**
- Tofu: **1.13.9**
- Watchexec: **2.8.0**

### Keycloak 26.1.0

`docker pull ghcr.io/chris-garrett/keycloak:26.1.0`

- Dockerize: **0.16.0**
- Keycloak: **26.7.5**

### Java 26.8.0

`docker pull ghcr.io/chris-garrett/java:26.8.0`

- Act_runner: **5.4.1**
- Actions_runner: **2.338.2**
- Curl: **8.23.0-1**
- Dockerize: **0.16.0**
- Java: **21**
- Maven: **3.10**
- Watchexec: **2.8.0**

## Examples

See `examples` folder

Bring up stack

```
./task ex:restart ex:log
```

Visit the api endpoints:

- http://py.fbi.com - Python FastApi example
- http://rust.fbi.com - Rust Api example (TODO)
- http://node.fbi.com - Node Frontend example (TODO)
- http://cs.fbi.com - .Net Api example (TODO)

Bring it down

```
./task ex:down
```

#### Images

- [Python @ py.fbi.com](py.fbi.com)
- [Node @ ts.fbi.com](ts.fbi.com)
- [Rust @ rs.fbi.com](rs.fbi.com)

#### Services

- [Caddy @ caddy.fbi.com](caddy.fbi.com)
- [OpenObserve @ o2.fbi.com](o2.fbi.com)
  - username: docker@fbi.com
  - password: U7FfkmB1ZcgGoan8

## Todo

There are improvements that can be made on image size.

- remove doc / man files
- remove extras
- found that folks are not stripping binaries :/

## References

- https://github.com/linuxserver/docker-baseimage-debian
- https://github.com/just-containers/s6-overlay
- https://docs.linuxserver.io/general/running-our-containers/#base-images
- https://github.com/jlesage/docker-baseimage
- https://github.com/sudo-bmitch/docker-base
- https://patorjk.com/software/taag
  - Note: LinuxServer.io requests that you replace their brand banner.
  - I used Font: Alligator2

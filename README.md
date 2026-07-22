# Docker

Kitchen sink developer images. These are intended for use with docker compose.

[![Python: Build](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml)
[![Rust: Build](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml)
[![Node: Build](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml)
[![Postgres: Build](https://github.com/chris-garrett/docker/actions/workflows/build-postgres.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-postgres.yaml)
[![Devops: Build](https://github.com/chris-garrett/docker/actions/workflows/build-devops.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-devops.yaml)


## Versions

### Python 26.13.0

`docker pull ghcr.io/chris-garrett/python:26.13.0`

- Act_runner: **0.6.1**
- Actions_runner: **2.335.0**
- Dockerize: **0.9.9**
- Python: **3.12**
- Uv: **0.9.25**
- Watchexec: **2.3.2**

### Rust 26.15.0

`docker pull ghcr.io/chris-garrett/rust:26.15.0`

- Act_runner: **0.6.1**
- Actions_runner: **2.335.0**
- Dockerize: **0.9.9**
- Rust: **1.92.0**
- Watchexec: **2.3.2**

### Node 26.14.0

`docker pull ghcr.io/chris-garrett/node:26.14.0`

- Act_runner: **0.6.1**
- Actions_runner: **2.335.0**
- Bun: **1.3.6**
- Dockerize: **0.9.9**
- Fnm: **1.38.1**
- Node: **22.22.0**
- Watchexec: **2.3.2**

### Postgres 26.11.0

`docker pull ghcr.io/chris-garrett/postgres:26.11.0`

- Pgvector: **0.8.3**
- Postgis: **17-3.6-alpine**

### Devops 26.9.0

`docker pull ghcr.io/chris-garrett/devops:26.9.0`

- Act_runner: **0.6.1**
- Actions_runner: **2.335.0**
- Aws: **2.27.40**
- Azure_cli: **2.86.0-1~bookworm**
- Dockerize: **0.9.9**
- Duckdb: **1.5.2**
- Easyrsa: **3.2.2-1**
- Jq: **1.7.1-6+deb13u2**
- K9s: **0.50.18**
- Kubectl: **1.36.1**
- Kubelogin: **0.2.17**
- Neovim: **0.10.4-8**
- Openssh_server: **1:10.0p1-7+deb13u4**
- Openvpn: **2.6.14***
- Psql17: **17.9-1.pgdg13+1**
- Psql18: **18.3-1.pgdg13+1**
- Sqlite3: **3.46.1-7+deb13u1**
- Tini: **0.19.0**
- Tofu: **1.11.7**
- Watchexec: **2.3.2**

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

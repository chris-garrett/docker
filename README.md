# Docker

Kitchen sink developer images. These are intended for use with docker compose.

[![Python: Build](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml)
[![Rust: Build](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml)
[![Node: Build](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml)
[![Postgres: Build](https://github.com/chris-garrett/docker/actions/workflows/build-postgres.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-postgres.yaml)


## Versions

### Python 26.1.0

`docker pull ghcr.io/chris-garrett/python:26.1.0`

- Dockerize: **0.9.9**
- Python: **3.12**
- Uv: **0.9.25**
- Watchexec: **2.3.2**

### Rust 26.2.0

`docker pull ghcr.io/chris-garrett/rust:26.2.0`

- Dockerize: **0.9.9**
- Rust: **1.92.0**
- Watchexec: **2.3.2**

### Node 26.1.0

`docker pull ghcr.io/chris-garrett/node:26.1.0`

- Bun: **1.3.6**
- Dockerize: **0.9.9**
- Fnm: **1.38.1**
- Node: **22.22.0**
- Watchexec: **2.3.2**

### Postgres 26.1.0

`docker pull ghcr.io/chris-garrett/postgres:26.1.0`

- Pgvector: **0.8.1**
- Postgis: **17-3.6-alpine**

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

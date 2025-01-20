# Docker

[![Python: Build](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml)

[![Rust: Build](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml)

[![Node: Build](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml)

Kitchen sink developer images. These are intended for use with docker compose.

## Versions

### Python 25.5.0

`docker pull ghcr.io/chris-garrett/python:25.5.0`

- Dockerize: **0.7.0**
- Python: **3.12**
- Uv: **0.5.21**
- Watchexec: **2.1.2**
### Rust 25.2.0

```docker pull ghcr.io/chris-garrett/rust:25.2.0```

* Dockerize: **0.7.0**
* Rust: **1.84.0**
* Watchexec: **2.1.2**


## Node 25.3.0

```docker pull ghcr.io/chris-garrett/node:25.3.0```

* Bun: **1.1.45**
* Dockerize: **0.7.0**
* Fnm: **1.38.1**
* Node: **20.16.0**
* Watchexec: **2.1.2**


## Examples

See `examples` folder

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

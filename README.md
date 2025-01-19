# Docker

[![Python: Build](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-python.yaml)

[![Rust: Build](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-rust.yaml)

[![Node: Build](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml/badge.svg)](https://github.com/chris-garrett/docker/actions/workflows/build-node.yaml)


Kitchen sink developer images. These are intended for use with docker compose. 

## Versions

### Python

* Dockerize: **0.7.0**
* Python: **3.12**
* Uv: **0.5.21**
* Watchexec: **2.1.2**


## Rust

* Dockerize: **0.7.0**
* Rust: **1.84.0**
* Watchexec: **2.1.2**


## Node

* Bun: **1.1.45**
* Dockerize: **0.7.0**
* Fnm: **1.38.1**
* Node: **20.16.0**
* Watchexec: **2.1.2**


## Todo

There are improvements that can be made on image size. 
* remove doc / man files
* remove extras
* found that folks are not stripping binaries :/


## Example

```docker-compose

```
## References

* https://github.com/linuxserver/docker-baseimage-debian
* https://github.com/just-containers/s6-overlay
* https://docs.linuxserver.io/general/running-our-containers/#base-images
* https://github.com/jlesage/docker-baseimage
* https://github.com/sudo-bmitch/docker-base


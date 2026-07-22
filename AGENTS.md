# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A build system for "kitchen sink" developer Docker images, published to `ghcr.io/chris-garrett/<name>`. Five images: **python**, **node**, **rust**, **devops**, **postgres**. Each bundles common CI/dev tooling on top of a language/service base. Images are meant to be used with docker compose (see `examples/`).

There is no application source and no test suite — "correctness" means the Dockerfile generates and the image builds. Verify changes by building the image locally.

## The `./task` runner

All work goes through `./task`, a bash shim that bootstraps `uv` (pinned by `UV_VERSION` in `config.env`) and runs a small Python task framework in `.task/`. Tasks are discovered from any `**/__task__.py` file exposing `configure(builder)`:

- `.task/__task__.py` → container tasks (`configure` registers per-service tasks via `__ci__.py`)
- `examples/__task__.py` → docker-compose tasks for the example stack

Run `./task <task>`. Multiple tasks chain: `./task ex:restart ex:log`.

### Container tasks (per service: python, node, rust, devops, postgres)

| Task | Does |
|------|------|
| `<svc>:update` | Regenerate `Dockerfile.<svc>` from templates + `config.env`, build single-arch, refresh SBOM and README |
| `<svc>:build`  | `docker buildx build` the generated Dockerfile (multi-arch + `--push` only when `CI` is set; local builds are single-arch `--load`) |
| `<svc>:sbom`   | Regenerate `Dockerfile.<svc>.sbom` (base-image digest, package labels, OS package list) |
| `<svc>:readme` | Rewrite the service's version block in `README.md` from image labels |
| `<svc>:pr`     | Branch, commit, open, approve, and squash-merge a version-bump PR (CI only) |
| `<svc>:tag`    | Create/push the git tag `<svc>/vMAJOR.MINOR.PATCH` (CI only) |

`./task update` runs every service's `:update`. `./task info` prints paths.

### Example-stack tasks (compose)

`ex:up`, `ex:down`, `ex:restart`, `ex:log` (follow), `ex:nlog` (no follow), `ex:pull`, `ex:nuke` (down + remove volumes). Which services start is controlled by `SERVICE_PROFILES` in `.env` (e.g. `caddy o2 py node`).

## Dockerfile generation — critical

**`Dockerfile.<svc>` and `Dockerfile.<svc>.sbom` are GENERATED. Never hand-edit them.** Edit the sources and run `./task <svc>:update`.

There are two generation patterns:

1. **Common/layered** (python, node, rust, devops): `Dockerfile.<svc>.build` + `Dockerfile.<svc>.final` are substituted into `$BUILD_TEMPLATE` / `$FINAL_TEMPLATE` placeholders in **`Dockerfile.common`**. `Dockerfile.common` provides the shared Debian base and tooling installed into `/work/opt/bin` (watchexec, dockerize, static curl, GitHub Actions runner, Gitea act_runner). The `.build` fragment adds the language toolchain; the `.final` fragment sets runtime env and version `LABEL`s. (`__ci__.py`: `_add_service` / `update_service_deprecated`.)

2. **Standalone template** (postgres): `Dockerfile.<svc>.templ` is a complete multi-stage Dockerfile; no `Dockerfile.common`. (`__ci__.py`: `_add_postgres_service` / `update_service`.)

Templating is Python `string.Template` fed by `config.env`. Because `$` is the substitution char, **literal shell `$` in a template must be escaped as `$$`** (e.g. `$$TARGETARCH`, `$$PATH`).

## Versioning & config

- **All version pins live in `config.env`.** To bump a tool, change its `*_VERSION` there, then `./task <svc>:update`. Every `config.env` key ending in `_VERSION` is passed to the build as a `--build-arg`.
- Image version = git tag per service, `<svc>/vMAJOR.MINOR.PATCH`, computed by `.task/__version__.py`. On `main` the patch bumps; on any other branch the minor bumps. `README.md` version blocks and `*.sbom` files are derived from `org.opencontainers.image.<tool>_version` labels, so those labels are load-bearing, not decorative.

## CI (GitHub Actions, `.github/workflows/`)

- `update-<svc>.yaml` — daily cron → `<svc>:update` then `<svc>:pr` (auto version-bump PR). Uses the composite action `.github/actions/update-dockerfile`.
- `build-<svc>.yaml` — on push to `main` (and PRs) touching `config.env`, `Dockerfile.<svc>`, or `Dockerfile.<svc>.sbom` → `<svc>:build` (multi-arch push) + `<svc>:tag`. Uses `.github/actions/build-image`.
- Auto-merge deliberately uses the PAT `CI_GITHUB_TOKEN` (not the default `GITHUB_TOKEN`). Pushing to `main` with `GITHUB_TOKEN` would not trigger the `build-*` workflows (GitHub anti-recursion), so the build would never fire. Keep merges on the PAT.

## Runtime behavior

Images run `entrypoint.sh`: it creates/reconciles a non-root user `sprout` at `PUID`/`PGID` (default 1000/1000), fixes ownership of `/work` and `/home/sprout`, then drops privileges with `gosu` to exec the command. Workdir is `/work/app`; installed tools are on `PATH` at `/work/opt/bin`.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A build system for developer and service Docker images, published to `ghcr.io/chris-garrett/<name>`. Seven images: **python**, **node**, **rust**, **devops**, **postgres**, **keycloak**, **java**. Images are meant to be used with docker compose (see `examples/`).

There is no application source and no test suite — "correctness" means the Dockerfile generates and the image builds. Verify changes by building the image locally.

Do not add incidental change notes or package-installation commentary to `README.md`; keep image/version updates in the existing sections.

## The `./task` runner

All work goes through `./task`, a bash shim that bootstraps `uv` (pinned by `UV_VERSION` in `config.env`) and runs a small Python task framework in `.task/`. Tasks are discovered from any `**/__task__.py` file exposing `configure(builder)`:

- `.task/__task__.py` → container tasks (`configure` registers per-service tasks via `__ci__.py`)
- `examples/__task__.py` → docker-compose tasks for the example stack

Run `./task <task>`. Multiple tasks chain: `./task ex:restart ex:log`.

### Container tasks (per service: python, node, rust, devops, postgres, keycloak, java)

| Task | Does |
|------|------|
| `<svc>:update` | Regenerate `Dockerfile.<svc>` from templates + `config.env`, build single-arch, refresh SBOM and README |
| `<svc>:build`  | Build one explicit version tag; only main CI publishes multi-arch images, while PR/local builds use single-arch `--load` |
| `<svc>:sbom`   | Regenerate `Dockerfile.<svc>.sbom` (base-image digest, package labels, OS package list) |
| `<svc>:readme` | Rewrite the service's pinned README reference using its current release tag and tool-version labels |
| `<svc>:pr`     | Branch, commit, open, approve, and squash-merge a version-bump PR (CI only) |
| `<svc>:tag`    | Create/push the git tag `<svc>/vMAJOR.MINOR.PATCH` (CI only) |
| `<svc>:publish-readme` | After a main release, update the pinned README section through GitHub's Contents API, preserving concurrent releases |

`./task update` runs every service's `:update`. `./task info` prints paths.

### Example-stack tasks (compose)

`ex:up`, `ex:down`, `ex:restart`, `ex:log` (follow), `ex:nlog` (no follow), `ex:pull`, `ex:nuke` (down + remove volumes). Which services start is controlled by `SERVICE_PROFILES` in `.env` (e.g. `caddy o2 py node`).

## Dockerfile generation — critical

**`Dockerfile.<svc>` and `Dockerfile.<svc>.sbom` are GENERATED. Never hand-edit them.** Edit the sources and run `./task <svc>:update`.

There are two generation patterns:

1. **Common/layered** (python, node, rust, devops, java): `Dockerfile.<svc>.build` + `Dockerfile.<svc>.final` are substituted into `$BUILD_TEMPLATE` / `$FINAL_TEMPLATE` placeholders in **`Dockerfile.common`**. `Dockerfile.common` provides the shared Debian base and tooling installed into `/work/opt/bin` (watchexec, dockerize, static curl, GitHub Actions runner, Gitea act_runner). The `.build` fragment adds the language toolchain; the `.final` fragment sets runtime env and version `LABEL`s. Java copies JDK and Maven from the configured Maven/Temurin image. (`__ci__.py`: `_add_service` / `update_service_deprecated`.)

2. **Standalone template** (postgres, keycloak): `Dockerfile.<svc>.templ` is a complete Dockerfile; no `Dockerfile.common`. These images preserve their upstream entrypoints and runtime defaults. (`.task/__task__.py`: `_add_template_service`; `__ci__.py`: `update_service`.)

Templating is Python `string.Template` fed by `config.env`. Because `$` is the substitution char, **literal shell `$` in a template must be escaped as `$$`** (e.g. `$$TARGETARCH`, `$$PATH`).

## Versioning & config

- **All version pins live in `config.env`.** To bump a tool, change its `*_VERSION` there, then `./task <svc>:update`. Every `config.env` key ending in `_VERSION` is passed to the build as a `--build-arg`.
- Image version = git tag per service, `<svc>/vMAJOR.MINOR.PATCH`, computed by `.task/__version__.py`. On `main` the patch bumps; on any other branch the minor bumps. README tool-version lists and `*.sbom` files are derived from `org.opencontainers.image.<tool>_version` labels, so those labels are load-bearing, not decorative.
- For new services, create and push an initial `<svc>/vYY.0.0` tag on an ancestor commit before pushing the implementation. `YY` is the two-digit year; use the existing version logic, not a code change, to produce the first release.
- Images are immutable: never build or publish a `:latest` alias, never overwrite an existing published version, and never force-update or delete release tags from PR workflows. README pull commands must pin explicit versions.
- `:update` documents the exact local build version. `:readme` refreshes pins from release tags. Main CI runs `:publish-readme` after a successful publish/tag to keep README pins current; SHA conflicts are re-fetched so concurrent releases do not overwrite each other's sections. Version badges remain live service-tag badges.
- SBOM generation supports Debian, Alpine, and RPM images. For UBI-micro images without an RPM CLI, it queries a temporary copy of the RPM database using `RPM_SBOM_IMAGE`; no tools are added to the runtime image.

## CI (GitHub Actions, `.github/workflows/`)

- `update-<svc>.yaml` — daily cron → `<svc>:update` then `<svc>:pr` (auto version-bump PR). Uses the composite action `.github/actions/update-dockerfile`.
- `build-<svc>.yaml` validates PRs with a local single-architecture build. Only CI builds on `refs/heads/main` publish multi-architecture versioned images and release tags. PRs must never push images or tags. Uses `.github/actions/build-image`.
- Successful image builds append the exact version and image tag to GitHub Actions' `GITHUB_STEP_SUMMARY`.
- Auto-merge deliberately uses the PAT `CI_GITHUB_TOKEN` (not the default `GITHUB_TOKEN`). Pushing to `main` with `GITHUB_TOKEN` would not trigger the `build-*` workflows (GitHub anti-recursion), so the build would never fire. Keep merges on the PAT.
- PR creation also uses `CI_GITHUB_TOKEN` so PR workflows run without manual workflow approval. PR reviews use the separate `GITHUB_TOKEN` bot identity because a PR author cannot approve their own PR. PR review approval does not approve workflow runs.
- Keycloak's existing private GHCR package is linked to `chris-garrett/devops`. Grant `chris-garrett/docker` Write access under the package's Manage Actions access settings so its standard `GITHUB_TOKEN` can publish; do not bypass missing package permissions with a PAT.
- Main build checkouts and release-tag pushes use `CI_GITHUB_TOKEN` with workflow permission: GitHub rejects bot-created tags pointing to commits that modify workflow files. PRs never receive this PAT; registry login and README publication continue to use `GITHUB_TOKEN`.

## Runtime behavior

The common/layered images run `entrypoint.sh`: it creates/reconciles a non-root user `sprout` at `PUID`/`PGID` (default 1000/1000), fixes ownership of `/work` and `/home/sprout`, then drops privileges with `gosu` to exec the command. Workdir is `/work/app`; installed tools are on `PATH` at `/work/opt/bin`. Standalone images retain their upstream entrypoints.

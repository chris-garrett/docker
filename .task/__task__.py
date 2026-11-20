import os
from __ci__ import (
    build_service,
    pr_service,
    tag_service,
    update_service,
    update_sbom,
    update_readme,
    publish_readme,
)
from __tasklib__ import TaskBuilder, TaskContext, load_dotenv


load_dotenv("config.env", override=True)
load_dotenv(".env", override=True)


def _info(ctx: TaskContext):
    ctx.log.info(f"root: {ctx.root_dir}")
    ctx.log.info(f"root: {ctx.project_dir}")


def _add_service(
    builder: TaskBuilder, mod: str, name: str, *, use_common: bool = True, platforms: str = None
):
    builder.add_task(
        mod, f"{name}:update", lambda ctx: update_service(ctx, name, use_common=use_common)
    )
    builder.add_task(mod, f"{name}:build", lambda ctx: build_service(ctx, name, platforms=platforms))
    builder.add_task(mod, f"{name}:sbom", lambda ctx: update_sbom(ctx, name))
    builder.add_task(mod, f"{name}:readme", lambda ctx: update_readme(ctx, name))
    builder.add_task(mod, f"{name}:publish-readme", lambda ctx: publish_readme(ctx, name))
    builder.add_task(mod, f"{name}:pr", lambda ctx: pr_service(ctx, name))
    builder.add_task(mod, f"{name}:tag", lambda ctx: tag_service(ctx, name))


def configure(builder: TaskBuilder):
    mod = "containers"

    _add_service(builder, mod, "python")
    _add_service(builder, mod, "node")
    _add_service(builder, mod, "rust")
    _add_service(builder, mod, "devops")
    _add_service(builder, mod, "java")
    _add_service(builder, mod, "postgres", use_common=False, platforms="linux/amd64")
    _add_service(builder, mod, "keycloak", use_common=False)

    builder.add_task(mod, "info", _info)
    builder.add_task(mod, "update", lambda ctx: None, ["python:update", "node:update", "rust:update", "devops:update", "postgres:update", "keycloak:update", "java:update"])

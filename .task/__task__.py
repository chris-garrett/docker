import os
from __ci__ import (
    build_service,
    pr_service,
    tag_service,
    update_service,
    update_service_deprecated,
    update_sbom,
    update_readme,
)
from __tasklib__ import TaskBuilder, TaskContext, load_dotenv


load_dotenv("config.env", override=True)
load_dotenv(".env", override=True)


def _info(ctx: TaskContext):
    ctx.log.info(f"root: {ctx.root_dir}")
    ctx.log.info(f"root: {ctx.project_dir}")


def _add_service(builder: TaskBuilder, mod: str, name: str):
    builder.add_task(
        mod, f"{name}:update", lambda ctx: update_service_deprecated(ctx, name)
    )
    builder.add_task(mod, f"{name}:build", lambda ctx: build_service(ctx, name))
    builder.add_task(mod, f"{name}:sbom", lambda ctx: update_sbom(ctx, name))
    builder.add_task(mod, f"{name}:readme", lambda ctx: update_readme(ctx, name))
    builder.add_task(mod, f"{name}:pr", lambda ctx: pr_service(ctx, name))
    builder.add_task(mod, f"{name}:tag", lambda ctx: tag_service(ctx, name))


def _add_postgres_service(builder: TaskBuilder, mod: str, name: str):
    builder.add_task(mod, f"{name}:update", lambda ctx: update_service(ctx, name))
    builder.add_task(mod, f"{name}:build", lambda ctx: build_service(ctx, name, platforms="linux/amd64"))
    builder.add_task(mod, f"{name}:tag", lambda ctx: tag_service(ctx, name))
    builder.add_task(mod, f"{name}:pr", lambda ctx: pr_service(ctx, name))
    builder.add_task(mod, f"{name}:sbom", lambda ctx: update_sbom(ctx, name))
    builder.add_task(mod, f"{name}:readme", lambda ctx: update_readme(ctx, name))


def configure(builder: TaskBuilder):
    mod = "containers"

    _add_service(builder, mod, "python")
    _add_service(builder, mod, "node")
    _add_service(builder, mod, "rust")
    _add_postgres_service(builder, mod, "postgres")

    builder.add_task(mod, "info", _info)
    builder.add_task(mod, "update", lambda ctx: None, ["python:update", "node:update", "rust:update", "postgres:update"])

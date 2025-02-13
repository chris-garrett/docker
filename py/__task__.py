from __ci__ import (
    build_service,
    pr_service,
    tag_service,
    update_service,
    update_sbom,
    update_readme,
)
from __tasklib__ import TaskBuilder, TaskContext, load_dotenv


load_dotenv("config.env", override=True)
load_dotenv(".env", override=True)


def _info(ctx: TaskContext):
    ctx.log.info(f"root: {ctx.root_dir}")
    ctx.log.info(f"root: {ctx.project_dir}")


def configure(builder: TaskBuilder):
    mod = "containers"

    builder.add_task(mod, "python:update", lambda ctx: update_service(ctx, "python"))
    builder.add_task(mod, "python:build", lambda ctx: build_service(ctx, "python"))
    builder.add_task(mod, "python:tag", lambda ctx: tag_service(ctx, "python"))
    builder.add_task(mod, "python:pr", lambda ctx: pr_service(ctx, "python"))
    builder.add_task(mod, "python:sbom", lambda ctx: update_sbom(ctx, "python"))
    builder.add_task(mod, "python:readme", lambda ctx: update_readme(ctx, "python"))

    builder.add_task(mod, "node:update", lambda ctx: update_service(ctx, "node"))
    builder.add_task(mod, "node:build", lambda ctx: build_service(ctx, "node"))
    builder.add_task(mod, "node:tag", lambda ctx: tag_service(ctx, "node"))
    builder.add_task(mod, "node:pr", lambda ctx: pr_service(ctx, "node"))
    builder.add_task(mod, "node:sbom", lambda ctx: update_sbom(ctx, "node"))
    builder.add_task(mod, "node:readme", lambda ctx: update_readme(ctx, "node"))

    builder.add_task(mod, "rust:update", lambda ctx: update_service(ctx, "rust"))
    builder.add_task(mod, "rust:build", lambda ctx: build_service(ctx, "rust"))
    builder.add_task(mod, "rust:tag", lambda ctx: tag_service(ctx, "rust"))
    builder.add_task(mod, "rust:pr", lambda ctx: pr_service(ctx, "rust"))
    builder.add_task(mod, "rust:sbom", lambda ctx: update_sbom(ctx, "rust"))
    builder.add_task(mod, "rust:readme", lambda ctx: update_readme(ctx, "rust"))

    builder.add_task(mod, "info", _info)

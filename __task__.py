from __ci__ import build_service, pr_service, tag_service, update_service, update_sbom
from __tasklib__ import TaskBuilder, load_dotenv


load_dotenv("config.env", override=True)
load_dotenv(".env", override=True)


def configure(builder: TaskBuilder):
    mod = "containers"

    builder.add_task(mod, "python:update", lambda ctx: update_service(ctx, "python"))
    builder.add_task(mod, "python:build", lambda ctx: build_service(ctx, "python"))
    builder.add_task(mod, "python:tag", lambda ctx: tag_service(ctx, "python"))
    builder.add_task(mod, "python:pr", lambda ctx: pr_service(ctx, "python"))
    builder.add_task(mod, "python:sbom", lambda ctx: update_sbom(ctx, "python"))

    builder.add_task(mod, "node:update", lambda ctx: update_service(ctx, "node"))
    builder.add_task(mod, "node:build", lambda ctx: build_service(ctx, "node"))
    builder.add_task(mod, "node:tag", lambda ctx: tag_service(ctx, "node"))
    builder.add_task(mod, "node:pr", lambda ctx: pr_service(ctx, "node"))
    builder.add_task(mod, "node:sbom", lambda ctx: update_sbom(ctx, "node"))

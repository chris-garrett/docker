from __ci__ import build_service, pr_service, tag_service, update_service
from __tasklib__ import TaskBuilder


def configure(builder: TaskBuilder):
    mod = "containers"

    builder.add_task(mod, "python:update", lambda ctx: update_service(ctx, "python"))
    builder.add_task(mod, "python:build", lambda ctx: build_service(ctx, "python"))
    builder.add_task(mod, "python:tag", lambda ctx: tag_service(ctx, "python"))
    builder.add_task(mod, "python:pr", lambda ctx: pr_service(ctx, "python"))

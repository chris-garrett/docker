import os
from __tasklib__ import TaskContext, TaskBuilder


def _prefix(ctx: TaskContext):
    compose_file = os.path.join(ctx.project_dir, "docker-compose.yml")
    return f"docker compose -f {compose_file}"


def _up(ctx: TaskContext):
    ctx.log.info("Starting docker-compose")
    ctx.exec(f"{_prefix(ctx)} up -d")


def _down(ctx: TaskContext):
    ctx.log.info("Stopping docker-compose")
    ctx.exec(f"{_prefix(ctx)} stop")
    ctx.exec(f"{_prefix(ctx)} rm -f")


def _logs(ctx: TaskContext):
    ctx.log.info("Showing docker-compose logs")
    ctx.exec(f"{_prefix(ctx)} logs -f --tail 100")


def _restart(ctx: TaskContext):
    _down(ctx)
    _up(ctx)


def configure(builder: TaskBuilder):
    module_name = "datalake"
    builder.add_task(module_name, "up", _up)
    builder.add_task(module_name, "down", _down)
    builder.add_task(module_name, "log", _logs)
    builder.add_task(module_name, "restart", _restart)

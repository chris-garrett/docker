import os
from __tasklib__ import TaskContext, TaskBuilder

mod = "compose"


def _prefix(ctx: TaskContext):
    compose_file = os.path.join(ctx.project_dir, "docker-compose.yml")
    return f"docker compose -f {compose_file} --profile all"


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


def _pull(ctx: TaskContext):
    ctx.exec(f"{_prefix(ctx)} pull")


def _log_service(ctx: TaskContext, service):
    ctx.exec(f"{_prefix(ctx)} logs {service} -f --tail 100")


def configure(builder: TaskBuilder):
    builder.add_task(mod, "ex:up", _up)
    builder.add_task(mod, "ex:down", _down)
    builder.add_task(mod, "ex:restart", _restart)
    builder.add_task(mod, "ex:log", _logs)
    builder.add_task(mod, "ex:pull", _pull)
    builder.add_task(mod, "ex:log:caddy", lambda ctx: _log_service(ctx, "caddy"))

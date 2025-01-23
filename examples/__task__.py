import json
import os
from __tasklib__ import TaskContext, TaskBuilder

mod = "compose"


def _prefix(ctx: TaskContext):
    # we are runnning at the root of the repo
    conf_file = "config.env"
    conf_arg = f"--env-file {conf_file}" if os.path.exists(conf_file) else ""
    env_file = ".env"
    env_arg = f"--env-file {env_file}" if os.path.exists(env_file) else ""
    compose_file = os.path.join("examples", "docker-compose.yml")
    service_profiles = os.getenv("SERVICE_PROFILES", "all")
    profiles0 = [f"--profile {svc.strip()}" for svc in service_profiles.split()]
    profiles = " ".join(profiles0)
    compose_file = os.path.join(ctx.project_dir, "docker-compose.yml")
    return f"""
        docker compose \
            -f {compose_file} \
            {conf_arg} \
            {env_arg} \
            {profiles}
        """


def _up(ctx: TaskContext):
    ctx.log.info("Starting docker-compose")
    return ctx.exec(f"{_prefix(ctx)} up -d")


def _down(ctx: TaskContext):
    ctx.log.info("Stopping docker-compose")
    ret = ctx.exec(f"{_prefix(ctx)} stop")
    if ret.returncode != 0:
        return ret
    return ctx.exec(f"{_prefix(ctx)} rm -f")


def _logs(ctx: TaskContext):
    ctx.log.info("Showing docker-compose logs")
    return ctx.exec(f"{_prefix(ctx)} logs -f --tail 100")


def _restart(ctx: TaskContext):
    _down(ctx)
    _up(ctx)


def _pull(ctx: TaskContext):
    return ctx.exec(f"{_prefix(ctx)} pull")


def _log_service(ctx: TaskContext, service):
    return ctx.exec(f"{_prefix(ctx)} logs {service} -f --tail 100")


def _nuke(ctx: TaskContext):
    ret = _down(ctx)
    if ret.returncode != 0:
        ctx.log.error(f"Failed to stop containers\nError was: {ret.stderr}")
        return ret

    # removes volumes so we can test from a clean state
    compose_file = os.path.join(ctx.project_dir, "docker-compose.yml")
    ret = ctx.exec(
        f"docker compose -f {compose_file} --profile '*' config --format json",
        capture=True,
    )
    if ret.returncode != 0:
        ctx.log.error(f"Failed to get config\nError was: {ret.stderr}")
        return ret

    config = json.loads(ret.stdout)
    project_name = config["name"]

    ret = ctx.exec("docker volume ls", capture=True)
    if ret.returncode != 0:
        ctx.log.error(f"Failed to get config\nError was: {ret.stderr}")
        return ret

    for row in ret.stdout.split("\n"):
        if project_name in row:
            volume = row.split()[1]
            ctx.exec(f"docker volume rm {volume}")


def configure(builder: TaskBuilder):
    builder.add_task(mod, "ex:up", _up)
    builder.add_task(mod, "ex:down", _down)
    builder.add_task(mod, "ex:restart", _restart)
    builder.add_task(mod, "ex:log", _logs)
    builder.add_task(mod, "ex:pull", _pull)
    builder.add_task(mod, "ex:log:caddy", lambda ctx: _log_service(ctx, "caddy"))
    builder.add_task(mod, "ex:nuke", _nuke)

import os
from string import Template

from __tasklib__ import TaskContext, load_env
from __version__ import VersionBuilder, VersionIncrement


class DockerBuilder:
    def __init__(self, ctx: TaskContext):
        self.ctx = ctx
        self.tags = []
        self.dockerfile = "Dockerfile"
        self.platforms = []
        self.push = False
        self.context_dir = "."
        self.repo = "ghcr.io"

    def with_file(self, file: str):
        self.dockerfile = file
        return self

    def add_tag(self, tag: str):
        self.tags.append(tag)
        return self

    def add_platform(self, platform: str):
        self.platforms.append(platform)
        return self

    def with_push(self, push: bool):
        self.push = push
        return self

    def with_repo(self, repo: bool):
        self.repo = repo
        return self

    def with_context(self, context: str):
        self.context_dir = context
        return self

    def build(self):
        cmd = f"docker buildx build -f {self.dockerfile}"

        platforms = " ".join([f"--platform {p}" for p in self.platforms])
        if len(platforms) > 0:
            cmd += f" {platforms}"

        tags = " ".join([f"-t {self.repo}/{t}" for t in self.tags])
        if len(tags) > 0:
            cmd += f" {tags}"

        if self.push:
            cmd += " --push"
        else:
            cmd += " --load"

        cmd += f" {self.context_dir}"

        return cmd


def get_version(ctx: TaskContext, service_name: str):
    ret = ctx.exec("git rev-parse --abbrev-ref HEAD", capture=True)
    return (
        VersionBuilder()
        .withIncrement(
            VersionIncrement.PATCH if ret.stdout == "main" else VersionIncrement.MINOR
        )
        .withTagPrefix(f"{service_name}/v")
        .build()
    )


def generate_service(ctx: TaskContext, name: str, custom_templates: dict = {}):
    try:
        env = {
            **load_env(os.path.join(ctx.root_dir, "config.env")),
        }

        base_templates = {
            "BUILD_TEMPLATE": f"Dockerfile.{name}.build",
            "FINAL_TEMPLATE": f"Dockerfile.{name}.final",
        }
        templates = {**custom_templates, **base_templates}

        for k, v in templates.items():
            with open(os.path.join(ctx.project_dir, v), "r") as f:
                env[k] = Template(f.read()).substitute(env)

        with open(os.path.join(ctx.project_dir, "Dockerfile.common"), "r") as f:
            common_content = f.read()

        final = Template(common_content).substitute(env)

        with open(os.path.join(ctx.project_dir, f"Dockerfile.{name}"), "w") as f:
            f.write(final)
    except Exception as e:
        ctx.log.error(f"Error generating service {name}: {e}")
        return 1
    return 0


def update_service(ctx: TaskContext, name: str, custom_templates: dict = {}):
    ret = generate_service(ctx, name, custom_templates)
    if ret != 0:
        return ret

    return 0


def pr_service(ctx: TaskContext, name: str, custom_templates: dict = {}):
    # check for local changes
    ret = ctx.exec("git status --porcelain", capture=True)
    if ret.returncode != 0:
        ctx.log.error(f"Error checking git status {ret.stderr}")
        return 1

    if f"Dockerfile.{name}" not in ret.stdout:
        ctx.log.info(f"No changes found for {name}")
        return 0

    ver = get_version(ctx, name)
    branch = f"{name}/{ver.semver_full}"

    # check if branch already exists on remote
    ret = ctx.exec(f"git branch -r -l origin/{branch}", capture=True)
    if ret.returncode != 0:
        ctx.log.error(f"Error checking git status {ret.stderr}")
        return 1
    if f"origin/{branch}" in ret.stdout:
        ctx.log.info(f"Branch {branch} already exists")
        return 0


def build_service(ctx: TaskContext, name: str):
    ctx.log.info(f"Building container for {name}")

    ver = get_version(ctx, name)
    tags = [f"{name}:latest", f"{name}:{ver.semver_full}"]

    b = DockerBuilder(ctx)
    b.with_repo(os.getenv("DOCKER_REGISTRY"))
    for tag in tags:
        b.add_tag(tag)
    if os.getenv("CI"):
        for p in os.getenv("TARGET_PLATFORMS").split(","):
            b.add_platform(p)
        b.with_push(True)
    b.with_file(os.path.join(ctx.project_dir, f"Dockerfile.{name}"))
    b.with_context(ctx.project_dir)
    return ctx.exec(b.build())


def tag_service(ctx: TaskContext, name: str):
    ver = get_version(ctx, name)
    ctx.log.info(f"Tagging container for {name} with {ver.tag}")
    env = {
        "GIT_AUTHOR_EMAIL": "cibot@users.noreply.github.com",
        "GIT_COMMITTER_EMAIL": "cibot@users.noreply.github.com",
        "GIT_AUTHOR_NAME": "CI Bot",
        "GIT_COMMITTER_NAME": "CI Bot",
    }
    ctx.exec(f'git tag -f -a {ver.tag} -m "{ver.tag}"', env=env)
    if os.getenv("CI"):
        ctx.exec(f"git push --force origin {ver.tag}")

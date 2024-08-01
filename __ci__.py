import base64
import time
import http.client
import json
import os
import urllib.parse
from string import Template

from __tasklib__ import TaskContext, load_env
from __version__ import VersionBuilder, VersionIncrement

git_env = {
    "GIT_AUTHOR_EMAIL": "cibot@users.noreply.github.com",
    "GIT_COMMITTER_EMAIL": "cibot@users.noreply.github.com",
    "GIT_AUTHOR_NAME": "CI Bot",
    "GIT_COMMITTER_NAME": "CI Bot",
}


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


def http_post(url: str, payload: dict, headers: dict):
    parsed_url = urllib.parse.urlparse(url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    path = parsed_url.path
    if parsed_url.query:
        path += "?" + parsed_url.query
    conn.request("POST", path, body=json.dumps(payload), headers=headers)
    res = conn.getresponse()
    return (res.status, res.reason, res.read())


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

    # create branch
    ret = ctx.exec(f"git checkout -b {branch}", capture=True)
    if ret.returncode != 0:
        ctx.log.error(f"Error creating branch {ret.stderr}")
        return 1

    ret = ctx.exec("git add -A")
    if ret.returncode != 0:
        ctx.log.error(f"Error adding files {ret.stderr}")
        return 1

    commit_msg = f"chore: {name} {ver.semver_full}"

    ret = ctx.exec(f'git commit -m "{commit_msg}"', env=git_env)
    if ret.returncode != 0:
        ctx.log.error(f"Error committing changes {ret.stderr}")
        return 1

    ret = ctx.exec(f"git push --set-upstream origin {branch}")
    if ret.returncode != 0:
        ctx.log.error(f"Error pushing branch {ret.stderr}")
        return 1

    time.sleep(20)

    token = f'{os.getenv("GITHUB_TOKEN")}'
    repo_url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}"

    # create PR
    ret = http_post(
        f"{repo_url}/pulls",
        {"title": commit_msg, "head": branch, "base": "main"},
        {
            "User-Agent": "CI Github Bot",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        },
    )
    if ret[0] != 201:
        ctx.log.error(f"Error creating PR {ret[0]} | {ret[1]} | {ret[2]}")
        return 1

    pull_number = json.loads(ret[2])["number"]

    # approve PR
    ret = http_post(
        f"{repo_url}/pulls/{pull_number}/reviews",
        {"body": "LGTM", "event": "APPROVE"},
        {
            "User-Agent": "CI Github Bot",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        },
    )
    if ret[0] != 201:
        ctx.log.error(f"Error creating PR {ret[0]} | {ret[1]} | {ret[2]}")
        return 1

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
    ctx.exec(f'git tag -f -a {ver.tag} -m "{ver.tag}"', env=git_env)
    if os.getenv("CI"):
        ctx.exec(f"git push --force origin {ver.tag}")

import re
import http.client
import json
import os
import time
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
        self.labels = []
        self.args = []

    def with_arg(self, name: str, value: str):
        self.args.append((name, value))
        return self

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

    def with_label(self, name: str, value: str):
        self.labels.append((name, value))
        return self

    def build(self):
        cmd = f"docker buildx build -f {self.dockerfile}"

        platforms = " ".join([f"--platform {p}" for p in self.platforms])
        if len(platforms) > 0:
            cmd += f" {platforms}"

        tags = " ".join([f"-t {t}" for t in self.tags])
        if len(tags) > 0:
            cmd += f" {tags}"

        labels = " ".join([f"-l {l[0]}={l[1]}" for l in self.labels])
        if len(labels) > 0:
            cmd += f" {labels}"

        args = " ".join([f"--build-arg {a[0]}={a[1]}" for a in self.args])
        if len(args) > 0:
            cmd += f" {args}"

        if self.push:
            cmd += " --push"
        else:
            cmd += " --load"

        cmd += f" {self.context_dir}"

        return cmd


def fetch(url: str, payload: dict, headers: dict, method="POST"):
    parsed_url = urllib.parse.urlparse(url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    path = parsed_url.path
    if parsed_url.query:
        path += "?" + parsed_url.query
    conn.request(method, path, body=json.dumps(payload), headers=headers)
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

        # get image used by FROM as final
        pattern = r"FROM\s+(\S+)\s+AS"

        # Search for the pattern in the input string
        match = re.search(pattern, final)
        if not match:
            ctx.log.error(f"Error parsing Dockerfile for final image {name}")
            return 1
        base_image = match.group(1)
        ret = ctx.exec("docker pull " + base_image)
        if ret.returncode != 0:
            ctx.log.error(f"Error pulling base image {base_image}")
            return ret.returncode
        ret = ctx.exec(
            "docker inspect --format='{{.RepoDigests}}' " + base_image, capture=True
        )
        if ret.returncode != 0:
            ctx.log.error(f"Error inspecting base image {base_image}")
            return ret.returncode
        digest = ret.stdout.strip("[]\n").split(",")[0].strip("'")
        print("digest", digest)

    except Exception as e:
        ctx.log.error(f"Error generating service {name}: {e}")
        return 1
    return 0


def update_hashes(
    ctx: TaskContext,
    name: str,
):
    try:
        with open(os.path.join(ctx.project_dir, f"Dockerfile.{name}"), "r") as f:
            final = f.read()

        # get image used by FROM as final
        pattern = r"FROM\s+(\S+)\s+AS"

        # Search for the pattern in the input string
        match = re.search(pattern, final)
        if not match:
            ctx.log.error(f"Error parsing Dockerfile for final image {name}")
            return 1
        base_image = match.group(1)
        ret = ctx.exec("docker pull " + base_image)
        if ret.returncode != 0:
            ctx.log.error(f"Error pulling base image {base_image}")
            return ret.returncode
        ret = ctx.exec(
            "docker inspect --format='{{.RepoDigests}}' " + base_image, capture=True
        )
        if ret.returncode != 0:
            ctx.log.error(f"Error inspecting base image {base_image}")
            return ret.returncode
        digest = ret.stdout.strip("[]\n").split(",")[0].strip("'")
        print("digest", digest)

        tag = f"{os.getenv("DOCKER_REGISTRY")}/{name}:latest"
        ret = ctx.exec(f"docker run --rm {tag} dpkg --list", capture=True)
        if ret.returncode != 0:
            ctx.log.error(f"Error getting package list {base_image}")
            return ret.returncode

        with open(os.path.join(ctx.project_dir, f"Dockerfile.{name}.hashes"), "w") as f:
            f.write(digest)
            f.write(ret.stdout)

    except Exception as e:
        ctx.log.error(f"Error generating service {name}: {e}")
        return 1
    return 0


def update_service(ctx: TaskContext, name: str, custom_templates: dict = {}):
    ret = generate_service(ctx, name, custom_templates)
    if ret != 0:
        return ret

    ret = build_service(ctx, name, skip_ci=True)
    if ret != 0:
        return ret

    ret = update_hashes(ctx, name)
    if ret != 0:
        return ret

    return 0


def pr_service(ctx: TaskContext, name: str):
    sleep_sec = 10
    token = f'{os.getenv("GITHUB_TOKEN")}'
    ci_token = f'{os.getenv("CI_GITHUB_TOKEN")}'
    repo_url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}"

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

    # create PR
    time.sleep(sleep_sec)

    ctx.log.info(f"Creating PR for {name}")
    ret = fetch(
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
    time.sleep(sleep_sec)

    ctx.log.info(f"Accepting PR for {name} PR {pull_number}")
    ret = fetch(
        f"{repo_url}/pulls/{pull_number}/reviews",
        {"body": "LGTM", "event": "APPROVE"},
        {
            "User-Agent": "CI Github Bot",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {ci_token}",
        },
    )
    if ret[0] != 200:
        ctx.log.error(f"Error accepting PR {ret[0]} | {ret[1]} | {ret[2]}")
        return 1

    # approve PR
    time.sleep(sleep_sec)

    ctx.log.info(f"Merging PR for {name} PR {pull_number}")
    ret = fetch(
        f"{repo_url}/pulls/{pull_number}/merge",
        {
            "commit_title": commit_msg,
            "merge_method": "squash",
        },
        {
            "User-Agent": "CI Github Bot",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        },
        method="PUT",
    )
    if ret[0] != 200:
        ctx.log.error(f"Error merging PR {ret[0]} | {ret[1]} | {ret[2]}")
        return 1

    return 0


def build_service(ctx: TaskContext, name: str, skip_ci=False):
    ctx.log.info(f"Building container for {name}")

    ver = get_version(ctx, name)
    tags = [
        f"{os.getenv("DOCKER_REGISTRY")}/{name}:latest",
        f"{os.getenv("DOCKER_REGISTRY")}/{name}:{ver.semver_full}",
    ]

    b = DockerBuilder(ctx)
    b.with_repo(os.getenv("DOCKER_REGISTRY"))
    for tag in tags:
        b.add_tag(tag)
    if not skip_ci and os.getenv("CI"):
        for p in os.getenv("TARGET_PLATFORMS").split(","):
            b.add_platform(p)
        b.with_push(True)
    b.with_file(os.path.join(ctx.project_dir, f"Dockerfile.{name}"))
    b.with_context(ctx.project_dir)

    b.with_label(
        "org.opencontainers.image.source", "https://github.com/chris-garrett/docker"
    )
    b.with_label("org.opencontainers.image.vendor", "NestEggs Inc.")
    b.with_label("org.opencontainers.image.version", ver.semver_full)
    b.with_label("org.opencontainers.image.created", ver.timestamp)
    b.with_label("org.opencontainers.image.branch", ver.branch)
    b.with_label("org.opencontainers.image.revision", ver.hash)

    config_env = load_env(os.path.join(ctx.root_dir, "config.env"))
    for k, v in config_env.items():
        if "_VERSION" in k:
            b.with_arg(k, v)

    return ctx.exec(b.build()).returncode


def tag_service(ctx: TaskContext, name: str):
    ver = get_version(ctx, name)
    ctx.log.info(f"Tagging container for {name} with {ver.tag}")

    ret = ctx.exec(f'git tag -f -a {ver.tag} -m "{ver.tag}"', env=git_env)
    if ret.returncode != 0:
        ctx.log.error(f"Error tagging {ver.tag} {ret.stderr}")
        return 1

    if os.getenv("CI"):
        ret = ctx.exec(f"git push --force origin {ver.tag}")
        if ret.returncode != 0:
            ctx.log.error(f"Error pushing tag {ver.tag} {ret.stderr}")
            return 1

    return 0

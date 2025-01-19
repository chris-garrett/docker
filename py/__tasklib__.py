################################################
# https://github.com/chris-garrett/python-task #
################################################
#
# Jul 30 2024
# * fix: regression in expanding variables
# * feat: added -q / --quiet option to disable logging. useful for capturing output.
# * feat: add support for key only task arguments. you can now:
#         `./task hello[big,world=yes]`
#
#         def _hello(ctx: TaskContext):
#             # ctx.args = {'big': None, 'world': 'yes'}
#             if "big" in ctx.args:
#                 ctx.log.info("Big is set")
#
# Jul 27 2024
# * chore: tease apart loading .env file from applying it to os.environ so that
#          tasks can consume .env files.
#          examples:
#              from __tasklib__ import load_env, load_dotenv
#              def some_task(ctx: TaskContext):
#                  env_dict = load_env(".env")
#                  load_dotenv(".env")
#
# * fix:   use int or CompeltedProcess.returncode from tasks to set the exit code.
#          examples:
#              def some_task(ctx: TaskContext):
#                  return ctx.exec("ls")
#              def some_task(ctx: TaskContext):
#                  return 0
#
#
# May 11 2024
# * feat: added support for task arguments. you can now:
#         `./task hello[arg1=value1,arg2=2.0]`
#
#         in your task you can access the args via ctx.args
#
#         def _hello(ctx: TaskContext):
#             ctx.log.info(f"Args: {ctx.args}")
#
# Apr 20 2024
# * chore: support single file task projects
#   * moved __task__.py to __tasklib__.py
#   * no longer filter __task__.py at root
#
# Mar 04 2024
# * chore: update to Python 3.9
# * chore: add tests for load_dotenv
# * feat: add environment variable expansion to load_dotenv
#
# Dec 16 2023
# * fix/feat: fix bug in load_dotenv where keys were not trimmed and white space not leading to a match, add
#             override to match python-dotenv behavior.
#
# Dec 05 2023
# * fix: add exception handling to exec() calls. normalize returned object.
#
# Dec 03 2023
# * added quiet option to exec(). This will capture stdout and stderr and will be available
#   in the CompletedProcess object.
#   example:
#    (args=['pwd'], returncode=0, stdout='/home/chris\n', stderr='') = ctx.exec("pwd", quiet=True)
# * log level can be specified via LOG_LEVEL env var. see ./task. Valid values are: TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL. # noqa
#
# Dec 02 2023
# * add support for task dependencies
#
# Nov 13 2023
# * initial cut of a task runner
#
# TODO
# * add the abililty to call depenencies with arguments.
# * add support for file depenencies. see go-task for inspiration: https://taskfile.dev/usage/#prevent-unnecessary-work

import argparse
import glob
import importlib.machinery
import inspect
import logging
import os
import platform
import shlex
import subprocess
import sys
import typing
from dataclasses import dataclass, field
from logging import Logger
from subprocess import CompletedProcess
from typing import Any, Callable, Dict, List, NamedTuple, Protocol, runtime_checkable


def load_env(filename=".env", expand_vars=True):
    """
    Loads dictionary from a .env file and returns the dictionary.

    Args:
    - filename (str, optional): The name of the .env file to load. Defaults to ".env".
    - override (bool, optional): If True, existing environment variables will be overwritten
      by those in the .env file. Defaults to False.

    Returns:
    dict
    """
    env = {}

    if not os.path.exists(filename):
        return env

    with open(filename) as f:
        for line in f:
            line = line.strip()

            # skip comments and empty lines
            if line.startswith("#") or "=" not in line:
                continue

            k, v = line.split("=", 1)
            k = k.strip()

            # dont set null values
            if v is not None:
                env[k] = v.strip()

    if expand_vars:
        # expand any env vars
        for k, v in env.items():
            if v.startswith("$"):
                env[k] = os.path.expandvars(v)

    return env


def load_dotenv(filename=".env", override=False, expand_vars=True):
    """
    Load environment variables from a .env file into the os.environ dictionary.

    Args:
    - filename (str, optional): The name of the .env file to load. Defaults to ".env".
    - override (bool, optional): If True, existing environment variables will be overwritten
      by those in the .env file. Defaults to False.

    Returns:
    None
    """
    for (
        k,
        v,
    ) in load_env(filename, expand_vars).items():
        if k in os.environ and not override:
            continue
        os.environ[k] = v


def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kws)


TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")
logging.Logger.trace = trace

QUIET_LEVEL = 999
logging.addLevelName(QUIET_LEVEL, "QUIET")

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("task")


@runtime_checkable
class ExecProtocol(Protocol):
    def exec(self, cmd: str, quiet: bool = False) -> int:
        raise NotImplementedError


class SystemContext(NamedTuple):
    platform: str  # Linux, Darwin, Windows
    arch: str  # x86_64, arm64
    distro: str  # Debian, Arch, RHEL


def exec(
    cmd: str,
    cwd: str = None,
    logger: Logger = None,
    venv_dir: str = None,
    capture: bool = False,
    input: str = None,
    env: Dict[str, str] = None,
) -> CompletedProcess[str]:
    args = [arg.strip() for arg in shlex.split(cmd.strip())]
    if isinstance(logger, Logger) and not capture:
        if cwd:
            logger.debug("Executing: [%s] Cwd: [%s]", " ".join(args), cwd)
        else:
            logger.debug("Executing: [%s]", " ".join(args))

    try:
        if env:
            env = {**os.environ.copy(), **env}

        return subprocess.run(
            args,
            check=False,
            text=True,
            cwd=cwd,
            capture_output=capture,
            input=input,
            env=env,
        )
    except Exception as ex:
        if isinstance(logger, Logger):
            logger.exception("Error executing: [%s]", " ".join(args))
        return CompletedProcess(args=args, returncode=1, stdout="", stderr=str(ex))


@dataclass
class TaskContext(ExecProtocol):
    root_dir: str
    project_dir: str
    log: Logger
    system: SystemContext
    args: Dict[str, Any] = field(default_factory=dict)

    def exec(
        self,
        cmd: str,
        cwd: str = None,
        venv_dir: str = None,
        capture: bool = False,
        input: str = None,
        env: Dict[str, str] = None,
    ) -> CompletedProcess[str]:
        return exec(cmd, cwd, self.log, venv_dir, capture, input, env)


class TaskFileDefinition(NamedTuple):
    func: Callable[[TaskContext], None]  # configure func
    filename: str
    dir: str


class TaskDefinition(NamedTuple):
    func: Callable[[TaskContext], None]  # task func
    module: str
    name: str
    filename: str
    dir: str
    deps: List[str] = []


class TaskBuilder(object):
    def __init__(self):
        self.parsers = []
        self.python_exe = "python"

    def use_python(self, python_exe):
        self.python_exe = python_exe

    def add_task(
        self, module: str, name: str, func: callable, deps: List[str] = []
    ) -> None:
        """
        Add a task to the list of parsers.

        Args:
        - module (str): The name of the module containing the task.
        - name (str): The name of the task.
        - func (callable): The function that implements the task.
        - deps (list[str]): A list of task names that this task depends on.
        """
        if not isinstance(deps, list):
            raise TypeError(f"deps must be a list, got {type(deps)}")
        self.parsers.append((module, name, func, deps))


def _ensure_venv(ctx: TaskContext):
    if not os.path.exists(ctx.venv_dir):
        ctx.log.info(f"Creating venv {ctx.venv_dir}")
        ctx.exec([ctx.python_exe, "-m", "venv", ctx.venv_dir])


def _load_tasks(task: TaskFileDefinition) -> typing.Dict[str, TaskDefinition]:
    """
    Builds a list of N tasks based on what was specified in configure().
    """
    tasks: typing.Dict[str, TaskDefinition] = {}
    builder = TaskBuilder()
    task.func(builder)
    for module, name, func, deps in builder.parsers:
        tasks[name] = TaskDefinition(
            module=module,
            name=name,
            func=func,
            dir=task.dir,
            filename=task.filename,
            deps=deps,
        )
    return tasks


def _load_task_definitions(task_files) -> List[TaskFileDefinition]:
    """
    Loads tasks files if they match the required signature.
    """
    tasks: List[TaskFileDefinition] = []

    for idx, task_file in enumerate(task_files):
        loader = importlib.machinery.SourceFileLoader(f"task{idx}", task_file)
        module = loader.load_module()
        if not hasattr(module, "configure"):
            logger.trace(
                f"load task definition: {task_file}: no configure() found, skipping {task_file}"
            )
            continue

        func = getattr(module, "configure")
        parameters = inspect.signature(func).parameters
        if "builder" not in parameters:
            logger.trace(
                f"load task definition: {task_file}: no configure(builder) found, skipping {task_file}"
            )
            continue

        logger.trace(f"load task definition: {task_file}: loaded successfully")
        tasks.append(
            TaskFileDefinition(
                func=func,
                filename=task_file,
                dir=os.path.abspath(os.path.dirname(task_file)),
            )
        )

    return tasks


def _find_task_files() -> List[str]:
    """
    Finds files that match naming convention
    """
    return [f for f in glob.glob("**/__task__.py", recursive=True) if os.path.isfile(f)]


def _build_system_distro(content: str) -> str:
    """
    Returns distro for os-release contents
    """

    id = ""
    id_like = None
    for line in content.split():
        if line.startswith("ID_LIKE="):
            id_like = line.split("=")[1].strip()
        if line.startswith("ID="):
            id = line.split("=")[1].strip()
    return id_like if id_like else id


def _build_system_context() -> SystemContext:
    """
    Builds a context object for the system.
    """

    distro = ""
    if platform.system() == "Linux" and os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            distro = _build_system_distro(f.read())

    return SystemContext(
        platform=platform.system().lower(),
        arch=platform.machine().lower(),
        distro=distro.lower(),
    )


def _build_task_context(task: TaskDefinition) -> TaskContext:
    """
    Builds a context object for a task.
    """
    return TaskContext(
        root_dir=os.path.abspath(os.curdir),
        project_dir=task.dir,
        log=logging.getLogger(task.module),
        system=_build_system_context(),
    )


def _print_help(available_tasks: List[str]):
    # do a lazy sort to put tasks with no colons first
    formatted_tasks = "".join(
        [
            f"  {t}\n"
            for t in sorted(
                available_tasks, key=lambda x: (0 if x.count(":") == 0 else 1, x)
            )
        ]
    )
    print(
        f"""usage: task [-h] [task ...]

arguments:
{formatted_tasks}

options:
  -h, --help  show this help message and exit
  -v, --verbose  enabled debug logging
"""
    )


def _resolve_deps(tasks_to_resolve, tasks):
    # Convert list of tasks to a dictionary for easy access
    task_dict = {list(task.keys())[0]: list(task.values())[0] for task in tasks}

    resolved = []  # List to store the resolved order of tasks
    visited = (
        set()
    )  # Set to keep track of visited tasks to detect circular dependencies

    def dfs(task):
        if task in resolved:  # If already resolved, no need to proceed
            return
        if task in visited:  # Circular dependency detected
            raise ValueError("Circular dependency detected")
        visited.add(task)

        # Resolve dependencies first
        for dep in task_dict.get(task, {}).get("deps", []):
            if dep not in resolved:
                dfs(dep)

        # Remove from visited as we are done with this task
        visited.remove(task)
        resolved.append(task)  # Add to resolved list

    for task in tasks_to_resolve:
        if task not in resolved:
            dfs(task)

    return resolved


def _parse_task_args(task_args: str) -> Dict[str, Any]:
    """
    Parse task arguments from a string in the format name[arg1=val1,arg2=val2,...].

    Args:
    - task_args (str): The string containing the task arguments.

    Returns:
    A dictionary of argument names and values.
    """
    args = {}
    args_str = task_args[task_args.find("[") + 1 : task_args.rfind("]")]
    for arg in args_str.split(","):
        if len(arg) > 0:
            if "=" in arg:
                key, value = arg.split("=")
                args[key.strip()] = value.strip()
            else:
                args[arg.strip()] = None

    return args


def _process_tasks():
    # need to boostrap this arg so that we can enable debug logging at
    # configure time
    raw_args = sys.argv[1:]
    if "-v" in raw_args or "--verbose" in raw_args:
        logger.setLevel(logging.DEBUG)

    if "-q" in raw_args or "--quiet" in raw_args:
        logger.setLevel(QUIET_LEVEL)

    logger.info("Processing tasks")

    task_files = _find_task_files()
    task_defs = _load_task_definitions(task_files)
    # { 'task_name': TaskDefinition }
    tasks: typing.Dict[str, TaskDefinition] = {}

    parser = argparse.ArgumentParser(description="task", add_help=False)
    parser.add_argument("tasks", nargs="*")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")

    # configure tasks
    for task_def in task_defs:
        tasks.update(_load_tasks(task_def))

    args = parser.parse_args()

    # Split tasks and their arguments
    tasks_with_args = {}
    for task_arg in args.tasks:
        if "[" in task_arg and "]" in task_arg:
            task_name, task_args = task_arg.split("[", 1)
            task_args = "[" + task_args
            tasks_with_args[task_name] = _parse_task_args(task_args)
        else:
            tasks_with_args[task_arg] = {}

    task_names = list(tasks_with_args.keys())

    if len(task_names) == 0 or args.help:
        _print_help(tasks.keys())
        return

    # validate tasks
    for task_name in task_names:
        if task_name not in tasks:
            logger.error("Unknown task: %s", task_name)
            _print_help(tasks.keys())
            return

    # build a list of tasks and dependencies to pass to the resolver
    # result should be:
    # [
    #   {
    #       "task_name": {
    #           "deps": ["dep1", "dep2"]
    #       }
    #   },
    # ]
    tasks_with_deps = [{k: {"deps": v.deps}} for k, v in tasks.items()]
    resolved_tasks = _resolve_deps(task_names, tasks_with_deps)

    # runtime
    ret_code = 0
    for task_name in resolved_tasks:
        if task_name in tasks:
            task = tasks[task_name]
            try:
                task_context = _build_task_context(task)
                task_context.args = tasks_with_args.get(task_name, {})
                ret = task.func(task_context)
                if isinstance(ret, CompletedProcess):
                    ret_code = ret.returncode
                elif isinstance(ret, int):
                    ret_code = ret
            except KeyboardInterrupt:
                pass
    sys.exit(ret_code)


if __name__ == "__main__":
    env_files = [
        {"file": ".env.defaults", "override": False},
        {"file": ".env.secrets", "override": False},
        {"file": ".env.user", "override": True},
        {"file": ".env.local", "override": True},
        {"file": ".env", "override": True},
    ]

    for env in env_files:
        load_dotenv(
            os.path.abspath(os.path.join(os.path.dirname(__file__), env["file"])),
            env["override"],
        )

    _process_tasks()

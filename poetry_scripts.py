import subprocess


def run_cmd(cmd: str, cwd: str = None) -> None:
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def run_pre_commit_in_submodules() -> None:
    # 获取所有子模块路径
    cmd = "git config --file .gitmodules --get-regexp path | awk '{ print $2 }'"
    result = subprocess.run(
        cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True
    )
    submodules = result.stdout.strip().split("\n")

    for submodule in submodules:
        print(f"Running pre-commit in {submodule}")
        # 进入子模块目录并执行pre-commit
        run_cmd("poetry run pre-commit run --all-files", cwd=submodule)


def run_tests() -> None:
    # Install requirements by poetry
    run_cmd("poetry install")

    # Run pre-commit tests in the main repository
    # run_cmd("poetry run pre-commit run --all-files")

    # Optionally run pre-commit in all submodules
    run_pre_commit_in_submodules()

    # Generate coverage report
    # run_cmd("poetry run pytest --cov=./ --cov-report=xml --cov-report=html -vv")


if __name__ == "__main__":
    run_tests()

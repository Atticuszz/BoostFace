import subprocess
from pathlib import Path


def run_cmd(cmd: str, cwd: str = None) -> None:
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' in {cwd} failed with exit status {e.returncode}")


def get_submodule_paths() -> list[str]:
    cmd = "git config --file .gitmodules --get-regexp path"
    result = subprocess.run(
        cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True
    )
    paths = [
        line.split()[-1]
        for line in result.stdout.split("\n")
        if line and Path(line).exists()
    ]
    return paths


def run_pre_commit_in_submodules() -> None:
    submodules = get_submodule_paths()
    for path in submodules:
        print(f"Running pre-commit in {path}")
        run_cmd("pre-commit run --all-files", cwd=path)


def run_tests() -> None:
    # Install requirements by poetry
    run_cmd("poetry install")
    # Run pre-commit
    # run_cmd("poetry run pre-commit autoupdate")
    # run_cmd("poetry run pre-commit clean")
    # run_cmd("poetry run pre-commit install")

    # Optionally run pre-commit in all submodules
    run_pre_commit_in_submodules()

    # Run pre-commit tests in the main repository
    run_cmd("poetry run pre-commit run --all-files")

    # Generate coverage report
    # run_cmd("poetry run pytest --cov=./ --cov-report=xml --cov-report=html -vv")


if __name__ == "__main__":
    run_tests()

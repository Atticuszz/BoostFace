"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 16/12/2023
@Description  :
"""
import subprocess


def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)


def run_tests():
    # Install requirements
    # run_cmd("poetry install")

    # Run pre-commit tests
    # run_cmd("poetry run pre-commit run --all-files")

    # Generate coverage report
    run_cmd("pytest tests")


if __name__ == '__main__':
    run_tests()

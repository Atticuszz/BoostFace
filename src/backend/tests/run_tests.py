import subprocess
from pathlib import Path


def run_pytest(test_dir: Path = Path(__file__).parent):
    assert test_dir.is_dir(), f"{test_dir} is not a directory"

    # 查找所有以 'test_' 开头的 Python 文件
    test_files = test_dir.rglob('test_*.py')

    for file_path in test_files:
        print(f"Running tests in {file_path}")
        with subprocess.Popen(["pytest", str(file_path)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              encoding='utf-8') as proc:
            for line in proc.stdout:
                print(line, end='')


if __name__ == "__main__":
    run_pytest()

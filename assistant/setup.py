import os
import subprocess
import sys


def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def upgrade_pip():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])


def install_pipreqs():
    try:
        import pipreqs
    except ImportError:
        install_package("pipreqs")


def generate_requirements():
    subprocess.check_call(["pipreqs", "."])


def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--force"])


def main():
    upgrade_pip()
    install_pipreqs()
    generate_requirements()
    install_requirements()


if __name__ == "__main__":
    main()

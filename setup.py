#!/usr/bin/env python
# Copyright (c) Facebook, Inc. and its affiliates.
import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from setuptools import find_packages, setup

ROOT_DIR = Path(__file__).parent.resolve()


def _get_version(nightly=False, release=False):
    version = "0.3.0a0"
    sha = "Unknown"
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT_DIR)).decode("ascii").strip()
    except Exception:
        pass

    if nightly:
        version = version[:-2] + "dev" + f"{datetime.utcnow():%Y%m%d}"
    elif release:
        version = version[:-2]
    else:
        os_build_version = os.getenv("BUILD_VERSION")
        if os_build_version:
            version = os_build_version
        elif sha != "Unknown":
            version += "+" + sha[:7]

    return version, sha


def _export_version(version, sha):
    version_path = ROOT_DIR / "torchdata" / "version.py"
    with open(version_path, "w") as f:
        f.write(f"__version__ = '{version}'\n")
        f.write(f"git_version = {repr(sha)}\n")


def get_parser():
    parser = argparse.ArgumentParser(description="TorchData setup")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--nightly",
        action="store_true",
        help="Nightly Release",
    )
    group.add_argument(
        "--release",
        action="store_true",
        help="Official/RC Release",
    )
    return parser


if __name__ == "__main__":
    args, unknown = get_parser().parse_known_args()

    VERSION, SHA = _get_version(args.nightly, args.release)
    _export_version(VERSION, SHA)

    print("-- Building version " + VERSION)

    pytorch_package_version = os.getenv("PYTORCH_VERSION")

    pytorch_package_dep = "torch"
    if pytorch_package_version:
        pytorch_package_dep += "==" + pytorch_package_version

    sys.argv = [sys.argv[0]] + unknown
    setup(
        # Metadata
        name="torchdata",
        version=VERSION,
        description="Composable data loading modules for PyTorch",
        url="https://github.com/pytorch/data",
        author="PyTorch Team",
        author_email="packages@pytorch.org",
        license="BSD",
        install_requires=["requests", pytorch_package_dep],
        python_requires=">=3.7",
        classifiers=[
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
        ],
        # Package Info
        packages=find_packages(exclude=["test*", "examples*"]),
        zip_safe=False,
    )
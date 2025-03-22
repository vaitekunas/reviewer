__all__ = ["prepare_workdir"]

import os


def prepare_workdir(root: str) -> None:
    os.makedirs(root, exist_ok = True)

    for folder in ["workflows", "analysis", "results", "datasets"]:
        os.makedirs(f"{root}/{folder}", exist_ok = True)


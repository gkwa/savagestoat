import logging
import os
import pathlib
import subprocess
import sys

logger = logging.getLogger(__name__)

_LIST_FILE = "/tmp/savagestoat-rsync-list.txt"


def rsync_to_staging(paths: list[str], staging: str) -> None:
    os.makedirs(staging, exist_ok=True)
    with open(_LIST_FILE, "w") as f:
        for p in paths:
            f.write(p.lstrip("/") + "\n")
    logger.info("rsyncing %d files to staging %s", len(paths), staging)
    result = subprocess.run(
        ["rsync", "--archive", "--files-from", _LIST_FILE, "/", staging + "/"],
    )
    if result.returncode != 0:
        logger.error("rsync to staging failed with exit code %d", result.returncode)
        sys.exit(result.returncode)


def rsync_to_dest(staging: str, dest: str) -> None:
    logger.info("rsyncing from staging to %s", dest)
    result = subprocess.run(
        ["rsync", "--archive", staging + "/", dest + "/"],
    )
    if result.returncode != 0:
        logger.error("rsync to dest failed with exit code %d", result.returncode)
        sys.exit(result.returncode)


def clear_dest_files(dest: str) -> None:
    logger.info("clearing files in %s", dest)
    result = subprocess.run(["find", dest, "-type", "f", "-delete"])
    if result.returncode != 0:
        logger.error("clearing dest failed with exit code %d", result.returncode)
        sys.exit(result.returncode)


def remove_staging(staging: str) -> None:
    logger.info("removing staging directory %s", staging)
    result = subprocess.run(["rm", "-rf", staging])
    if result.returncode != 0:
        logger.error("removing staging failed with exit code %d", result.returncode)
        sys.exit(result.returncode)


def file_count(dest: str) -> int:
    result = subprocess.run(
        ["find", dest, "-type", "f"],
        capture_output=True,
        text=True,
    )
    return len(result.stdout.splitlines())


def disk_usage(dest: str) -> str:
    result = subprocess.run(["du", "-sh", dest], capture_output=True, text=True)
    return result.stdout.split()[0] if result.stdout else "unknown"


def expand(path: str) -> str:
    return str(pathlib.Path(path).expanduser())

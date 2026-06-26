import datetime
import logging
import os
import pathlib
import random

from savagestoat import packs

logger = logging.getLogger(__name__)

_RANGE_START = datetime.datetime(1950, 1, 1, tzinfo=datetime.timezone.utc)
_RANGE_END = datetime.datetime(1959, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
_RANGE_SECONDS = int((_RANGE_END - _RANGE_START).total_seconds())


def _random_timestamp() -> float:
    return (_RANGE_START + datetime.timedelta(seconds=random.randint(0, _RANGE_SECONDS))).timestamp()


def _collect_by_dir(root: pathlib.Path) -> dict[pathlib.Path, list[pathlib.Path]]:
    dir_files: dict[pathlib.Path, list[pathlib.Path]] = {}
    for path in root.rglob("*"):
        if path.is_file() and packs.is_media(str(path)):
            dir_files.setdefault(path.parent, []).append(path)
    return dir_files


def randomize_timestamps(root: pathlib.Path) -> None:
    dir_files = _collect_by_dir(root)
    pack_count = 0
    standalone_count = 0
    for file_list in dir_files.values():
        if packs.MIN_PACK <= len(file_list) <= packs.MAX_PACK:
            ts = _random_timestamp()
            for path in file_list:
                os.utime(path, (ts, ts))
            pack_count += 1
        else:
            for path in file_list:
                ts = _random_timestamp()
                os.utime(path, (ts, ts))
                standalone_count += 1
    logger.info("timestamped %d packs, %d standalone files", pack_count, standalone_count)

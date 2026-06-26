import logging
import pathlib
import random

logger = logging.getLogger(__name__)

DEFAULT_MIN_PACK = 1
DEFAULT_MAX_PACK = 20

MEDIA_EXTS = {
    "jpg", "jpeg", "png", "gif", "webp", "heic", "tiff", "bmp",
    "mp4", "mov", "avi", "mkv", "m4v", "wmv", "flv", "webm",
    "mp3", "flac", "wav", "aac", "ogg", "m4a",
}


def parse_size(size_str: str) -> int:
    s = size_str.upper().strip()
    units = {"TB": 1024**4, "GB": 1024**3, "MB": 1024**2, "KB": 1024, "B": 1}
    for suffix, multiplier in units.items():
        if s.endswith(suffix):
            return int(float(s[: -len(suffix)]) * multiplier)
    return int(s)


def is_media(path: str) -> bool:
    p = pathlib.Path(path)
    if p.stem.endswith("_thumb"):
        return False
    return p.suffix.lstrip(".").lower() in MEDIA_EXTS


def build_collection(
    files: list[tuple[str, int]],
    min_pack: int = DEFAULT_MIN_PACK,
    max_pack: int = DEFAULT_MAX_PACK,
) -> list[list[tuple[str, int]]]:
    dir_files: dict[str, list[tuple[str, int]]] = {}
    for path, size in files:
        if not is_media(path):
            continue
        parent = str(pathlib.Path(path).parent)
        dir_files.setdefault(parent, []).append((path, size))

    packs: list[list[tuple[str, int]]] = []
    standalones: list[tuple[str, int]] = []

    for file_list in dir_files.values():
        if min_pack <= len(file_list) <= max_pack:
            packs.append(sorted(file_list, key=lambda x: pathlib.Path(x[0]).name.lower()))
        else:
            standalones.extend(file_list)

    items: list[list[tuple[str, int]]] = packs + [[f] for f in standalones]
    random.shuffle(items)
    logger.info(
        "collection: %d items (%d packs, %d standalones)",
        len(items),
        len(packs),
        len(standalones),
    )
    return items


def select_up_to_limit(
    collection: list[list[tuple[str, int]]], max_bytes: int
) -> list[str]:
    total = 0
    selected: list[str] = []
    for item in collection:
        item_size = sum(size for _, size in item if size)
        if total + item_size <= max_bytes:
            total += item_size
            selected.extend(path for path, _ in item)
    logger.info("selected %d files (%.2f GB)", len(selected), total / 1024**3)
    return selected

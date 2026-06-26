import argparse
import logging
import sys

import savagestoat.db as db
import savagestoat.packs as packs
import savagestoat.rsync as rsync
import savagestoat.timestamps as timestamps
import pathlib

logger = logging.getLogger(__name__)

_STAGING = "/tmp/savagestoat-staging"
_DEFAULT_DB = "~/Pictures/digikam4.db"
_DEFAULT_DEST = "~/Documents/jack"


def _setup_logging(verbosity: int) -> None:
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(verbosity, len(levels) - 1)]
    logging.basicConfig(level=level, stream=sys.stderr, format="%(levelname)s %(message)s")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy DigiKam-tagged media to a destination using the media pack shuffle spec.",
    )
    parser.add_argument(
        "--tag",
        dest="tags",
        action="append",
        required=True,
        metavar="TAG",
        help="DigiKam tag name to include (repeatable)",
    )
    parser.add_argument(
        "--size",
        required=True,
        metavar="SIZE",
        help="maximum total size to copy, e.g. 5GB or 500MB",
    )
    parser.add_argument(
        "--dest",
        default=_DEFAULT_DEST,
        metavar="DIR",
        help=f"destination directory (default: {_DEFAULT_DEST})",
    )
    parser.add_argument(
        "--db",
        default=_DEFAULT_DB,
        metavar="PATH",
        help=f"DigiKam SQLite database path (default: {_DEFAULT_DB})",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="skip clearing destination files before copying",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increase log verbosity (-v INFO, -vv DEBUG)",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _setup_logging(args.verbose)

    db_path = rsync.expand(args.db)
    dest = rsync.expand(args.dest)
    max_bytes = packs.parse_size(args.size)

    logger.info("resolving tags: %s", args.tags)
    tag_map = db.resolve_tag_ids(db_path, args.tags)
    if not tag_map:
        logger.error("no matching tags found in database")
        sys.exit(1)

    tag_ids = list(tag_map.values())
    files = db.get_tagged_files(db_path, tag_ids)

    collection = packs.build_collection(files)
    selected = packs.select_up_to_limit(collection, max_bytes)
    if not selected:
        logger.error("no files selected")
        sys.exit(1)

    rsync.remove_staging(_STAGING)
    rsync.rsync_to_staging(selected, _STAGING)
    timestamps.randomize_timestamps(pathlib.Path(_STAGING))

    if not args.no_clean:
        rsync.clear_dest_files(dest)

    rsync.rsync_to_dest(_STAGING, dest)
    rsync.remove_staging(_STAGING)

    count = rsync.file_count(dest)
    size = rsync.disk_usage(dest)
    logger.warning("done: %d files, %s in %s", count, size, dest)

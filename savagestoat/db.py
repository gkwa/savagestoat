import logging
import sqlite3

logger = logging.getLogger(__name__)

_QUERY = """
SELECT DISTINCT ar.specificPath || a.relativePath || '/' || i.name,
       COALESCE(i.fileSize, 0)
FROM ImageTags it
JOIN Images i ON i.id = it.imageid
JOIN Albums a ON a.id = i.album
JOIN AlbumRoots ar ON ar.id = a.albumRoot
WHERE it.tagid IN ({placeholders})
  AND i.status != 4
  AND i.album IS NOT NULL
ORDER BY 1
"""


def resolve_tag_ids(db_path: str, tag_names: list[str]) -> dict[str, int]:
    placeholders = ",".join("?" * len(tag_names))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT name, id FROM Tags WHERE name IN ({placeholders})",
        tag_names,
    )
    result = dict(cursor.fetchall())
    conn.close()
    missing = set(tag_names) - set(result)
    if missing:
        logger.warning("tags not found in database: %s", sorted(missing))
    logger.info("resolved tags: %s", result)
    return result


def get_tagged_files(db_path: str, tag_ids: list[int]) -> list[tuple[str, int]]:
    placeholders = ",".join("?" * len(tag_ids))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(_QUERY.format(placeholders=placeholders), tag_ids)
    rows = cursor.fetchall()
    conn.close()
    logger.info("found %d tagged files", len(rows))
    return rows

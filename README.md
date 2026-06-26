# savagestoat

Copies DigiKam-tagged media to a destination directory using the media pack shuffle spec.

Files are staged outside the Syncthing watch path, timestamped to a random date in the 1950s, then moved into the destination in one pass so Syncthing sees each file exactly once with its final timestamp already set.

## Install

```sh
uv tool install git+https://github.com/gkwa/savagestoat
```

Or run without installing:

```sh
uv run --project /path/to/savagestoat savagestoat --help
```

## Usage

```sh
# copy files tagged with a single tag (5GB limit, destination defaults to ~/Documents/jack)
savagestoat --tag portrait --size 5GB

# multiple tags
savagestoat --tag portrait --tag landscape --size 10GB

# custom destination
savagestoat --tag portrait --size 5GB --dest ~/Desktop/gallery

# skip clearing destination before copying
savagestoat --tag portrait --size 5GB --no-clean

# custom DigiKam database path
savagestoat --tag portrait --size 5GB --db ~/Pictures/other.db

# verbose output (INFO level)
savagestoat --tag portrait --size 5GB -v

# debug output
savagestoat --tag portrait --size 5GB -vv

# adjust media pack size bounds (default: min 1, max 20)
savagestoat --tag portrait --size 5GB --min-pack-size 2 --max-pack-size 10

# combine multiple tags with a large size limit and debug logging
savagestoat --tag portrait --tag landscape --tag nature --size 20GB -vv
```

## Media pack definition

A directory qualifies as a media pack when it contains between `--min-pack-size` and `--max-pack-size` media files directly inside it.

Directories with more than `--max-pack-size` media files are not packs — their files are treated as standalones.

Within a pack, files are kept together as an indivisible block and sorted lexicographically by filename.

Packs and standalones are shuffled together into a random order before selection.

## Staging

Files are rsynced to `/tmp/savagestoat-staging`, timestamped there, then rsynced into the destination.

The staging directory is always removed after the run completes.

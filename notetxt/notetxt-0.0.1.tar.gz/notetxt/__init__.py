import os
import re
import glob
from pathlib import Path
from collections import defaultdict


TITLE_REGEX = "^([A-Za-z0-9 -_:]+)\n(?:-|=)+\n"


class Note:
    def __init__(self, title: str, path: Path, dir: Path) -> None:
        self.__tags = set()  # type: set
        self.__tags_added = set()  # type: set
        self.__tags_removed = set()  # type: set

        self.title = title
        self.path = path
        self.dir = dir

    @property
    def tags(self) -> set:
        return self.__tags

    def add_tag(self, tag):
        self.__tags_added.add(tag)
        self.__tags.add(tag)

    def remove_tag(self, tag):
        self.__tags_removed.add(tag)
        self.__tags.remove(tag)

    def add_tag_from_link(self, linkpath):
        commonprefix = os.path.commonprefix([linkpath, self.path])
        tag = re.sub(f"^{commonprefix}", '', linkpath)
        self.__tags.add(os.path.dirname(tag))

    def __repr__(self) -> str:
        return f"Note(title='{self.title}', path='{self.path}', " \
               f"tags={self.tags})"

    def save_tags(self):
        filename = os.path.basename(self.path)
        for tag in self.__tags_added:
            path = Path(f"{self.dir}/{tag}/{filename}")
            if not path.exists():
                # This is the closest to mkdir -p as we could make it
                try:
                    os.makedirs(f"{self.dir}/{tag}")
                except:
                    pass
            relpath = os.path.relpath(str(self.path),
                                      str(self.dir.resolve()))

            # count the dept of a tag (the number of directories it is inside
            # the current directory) and then update the link accordingly
            depth = relpath.count('/') + 1
            path.symlink_to(f"{'../' * depth}{relpath}")

        for tag in self.__tags_removed:
            path = Path(f"{self.dir}/{tag}/{filename}")
            os.unlink(str(path))

        # reset tags sets
        self.__tags_added = set()
        self.__tags_removed = set()

    def save(self):
        if not self.path.exists():
            content = f"{self.title}\n{len(self.title) * '='}\n"
            with open(str(self.path), 'w') as f:
                f.write(content)
        self.save_tags()


def note_from_path(path: Path, dir: Path) -> Note:
    contents = path.read_text(errors='ignore')
    # check first 512 bytes of a file
    match = re.match(TITLE_REGEX, contents[:512], flags=re.MULTILINE)
    if match:
        title = match.group(1)
        return Note(title, path, dir)

    return None


def load_from_dir(directory: str) -> list:
    glob_str = f"{directory}/**/*.*"
    path_map = defaultdict(set)
    notes = {}

    for filepath in glob.iglob(glob_str, recursive=True):
        path = Path(os.path.abspath(filepath))
        if path.is_symlink() and path.resolve().exists():
            path_map[str(path.resolve())].add(str(path))
            continue

        note = note_from_path(path, Path(directory))
        if note:
            notes[str(path)] = note

    for pathstr, linkstrs in path_map.items():
        for linkstr in linkstrs:
            notes[pathstr].add_tag_from_link(linkstr)

    return list(notes.values())


if __name__ == "__main__":
    import pprint
    notes = load_from_dir('./tests/test-notedir/')
    notes[0].add_tag('another-tag')
    notes[0].save_tags()
    pprint.pprint(notes)

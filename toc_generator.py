from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Generator
from urllib import parse

DEFAULT_TITLE = "Table of contents"
DEFAULT_HEADER_LEVELS = 3
SPACES_INDENTATION = 4


class TableOfContents:
    def __init__(
        self,
        source: str | list[Path],
        title: str = DEFAULT_TITLE,
        header_levels: int = DEFAULT_HEADER_LEVELS,
    ):
        """Initialize a TableOfContents object

        Args:
            source (str | list[Path]): A filepath or a list of Paths for
            .md files.
            title (str): The table of contents title. Defaults to
            DEFAULT_TITLE.
            header_levels (int, optional): The max level of headers.
            Defaults to DEFAULT_HEADER_LEVELS.

        Returns:
            TableOfContents: A TableOfContents object
        """
        if isinstance(source, str):
            self.source = [Path(source)]
        else:
            self.source = source
        self.title = title
        self.header_levels = header_levels

    @classmethod
    def from_cwd(
        cls,
        pattern: str = "*.md",
        title: str = DEFAULT_TITLE,
        header_levels: int = DEFAULT_HEADER_LEVELS,
        sort: Callable = str,
    ) -> "TableOfContents":
        """Initialize TableOfContents with .md files from current dir

        Args:
            pattern (str, optional): Pattern of filenames. Defaults
            to "*.md".
            title (str): The table of contents title. Defaults to
            DEFAULT_TITLE.
            header_levels (int, optional): The max level of headers.
            Defaults to DEFAULT_HEADER_LEVELS.
            sort (Callable, optional): Callable to sort the
            list of files. Defaults to "str".

        Returns:
            TableOfContents: A TableOfContents object
        """
        path = Path.cwd()
        files = sorted(path.rglob(pattern), key=sort)
        return cls(files, title, header_levels)

    @property
    def has_multiple_sources(self) -> bool:
        """Check if the table of contents uses multiple .md files

        Returns:
            bool: True if the table of contents uses multiple .md files
            False otherwise
        """
        return len(self.source) > 1

    @property
    def markdown(self) -> str:
        """Table of contents markdown"""
        return self.generate_list()

    def generate_list(self) -> str:
        """Generate the table of contents list

        Returns:
            str: A markdown list with items generated
        """
        content = f"## {self.title}\n"
        for file in self.source:
            for header in self.find_headers(file):
                if self.has_multiple_sources:
                    content += self.generate_item(header, file)
                else:
                    content += self.generate_item(header)
        return content

    def find_headers(self, file: Path) -> Generator:
        """Find headers markdown in file

        Args:
            file (Path): A file where to find headers markdown

        Yields:
            Generator: headers markdown
        """
        with file.open() as f:
            for row in f:
                if row.startswith("#") and row.count("#") <= self.header_levels:
                    yield row

    def generate_item(self, header: str, file: Path | None = None) -> str:
        """Generate a table of contents item markdown

        Args:
            header (str): A header markdown
            file (Path | None, optional): The file to generate a
            relative link. Defaults to None.

        Returns:
            str: A table of contents item markdown
        """
        indentation_level = header.count("#") - 1
        indentation = " " * SPACES_INDENTATION * indentation_level
        header_text = header.replace("#", "").strip()
        anchor = self.slugify(header_text)
        if file is not None:
            rel_link = self.get_relative_link(file)
            return f"{indentation}- [{header_text}](./{rel_link}#{anchor})\n"
        return f"{indentation}- [{header_text}](#{anchor})\n"

    @staticmethod
    def slugify(text: str) -> str:
        """Remove invalid chars and change whitespaces to dashes

        Args:
            text (str): The text to be handle

        Returns:
            str: The text slugifyed
        """
        text = re.sub(r"[^\w\s-]", "", text.lower())
        return re.sub(r"[-\s]+", "-", text).strip("-_")

    def get_relative_link(self, file: Path) -> str:
        """Convert a relative file path to a markdown relative link

        Args:
            file (Path): A .md file
        Returns:
            str: The relative link
        """
        relative_path = file.relative_to(Path.cwd())
        return parse.quote(str(relative_path))

    def save_to(self, destination: str):
        """Save the table of contents to a file

        Args:
            destination (str): Path where to save the file
        """
        Path(destination).write_text(self.markdown)


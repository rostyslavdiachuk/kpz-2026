from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Line:
    number: int
    text: str

@dataclass(frozen=True, slots=True)
class Heading:
    level: int
    title: str

@dataclass(frozen=True, slots=True)
class Bullet:
    text: str

@dataclass(frozen=True, slots=True)
class Empty:
    pass

@dataclass(frozen=True, slots=True)
class Plain:
    text:str


def read(lines: list[str]) -> Iterator[Line]:
    for number, text in enumerate(lines):
        yield Line(number, text.rstrip("\n"))


def classify(line: Line) -> Heading | Bullet | Empty | Plain:
    match line.text.split():
        case []:
            return Empty()
        case [marker, *words] if marker.startswith("#"):
            return Heading(level=len(marker), title=" ".join(words))
        case [_, *words]:
            return Bullet(text=" ".join(words))
        case text:
            return Plain(text=text)
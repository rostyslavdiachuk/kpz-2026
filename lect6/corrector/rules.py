import re
from dataclasses import dataclass
from typing import Iterable, Iterator

from corrector.line import Line


@dataclass
class Issue:
    line: int
    column: int
    message: str
    severity: str


def rule_trailing_space(line: Line) -> Issue | None:
    if line.text != line.text.rstrip():
        return Issue(line.number,
                     len(line.text.rstrip()) + 1,
                     "Trailing space", "warning")
    return None


def find(pattern: str, message: str, severity: str) -> Issue:
    regex = re.compile(pattern)

    def rule(line: Line) -> Issue | None:
        match = regex.search(line.text)
        if match:
            return Issue(line.number, match.start() + 1, message, severity)
        return None

    return rule


rules = [rule_trailing_space,
         find(r"\t", "Tab character", "style"),
         find(r'"', "Double quote", "style")
         ]

def check(lines: Iterable[Line]) -> Iterator[Issue]:
    for line in lines:
        for rule in rules:
            issue = rule(line)
            if issue is not None:
                yield issue



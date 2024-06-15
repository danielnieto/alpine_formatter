import re
from re import Match
from jsbeautifier import beautify

RE_PATTERN = re.compile(
    r"((?P<directive>x-data)\s*=\s*(?P<quote>['\"]))(?P<code>.*?)(?<!\\)(?P=quote)",
    flags=re.DOTALL | re.IGNORECASE,
)


def get_indentation_level(match: Match) -> int:
    before_match = match.string[: match.start()]
    reverse = before_match[::-1]

    if "\n" in reverse:
        return reverse.index("\n")
    return 0


def replace_func(match: Match) -> str:
    formatted = beautify(match.group("code").strip())
    directive = match.group("directive")
    quote = match.group("quote")
    before_closing = ""

    is_multiline = "\n" in formatted

    if is_multiline:
        indentation = " " * get_indentation_level(match)

        indented_formatted = ""
        for line in formatted.split("\n"):
            indented_formatted += f"\n{indentation}{line}"

        formatted = indented_formatted
        before_closing = "\n" + indentation

    return f"{directive}={quote}{formatted}{before_closing}{quote}"


def format_alpine(content: str) -> str:
    result = RE_PATTERN.sub(replace_func, content)
    return result

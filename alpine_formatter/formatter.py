import re
from re import Match
from jsbeautifier import beautify

MODIFIERS = r"(\.[a-zA-Z0-9.-]+)*"
X_DATA = r"x-data"
X_INIT = r"x-init"
X_SHOW = rf"x-show{MODIFIERS}"
X_BIND = r"(x-bind)?:[a-zA-Z0-9-]+"
X_ON = rf"(x-on:|@)[a-zA-Z0-9-]+{MODIFIERS}"
X_TEXT = r"x-text"
X_HTML = r"x-html"
X_MODEL = rf"x-model{MODIFIERS}"
X_MODELABLE = r"x-modelable"
X_FOR = r"x-for"
X_EFFECT = r"x-effect"
X_REF = r"x-ref"
X_IF = r"x-if"
X_ID = r"x-id"

# ignore x-ignore and x-cloak since these directives cannot have values
# ignore x-transition and x-teleport since these directives have CSS as values
ALL_DIRECTIVES = [
    X_DATA,
    X_INIT,
    X_SHOW,
    X_BIND,
    X_ON,
    X_TEXT,
    X_HTML,
    X_MODEL,
    X_MODELABLE,
    X_FOR,
    X_EFFECT,
    X_REF,
    X_IF,
    X_ID,
]

DIRECTIVE = rf"(?P<directive>{'|'.join(ALL_DIRECTIVES)})"
OPENING_QUOTE = r"(?P<quote>['\"]))"
CODE = r"(?P<code>.*?)(?<!\\)"
CLOSING_QUOTE = r"(?P=quote)"

RE_PATTERN = re.compile(
    rf"(?<=\s)({DIRECTIVE}\s*=\s*{OPENING_QUOTE}{CODE}{CLOSING_QUOTE}",
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

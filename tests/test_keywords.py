from pylox.token import TokenType
from pylox.keywords import KEYWORDS

def test_keywords() -> None:
    assert KEYWORDS.issubset((t.value for t in TokenType))

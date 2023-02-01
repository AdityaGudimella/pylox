import pytest

from pylox.errors import Errors, PyloxError, PyloxResolverError
from pylox.interpreter import Interpreter
from pylox.parser import Parser
from pylox.resolver import Resolver


@pytest.mark.parametrize(
    "source, err",
    [
        pytest.param(
            """
            var a;
            if (true) {
                var a = a;
            }
            """,
            PyloxResolverError,
            id="assign var to self",
        ),
    ],
)
def test_resolver_raises_error(source: str, err: type[PyloxError]) -> None:
    """Test that the resolver raises the expected error."""
    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    expr = Parser.from_source(source, errors=Errors()).parse()
    with pytest.raises(err):
        resolver.resolve(*expr)

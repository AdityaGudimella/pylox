import abc

import attrs


@attrs.define(frozen=True)
class Node(abc.ABC):
    @property
    @abc.abstractmethod
    def literal(self) -> str:
        raise NotImplementedError

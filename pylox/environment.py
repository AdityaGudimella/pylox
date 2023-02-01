import copy
import typing as t

import attrs


@attrs.define()
class Environment:
    enclosing: "Environment | None" = attrs.field(default=None)
    values: dict[str, t.Any] = attrs.field(factory=dict)

    def assign(self, name: str, value: t.Any) -> None:
        """Assign a value to an existing var."""
        if name in self.values:
            self.values[name] = value
        elif self.enclosing:
            self.enclosing.assign(name, value)
        else:
            raise KeyError(f"Undefined variable {name}.")

    def define(self, name: str, value: t.Any) -> None:
        self.values[name] = value

    def get(self, name: str) -> t.Any:
        """Get the value of a var."""
        try:
            return self.values[name]
        except KeyError:
            if self.enclosing:
                return self.enclosing.get(name)
            raise

    def get_at(self, distance: int, name: str) -> t.Any:
        return self.ancestor(distance).values[name]

    def assign_at(self, distance: int, name: str, value: t.Any) -> None:
        self.ancestor(distance).values[name] = value

    def clone(self, enclosing: "Environment | None" = None) -> "Environment":
        return Environment(values=copy.deepcopy(self.values), enclosing=enclosing)

    def ancestor(self, distance: int) -> "Environment":
        env = self
        for _ in range(distance):
            if (enclosing := env.enclosing) is None:
                raise ValueError("No enclosing environment.")
            env = enclosing
        return env

    def test_get_var(self, name: str) -> t.Any:
        return self.values[name]

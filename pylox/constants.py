import enum


class FunctionType(enum.Enum):
    NONE = "none"
    FUNCTION = "function"
    METHOD = "method"
    INITIALIZER = "initializer"


class ClassType(enum.Enum):
    NONE = "none"
    CLASS = "class"
    SUBCLASS = "subclass"

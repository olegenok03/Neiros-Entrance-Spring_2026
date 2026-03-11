
"""Module providing geometry shapes classes.
"""
from abc import ABC, abstractmethod
from helpers import camelcase_to_snakecase


class ShapeTypeDescriptor:
    def __get__(self, instance, owner) -> str:
        return camelcase_to_snakecase(str(owner.__name__))

    def __set__(self, instance, value) -> None:
        raise AttributeError(
            f'Cannot assign to attribute "shape_type" for class "{instance.__class__.__name__}"'
        )

    def __delete__(self, instance) -> None:
        raise AttributeError(
            f'Cannot delete attribute "shape_type" of class "{instance.__class__.__name__}"'
        )


class Shape(ABC):
    """Abstract geometry shape class."""
    shape_type = ShapeTypeDescriptor()

    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def get_borders(self) -> tuple[float, float, float, float]:
        """Returns rectangular borders of the shape."""

    def fits_in(self, min_x: float, min_y: float, max_x: float, max_y: float) -> bool:
        """Returns True, if the shape fits in provided rectangular borders.
        Returns False otherwise.
        """
        x1, y1, x2, y2 = self.get_borders()
        return all((
            min(x1, x2) >= min_x,
            min(y1, y2) >= min_y,
            max(x1, x2) <= max_x,
            max(y1, y2) <= max_y
        ))


class Point(Shape):
    """Point class."""
    def __init__(self, x0: float, y0: float) -> None:
        self.x0 = x0
        self.y0 = y0

    def __str__(self) -> str:
        return self.shape_type + f'(x0: {self.x0}; y0: {self.y0})'

    def get_borders(self) -> tuple[float, float, float, float]:
        return (self.x0, self.y0, self.x0, self.y0)


class LineSegment(Shape):
    """Line segment class."""
    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __str__(self) -> str:
        return self.shape_type + f'(x1: {self.x1}; y1: {self.y1}; x2: {self.x2}; y2: {self.y2})'

    def get_borders(self) -> tuple[float, float, float, float]:
        return (
            min(self.x1, self.x2),
            min(self.y1, self.y2),
            max(self.x1, self.x2),
            max(self.y1, self.y2)
        )


class Circle(Shape):
    """Circle class."""
    def __init__(self, x0: float, y0: float, r: float) -> None:
        self.x0 = x0
        self.y0 = y0
        self.r = r # TODO: validation > 0

    def __str__(self) -> str:
        return self.shape_type + f'(x0: {self.x0}; y0: {self.y0}; r: {self.r})'

    def get_borders(self) -> tuple[float, float, float, float]:
        return (
            self.x0 - self.r,
            self.y0 - self.r,
            self.x0 + self.r,
            self.y0 + self.r
        )


class Square(Shape):
    """Square class."""
    def __init__(self, x1: float, y1: float, a: float) -> None:
        self.x1 = x1
        self.y1 = y1
        self.a = a # TODO: validation > 0

    def __str__(self) -> str:
        return self.shape_type + f'(x1: {self.x1}; y1: {self.y1}; a: {self.a})'

    def get_borders(self) -> tuple[float, float, float, float]:
        return (
            self.x1,
            self.y1,
            self.x1 + self.a,
            self.y1 + self.a
        )


SHAPES_REGISTRY: dict[str, type[Shape]] = {
    cls.shape_type: cls for cls in Shape.__subclasses__()
}

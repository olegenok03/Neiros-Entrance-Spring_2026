"""Module providing drawings classes and the CanvasManager class."""
from functools import singledispatchmethod
import inspect
from tkinter import Canvas, Tk
from shapes import Shape, Point, LineSegment, Circle, Square, SHAPES_REGISTRY


class Layer:
    """Class for shape layer."""
    _width = 3.0 #TODO: add to config
    _color = 'black' #TODO: add to config
    _highlight_color = 'yellow' #TODO: add to config

    def __init__(self, shape: Shape, canvas: Canvas) -> None:
        if not shape.fits_in(0, 0, canvas.winfo_reqwidth(), canvas.winfo_reqheight()):
            raise ValueError('Shape out of canvas')

        self._shape = shape
        self._canvas = canvas
        self._id = self._draw()
        self._is_highlighted = False

    @property
    def id(self) -> int:
        return self._id

    @property
    def is_highlighted(self) -> bool:
        return self._is_highlighted

    @is_highlighted.setter
    def is_highlighted(self, val: bool) -> None:
        self._is_highlighted = val
        if self._is_highlighted:
            self._change_color(self._shape, self._highlight_color)
        else:
            self._change_color(self._shape, self._color)

    def _draw(self) -> int:
        return self._draw_implementation(self._shape)

    @singledispatchmethod
    def _draw_implementation(self, shape: Shape) -> int:
        raise TypeError(f'Невозможно отрисовать {type(self)}.')

    @_draw_implementation.register(Point|Circle)
    def _draw_circle(self, shape: Point|Circle) -> int:
        return self._canvas.create_oval(
            shape.get_borders(),
            width=self._width,
            outline=self._color
        )

    @_draw_implementation.register(LineSegment)
    def _draw_line_segment(self, shape: LineSegment) -> int:
        return self._canvas.create_line(
            (shape.x1, shape.y1, shape.x2, shape.y2),
            width=self._width,
            fill=self._color
        )

    @_draw_implementation.register(Square)
    def _draw_square(self, shape: Square) -> int:
        return self._canvas.create_rectangle(
            shape.get_borders(),
            width=self._width,
            outline=self._color
        )

    @singledispatchmethod
    def _change_color(self, shape: Shape, color: str) -> None:
        raise TypeError(f'Невозможно изменить цвет {type(self)}.')

    @_change_color.register(Point|Circle|Square)
    def _change_color_outline(self, _: Point|Circle|Square, color: str) -> None:
        self._canvas.itemconfig(self._id, outline=color)

    @_change_color.register(LineSegment)
    def _change_color_fill(self, _: LineSegment, color: str) -> None:
        self._canvas.itemconfig(self._id, fill=color)

    def delete(self) -> None:
        """Deletes shape from canvas."""
        self._canvas.delete(self._id)

    def __str__(self) -> str:
        return f'{self._shape} with id {self._id}'


class CanvasManager:
    """Class for managing canvas and shapes."""
    _canvas_width = 900
    _canvas_height = 600
    _canvas_bg_color = '#F0F0F0'

    def __init__(self, master: Tk) -> None:
        self._canvas = Canvas(
            master,
            height=self._canvas_height,
            width=self._canvas_width,
            background=self._canvas_bg_color
        )
        self._canvas.pack()
        self._canvas.update() #TODO: check whether size is correctly updated
        self._id_to_layer: dict[int, Layer] = {}

    def create_layer(self, shape_type: str, *args) -> int:
        """Creates layer of provided shape with provided parameters."""
        if not shape_type in SHAPES_REGISTRY:
            raise ValueError(f'Unknown shape: {shape_type}')
        shape = SHAPES_REGISTRY[shape_type](*args)
        layer = Layer(shape, self._canvas)
        self._id_to_layer[layer.id] = layer
        return layer.id

    def get_layer_name(self, layer_id: int) -> str:
        """Returns layer name by its id."""
        return str(self._id_to_layer[layer_id])

    def get_layers_names(self) -> list[str]:
        """Returns list of layers names."""
        return [str(layer) for layer in self._id_to_layer.values()]

    def _validate_layer_id(self, layer_id: int) -> None:
        if layer_id not in self._id_to_layer:
            raise KeyError(f'No layer with id {layer_id}.')

    def force_canvas_update(self) -> None:
        """Updates canvas forcibly."""
        self._canvas.update()

    def highlight_layer(self, layer_id: int) -> None:
        """Sets color of the layer with provided id to the highlight color."""
        self._id_to_layer[layer_id].is_highlighted = True

    def remove_layer_highlight(self, layer_id: int) -> None:
        """Sets color of the layer with provided id to the basic color."""
        self._validate_layer_id(layer_id)
        self._id_to_layer[layer_id].is_highlighted = False

    def delete_layer(self, layer_id: int) -> None:
        """Deletes layer from canvas and layers list by its id."""
        self._validate_layer_id(layer_id)
        self._id_to_layer[layer_id].delete()
        del self._id_to_layer[layer_id]

    def get_create_help(self) -> str:
        """Returns detailed description of \"create_layer\" method options."""
        lines = ['Shape-specific usage:']
        for num, (shape_type, cls) in enumerate(sorted(SHAPES_REGISTRY.items())):
            sig = inspect.signature(cls.__init__)
            params = [p for p in sig.parameters if p != 'self']
            params_str = ' '.join(f'<{p}>' for p in params)
            lines.append(f'    {num}) create {shape_type} {params_str}')
        return '\n'.join(lines)

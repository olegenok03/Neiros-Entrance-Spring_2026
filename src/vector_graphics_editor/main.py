"""Main VGE module."""
from tkinter import Tk, TclError
import cmd
import shlex
from drawings import CanvasManager


class VGEInterpreter(cmd.Cmd):
    """Class providing REPL command interpreter."""
    intro = 'VectorGraphicsEditor 1.0. Type "help" or "?" to see available commands.'
    prompt = 'VGE >>> '
    aliases = {'del': 'delete', 'ls': 'list'}
    err_prefix = ''

    def __init__(
            self,
            widget: Tk,
            completekey: str = 'tab',
            stdin=None,
            stdout=None
        ) -> None:
        super().__init__(completekey, stdin, stdout)
        self._widget = widget
        self._exiting = False
        self._widget.protocol('WM_DELETE_WINDOW', self._on_close_widget)

        self._cm = CanvasManager(widget)

    def _on_close_widget(self) -> None:
        self._exiting = True
        self._widget.destroy()

    def precmd(self, line: str) -> str:
        parts = line.strip().split(maxsplit=1)
        if not parts:
            return line.strip()

        cmd_name = parts[0]
        rest = parts[1] if len(parts) > 1 else ''
        if cmd_name in self.aliases:
            cmd_name = self.aliases[cmd_name]
        return f'{cmd_name} {rest}'.strip()

    def postcmd(self, stop: bool, line: str) -> bool:
        if self._exiting:
            stop = True
        return super().postcmd(stop, line)

    def emptyline(self) -> bool:
        return False

    def default(self, line: str) -> None:
        print(f'Unknown command: "{line}". Type "help" to list commands.')

    def do_create(self, arg: str) -> None:
        """Create a new shape layer. Usage: create <shape_type> [<arg> ...]"""
        try:
            shape_type, *shape_args = shlex.split(arg)
            shape_args = list(map(float, shape_args))
            layer_id = self._cm.create_layer(shape_type, *shape_args)
        except (ValueError, TypeError) as args_error_msg:
            print(args_error_msg)
            return
        except TclError:
            print('Widget was closed.')
            return

        layer_name = self._cm.get_layer_name(layer_id)
        print(f'Created layer {layer_name}.')

    def help_create(self) -> None:
        """Print detailed help for \"create\" command."""
        print(self.do_create.__doc__)
        print(self._cm.get_create_help())

    def do_list(self, _: str) -> None:
        """Print the list of layers."""
        layers = self._cm.get_layers_names()
        if not layers:
            print('List is empty.')
            return

        print('Shape layers:')
        for num, layer in enumerate(layers, 1):
            print(f'    {num}) {layer}')

    def do_delete(self, arg: str) -> None:
        """Delete a layer by its id. Usage: delete <layer_id>"""
        try:
            layer_id = int(arg.strip())
        except ValueError:
            print('Layer id must be numeric.')
            return

        try:
            self._cm.highlight_layer(layer_id)
        except KeyError:
            print(f'No layer with id {layer_id}.')
            return
        except TclError:
            print('Widget was closed.')
            return

        layer_name = self._cm.get_layer_name(layer_id)
        msg = f'Sure you want to delete layer {layer_name} (highlighted)? (y/n): '
        option = input(msg).strip().lower()
        if option in ('y', 'yes'):
            try:
                self._cm.delete_layer(layer_id)
                print(f'Deleted layer {layer_name}.')
                return
            except TclError:
                print('Widget was closed.')
                return

        try:
            self._cm.remove_layer_highlight(layer_id)
            print('Canceled.')
        except TclError:
            print('Widget was closed.')

    def do_exit(self, _: str) -> bool:
        """Exit the VGE."""
        print('Terminating VGE...')
        return True


if __name__ == '__main__':
    root = Tk()
    editor_interpreter = VGEInterpreter(root)
    editor_interpreter.cmdloop()

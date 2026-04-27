from textual.screen import ModalScreen
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label, Switch
from textual.message import Message
from typing import TYPE_CHECKING
from termout.storage import HistoryManager

if TYPE_CHECKING:
    from termout.app import Termout


class SettingsMenu(ModalScreen):
    class VimMode(Message):
        pass

    app: "Termout"
    BINDINGS = [("c", "close_menu", "Close Menu")]

    def compose(self):
        with Vertical(id="menu"):
            yield Label("Configs", id="menu_title")

            with Horizontal(classes="option_row"):
                yield Label("Vim Bindings", classes="option_label")
                yield Switch(value=False, id="vim_switch")

            yield Button("Close", id="btn_close", variant="primary")

    def on_mount(self) -> None:
        is_vim_mode_on = self.app.settings.get("vim_mode", False)
        self.query_one("#vim_switch", Switch).value = is_vim_mode_on

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn_close":
            self.app.pop_screen()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "vim_switch":
            history = HistoryManager.load()

            if "settings" not in history:
                history["settings"] = {}

            history["settings"]["vim_mode"] = event.value

            HistoryManager.save(history)

    def action_close_menu(self) -> None:
        self.app.pop_screen()

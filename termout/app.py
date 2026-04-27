from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Input
from textual.containers import VerticalScroll
from textual import events
from pathlib import Path
from termout.storage import HistoryManager
from termout.timer_widget import Countdown
from termout.screen import SettingsMenu
import secrets


class Termout(App):
    history = HistoryManager.load()
    settings: dict = {}

    CSS_PATH = Path(__file__).parent / "termout.tcss"
    BINDINGS = [
        ("a", "add_countdown", "Add"),
        ("s", "start_countdown", "Start"),
        ("p", "stop_countdown", "Stop"),
        ("r", "reset_countdown", "Reset"),
        ("d", "delete_countdown", "Del"),
        ("n", "focus_input_name", "Name"),
        ("R", "focus_input_repeats", "Reps"),
        ("M", "toggle_switch", "Switch"),
        ("c", "show_settings", "Config"),
    ]

    def on_mount(self) -> None:
        history = self.history
        container = self.query_one("#countdowns")

        timers_dict = history.get("timers", {})
        self.settings = history.get("settings", {})

        if len(timers_dict) > 0:
            id_to_focus = ""
            for timer_id, info in timers_dict.items():
                new_timer = Countdown(
                    value=info["time"],
                    name=info["name"],
                    repeats=info["repeats"],
                    switch_state=info["enabled"],
                    id=f"timer_{timer_id}",
                )

                container.mount(new_timer)
                if id_to_focus == "":
                    id_to_focus = f"timer_{timer_id}"

            self.query_one(f"#{id_to_focus}").focus()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Button(label="+", id="add", classes="add")
        yield Input(placeholder="00:00:00", type="text", id="input", classes="inactive")
        yield VerticalScroll(id="countdowns")
        yield Footer()

    def action_add_countdown(self) -> None:
        my_input = self.query_one("#input", Input)
        my_input.display = True
        my_input.focus()

    def action_show_settings(self):
        self.push_screen(SettingsMenu())

    def on_key(self, event: events.Key) -> None:
        my_input = self.query_one("#input", Input)
        key = event.key.lower()

        if key == "escape":
            if my_input.has_focus:
                my_input.display = False
        elif key == "k" or key == "up":
            self.move(pos="up")
        elif key == "j" or key == "down":
            self.move(pos="down")

    def move(self, pos: str) -> None:
        timers = list(self.query(Countdown))
        if not timers:
            return

        last_timer = timers[-1]
        first_timer = timers[0]

        if pos == "down":
            if last_timer.has_focus:
                return
            self.screen.focus_next(Countdown)
        elif pos == "up":
            if first_timer.has_focus:
                return
            self.screen.focus_previous(Countdown)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "input":
            unique_id = secrets.token_hex(2)
            countdown = Countdown(value=event.value, id=f"timer_{unique_id}")
            self.query_one("#input").display = False
            self.query_one("#countdowns").mount(countdown)
            countdown.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        id = event.button.id
        if id == "add":
            self.query_one("#input").display = True
            self.query_one("#input").focus()


app = Termout()
if __name__ == "__main__":
    app.run()

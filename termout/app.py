from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Input
from textual.containers import VerticalScroll
from textual import events
from pathlib import Path
from storage import HistoryManager
from timer_widget import Countdown
import secrets


class Termout(App):
    last_id = 0

    CSS_PATH = Path(__file__).parent / "termout.tcss"
    BINDINGS = [
        ("a", "add_countdown", "Add"),
        ("s", "start_countdown", "Start"),
        ("p", "stop_countdown", "Stop"),
        ("r", "reset_countdown", "Reset"),
        ("d", "delete_countdown", "Del"),
        ("n", "focus_input_name", "Name"),
        ("R", "focus_input_repeats", "Reps"),
        ("M", "focus_swtich", "Switch"),
    ]

    def on_mount(self) -> None:
        history = HistoryManager.load()
        container = self.query_one("#countdowns")

        timers_dict = history.get("timers", {})

        for timer_id, info in timers_dict.items():
            new_timer = Countdown(
                value=info["time"],
                name=info["name"],
                repeats=info["repeats"],
                switch_state=info["enabled"],
                id=f"timer_{timer_id}",
            )
            container.mount(new_timer)

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

    def on_key(self, event: events.Key) -> None:
        my_input = self.query_one("#input", Input)
        key = event.key.lower()
        if key == "escape":
            if my_input.has_focus:
                my_input.display = False
        elif key == "k":
            self.screen.focus_previous(Countdown)
        elif key == "j":
            self.screen.focus_next(Countdown)

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

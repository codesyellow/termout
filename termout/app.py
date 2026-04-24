from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Digits, Input, Static
from textual.reactive import reactive
from textual.containers import VerticalScroll, Horizontal
from textual.message import Message
from textual.validation import Integer, Length
from plyer import notification
from textual import on, events
from pathlib import Path


class StartCount(Digits):
    class Started(Message):
        pass

    class Finished(Message):
        pass

    time: reactive = reactive(0)
    default_time: int = 0
    has_started: bool = False

    def __init__(self, value) -> None:
        super().__init__()
        seconds = self.str_to_seconds(value)
        self.default_time = seconds
        self.time = seconds

    def str_to_seconds(self, time_str: str) -> int:
        if ":" not in time_str:
            return int(time_str) * 60

        parts = list(map(int, time_str.split(":")))

        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h, m, s = 0, parts[0], parts[1]
        else:
            h, m, s = 0, 0, parts[0]

        return h * 3600 + m * 60 + s

    def on_mount(self) -> None:
        self.interval = self.set_interval(1, self.update_time, pause=True)

    def is_repeating(self) -> bool:
        return True

    def update_time(self) -> None:
        if not self.has_started:
            self.post_message(self.Started())
            self.has_started = True
        if self.time > 0:
            self.time -= 1
            return

        self.time = self.default_time
        self.has_started = False
        self.post_message(self.Finished())

    def watch_time(self) -> None:
        minutes, seconds = divmod(self.time, 60)
        horas, minutes = divmod(minutes, 60)
        self.update(f"{horas:02}:{minutes:02}:{seconds:02}")

    def start(self) -> None:
        self.interval.resume()

    def stop(self) -> None:
        self.interval.pause()


class Countdown(Static):
    countdown_name = reactive("Name")
    can_focus = True
    repeats_left = 1

    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Button("start", id="btn_start"),
            Button("stop", id="btn_stop", classes="inactive"),
            classes="btn_group",
        )
        yield StartCount(value=self.value)

        yield Horizontal(
            Button("del", id="btn_delete"),
            Button("res", id="btn_reset"),
            classes="btn_group2",
        )

        yield Horizontal(
            Input(
                placeholder="Name it!",
                id="input_name",
                validators=[
                    Length(maximum=20),
                ],
            ),
            Input(
                value="1",
                placeholder="1",
                id="input_repeats",
                type="integer",
                validators=[
                    Integer(minimum=1, maximum=99),
                    Length(minimum=1, maximum=2),
                ],
            ),
            classes="input_group",
        )

    def send_notification(self, title: str, message: str) -> None:
        notification.notify(
            title=title,
            message=message,
            app_name="Termout",
        )  # type: ignore

    def handle_countdown(self, cmd: str) -> None:
        timer = self.query_one(StartCount)
        timer.time = timer.default_time
        if cmd == "start":
            timer.start()
        else:
            timer.stop()

    def disable_inputs(self, inputs_id: list, value: bool) -> None:
        for id in inputs_id:
            input = self.query_one(f"#{id}", Input)
            input.disabled = value

    def toggle_buttons_visibility(self, display: list[bool]) -> None:
        self.query_one("#btn_start").display = display[0]
        self.query_one("#btn_stop").display = display[1]

    @on(StartCount.Started)
    def handle_timer_start(self) -> None:
        self.send_notification(title=f"{self.countdown_name}", message="Has started!")
        self.disable_inputs(inputs_id=["input_name", "input_repeats"], value=True)

    @on(StartCount.Finished)
    def handler_timer_end(self) -> None:
        self.notify(f"{self.repeats_left}")
        if self.repeats_left > 1:
            self.repeats_left -= 1
            self.notify(f"{self.repeats_left}")
            self.handle_countdown(cmd="start")
        else:
            self.notify(f"Timer '{self.countdown_name}' finalizado!")
            self.send_notification(
                title=f"{self.countdown_name}", message="Has finished!"
            )
            self.handle_countdown(cmd="stop")
            self.toggle_buttons_visibility(display=[True, False])
            self.disable_inputs(inputs_id=["input_name", "input_repeats"], value=False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        id = event.button.id
        if id == "btn_start":
            self.start_timer()
        elif id == "btn_stop":
            self.stop_timer()
        elif id == "btn_delete":
            self.remove()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "input_repeats":
            try:
                self.repeats_left = int(event.value)
            except ValueError:
                pass
        if event.input.id == "input_name":
            self.countdown_name = event.value

    def on_key(self, event: events.Key) -> None:
        key = event.key.lower()
        input_name = self.query_one("#input_name", Input)
        input_repeats = self.query_one("#input_repeats", Input)
        if key == "escape":
            if input_name.has_focus:
                input_name.blur()
            elif input_repeats.has_focus:
                input_repeats.blur()
        if key == "s":
            self.start_timer()
        elif key == "p":
            self.stop_timer()
        elif key == "d":
            self.remove()
        elif key == "n":
            name = self.query_one("#input_name", Input)
            name.focus()

    def start_timer(self) -> None:
        startcount = self.query_one(StartCount)
        self.toggle_buttons_visibility(display=[False, True])
        startcount.start()

    def stop_timer(self) -> None:
        startcount = self.query_one(StartCount)
        self.toggle_buttons_visibility(display=[True, False])
        startcount.stop()


class Termout(App):
    last_id = 0

    CSS_PATH = Path(__file__).parent / "termout.tcss"
    BINDINGS = [
        ("a", "add_countdown", "Add"),
    ]

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
            self.screen.focus_previous()
        elif key == "j":
            self.screen.focus_next()

    @on(Input.Submitted)
    def handle_submit(self, event: Input.Submitted) -> None:
        if event.input.id == "input":
            countdown = Countdown(value=event.value)
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

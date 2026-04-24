from textual.app import ComposeResult
from textual import on, events
from textual.widgets import Button, Input, Static, Switch
from textual.reactive import reactive
from textual.containers import Horizontal
from textual.validation import Integer, Length
from utils import send_notification
from components import StartCount
from storage import HistoryManager


class Countdown(Static):
    countdown_name = reactive("Name")
    repeats_left = reactive(1)
    is_enabled = reactive(True)
    switch_state = False
    has_started = False
    can_focus_children = False
    can_focus = True

    BINDINGS = [
        ("s", "start", "Start"),
        ("p", "pause", "Stop"),
        ("r", "reset", "Reset"),
        ("d", "delete", "Del"),
        ("n", "focus_name", "Name"),
        ("R", "focus_reps", "Reps"),
        ("M", "focus_switch", "Switch"),
    ]

    def action_start(self) -> None:
        if not self.has_started:
            self.start_timer()
            self.has_started = True

    def action_pause(self) -> None:
        if self.has_started:
            self.stop_timer()
            self.has_started = False

    def action_reset(self) -> None:
        self.reset_timer()
        self.has_started = False

    def action_delete(self) -> None:
        self.remove()

    def action_focus_name(self) -> None:
        self.query_one("#input_name", Input).focus()

    def action_focus_reps(self) -> None:
        self.query_one("#input_repeats", Input).focus()

    def action_focus_switch(self) -> None:
        switch = self.query_one(Switch)
        if switch.value:
            switch.value = False
        else:
            switch.value = True

    def __init__(
        self,
        value: str,
        name: str = "Timer",
        repeats: int = 1,
        switch_state: bool = False,
        enabled: bool = True,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)

        self.value = value
        self.countdown_name = name
        self.repeats_left = repeats
        self.is_enabled = enabled
        self.switch_state = switch_state

    def watch_countdown_name(self) -> None:
        self._update_history()

    def watch_repeats_left(self) -> None:
        self._update_history()

    def _update_history(self) -> None:
        if self.id:
            my_id = self.id.replace("timer_", "")
            history = HistoryManager.load()

            if my_id in history.get("timers", {}):
                history["timers"][my_id]["name"] = self.countdown_name
                history["timers"][my_id]["repeats"] = self.repeats_left
                HistoryManager.save(history)

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Button("start", id="btn_start"),
            Button("stop", id="btn_stop", classes="inactive"),
            classes="btn_group",
        )
        yield StartCount(value=self.value)
        yield Switch(value=self.switch_state)

        yield Horizontal(
            Button("del", id="btn_delete"),
            Button("res", id="btn_reset"),
            classes="btn_group2",
        )

        yield Horizontal(
            Input(
                value=str(self.countdown_name),
                placeholder="Name it!",
                id="input_name",
                validators=[
                    Length(maximum=20),
                ],
            ),
            Input(
                value=str(self.repeats_left),
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

    @on(StartCount.Finished)
    def handler_timer_end(self) -> None:
        if self.repeats_left > 1:
            self.repeats_left -= 1
            self.notify(f"{self.repeats_left}")
            self.handle_countdown(cmd="start")
        else:
            self.notify(f"Timer '{self.countdown_name}' finalizado!")
            send_notification(
                title=f"{self.countdown_name}",
                message="Has finished!",
                timeout=8,
            )
            self.handle_countdown(cmd="stop")
            self.toggle_buttons_visibility(display=[True, False])
            self.disable_inputs(inputs_id=["input_name", "input_repeats"], value=False)
            self.has_started = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        id = event.button.id
        if id == "btn_start":
            self.start_timer()
        elif id == "btn_stop":
            self.stop_timer()
        elif id == "btn_reset":
            self.reset_timer()
        elif id == "btn_delete":
            self.remove()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if self.id is None:
            return

        history = HistoryManager.load()
        timers = history.get("timers", {})
        my_id = self.id.replace("timer_", "")

        if my_id not in timers:
            self.notify(f"{self.countdown_name}/{self.value} was added to the list")
            timers[my_id] = {
                "name": self.countdown_name,
                "time": self.value,
                "repeats": self.repeats_left,
                "enabled": True,
            }
        else:
            self.notify(f"{self.countdown_name}/{self.value} was deleted!")
            del timers[my_id]

        history["timers"] = timers
        HistoryManager.save(history)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "input_repeats":
            if event.value.isdigit():
                self.repeats_left = int(event.value)
                self.notify(f"{self.repeats_left} reps was stored!")
                self.focus()
        if event.input.id == "input_name":
            self.countdown_name = event.value
            self.notify(f"{self.countdown_name} name was stored!")
            self.focus()

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            if self.query("Input:focus"):
                self.focus()

    def start_timer(self) -> None:
        startcount = self.query_one(StartCount)
        startcount.start()
        self.disable_inputs(inputs_id=["input_name", "input_repeats"], value=True)
        self.toggle_buttons_visibility(display=[False, True])
        send_notification(
            title=f"{self.countdown_name}",
            message="Has started!",
            timeout=8,
        )

    def stop_timer(self) -> None:
        startcount = self.query_one(StartCount)
        startcount.stop()
        self.toggle_buttons_visibility(display=[True, False])

    def reset_timer(self) -> None:
        startcount = self.query_one(StartCount)
        startcount.reset()
        self.toggle_buttons_visibility(display=[True, False])
        self.disable_inputs(inputs_id=["input_name", "input_repeats"], value=False)

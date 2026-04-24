from textual.widgets import Digits
from textual.message import Message
from utils import str_to_seconds
from textual.reactive import reactive


class StartCount(Digits):
    class Finished(Message):
        pass

    time: reactive = reactive(0)
    default_time: int = 0
    has_started: bool = False

    def __init__(self, value) -> None:
        super().__init__()
        seconds = str_to_seconds(value)
        self.default_time = seconds
        self.time = seconds

    def on_mount(self) -> None:
        self.interval = self.set_interval(1, self.update_time, pause=True)

    def is_repeating(self) -> bool:
        return True

    def update_time(self) -> None:
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

    def reset(self) -> None:
        self.interval.pause()
        self.time = self.default_time

    def stop(self) -> None:
        self.interval.pause()

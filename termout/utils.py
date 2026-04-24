import sys
import subprocess
from plyer import notification


def send_notification(title: str, message: str, timeout: int = 8):
    if sys.platform == "linux":
        try:
            subprocess.run(
                ["notify-send", "-t", str(timeout * 1000), title, message], check=False
            )
        except FileNotFoundError:
            _plyer_fallback(title, message, timeout)
    else:
        _plyer_fallback(title, message, timeout)


def _plyer_fallback(title, message, timeout):
    notification.notify(
        title=title, message=message, app_name="Termout", timeout=timeout
    )  # type: ignore


def str_to_seconds(time_str: str) -> int:
    """Converte 00:00:00 ou minutos em segundos."""
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

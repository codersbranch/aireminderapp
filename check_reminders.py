from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
import os
import time
import webbrowser

from bs4 import BeautifulSoup

REMINDERS_FILE = Path("reminders.txt")
NOTIFICATION_HTML_FILE = Path("notification.html")


def read_reminders(file_path: Path) -> dict[str, list[str]]:
    reminders: dict[str, list[str]] = defaultdict(list)

    if not file_path.exists():
        return reminders

    with file_path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if "-" not in line:
                continue

            time_part, message = line.split("-", 1)
            time_str = time_part.strip()
            msg = message.strip().strip('"')

            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                continue

            if msg:
                reminders[time_str].append(msg)

    return reminders


def write_reminder(new_reminder: str, html_path: Path = NOTIFICATION_HTML_FILE) -> None:
    with html_path.open("r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    reminder_list = soup.find("ul", {"id": "reminder-list"})
    if reminder_list is None:
        raise ValueError("notification.html is missing <ul id='reminder-list'>.")

    reminder_list.clear()
    list_item = soup.new_tag("li")
    list_item.append(new_reminder)
    reminder_list.append(list_item)

    with html_path.open("w", encoding="utf-8") as file:
        file.write(soup.prettify())

    print("✅ Reminder added to HTML file.")


def open_html_file(html_path: Path = NOTIFICATION_HTML_FILE) -> None:
    file_url = f"file://{os.path.abspath(html_path)}"
    webbrowser.open(file_url)


def main() -> None:
    already_triggered: set[tuple[str, int]] = set()
    reminders_by_time: dict[str, list[str]] = {}
    last_mtime: float | None = None

    while True:
        try:
            mtime = REMINDERS_FILE.stat().st_mtime
        except FileNotFoundError:
            reminders_by_time = {}
            last_mtime = None
            time.sleep(2)
            continue

        if last_mtime != mtime:
            reminders_by_time = read_reminders(REMINDERS_FILE)
            last_mtime = mtime

        now = datetime.now().strftime("%H:%M")
        due_messages = reminders_by_time.get(now, [])

        for idx, message in enumerate(due_messages):
            reminder_key = (now, idx)
            if reminder_key in already_triggered:
                continue

            print(f"[{now}] Reminder: {message}")
            write_reminder(message)
            open_html_file()
            already_triggered.add(reminder_key)

        time.sleep(2)


if __name__ == "__main__":
    main()

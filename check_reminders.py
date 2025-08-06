import time
from datetime import datetime
import webbrowser
import os
from bs4 import BeautifulSoup


def read_reminders(file_path):
    reminders = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '-' in line:
                time_part, message = line.strip().split('-', 1)
                time_str = time_part.strip()
                msg = message.strip().strip('"')
                reminders[time_str] = msg
    return reminders


def write_reminder(new_reminder):   
     # Load existing HTML file
    with open("notification.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

        # Find the <ul> element
        ul = soup.find("ul", {"id": "reminder-list"})
        ul.clear()
        # Create new <li> tag
        li = soup.new_tag("li")       
        li.append(new_reminder)      
        ul.append(li)   

        # Save updated HTML
        with open("notification.html", "w", encoding="utf-8") as f:
            f.write(str(soup.prettify()))
        print("✅ Reminder added to HTML file.")


def open_html_file():
    # Path to your local HTML file
    html_file = os.path.abspath("notification.html")
    # Convert to file URL
    file_url = f"file://{html_file}"

    # Open in default web browser
    webbrowser.open(file_url)

def main():
    file_path = 'reminders.txt'
    already_triggered = set()

    while True:
        now = datetime.now().strftime('%H:%M')  # Current time in HH:MM format
        reminders = read_reminders(file_path)

        if now in reminders and now not in already_triggered:
            print(f"[{now}] Reminder: {reminders[now]}")
            write_reminder(reminders[now])
            open_html_file()
            already_triggered.add(now)

        time.sleep(2)

if __name__ == '__main__':
    main()

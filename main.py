import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

cookies = os.environ.get("COOKIE_PART1", "") + os.environ.get("COOKIE_PART2", "")

HEADERS = {"User-Agent": "Mozilla/5.0", "Cookie": cookies}

URL = "https://p.vendista.ru/Transactions/Search?OrderByColumn=2&OrderDesc=True&ItemsOnPage=50&TerminalId=153950"

STATE_FILE = "state.json"


def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE, "r", encoding="utf-8"))
    return {"last_marker": "", "cash": 0.0, "date": ""}


def save_state(state):
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
        timeout=30
    )


def main():
    state = load_state()

    today = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y")

    if state["date"] != today:
        state["date"] = today
        state["cash"] = 0.0
        state["last_marker"] = ""

    r = requests.get(URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.find_all("tr")

    if len(rows) < 2:
        return

    new_sales = []

    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        t = cols[2].text.strip()
        amount_raw = cols[4].text.replace("₽", "").replace(" ", "").replace(",", ".").strip()

        try:
            amount = float(amount_raw)
        except:
            continue

        marker = f"{t}|{amount}"

        # 🔥 стоп-условие (главный фикс)
        if marker == state["last_marker"]:
            break

        new_sales.append((marker, t, amount))

    if not new_sales:
        return

    new_sales.reverse()

    for marker, t, amount in new_sales:
        state["cash"] += amount

        send_telegram(
            f"💰 <b>Продажа</b>\n"
            f"📅 {t}\n"
            f"🛒 {int(amount)} ₽\n"
            f"🏦 Касса: {int(state['cash'])} ₽"
        )

        state["last_marker"] = marker

    save_state(state)


if __name__ == "__main__":
    main()

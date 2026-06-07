import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

cookies = (
    os.environ.get("COOKIE_PART1", "")
    + os.environ.get("COOKIE_PART2", "")
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": cookies
}

URL = "https://p.vendista.ru/Transactions/Search?OrderByColumn=2&OrderDesc=True&ItemsOnPage=50&TerminalId=153950"

LAST_TIME_FILE = "last_time.txt"
CASH_FILE = "cash.txt"


def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        },
        timeout=30
    )


def load_last_time():
    if os.path.exists(LAST_TIME_FILE):
        with open(LAST_TIME_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_last_time(value):
    with open(LAST_TIME_FILE, "w", encoding="utf-8") as f:
        f.write(value)


def load_cash():
    today = datetime.now(
        ZoneInfo("Europe/Berlin")
    ).strftime("%d.%m.%Y")

    if not os.path.exists(CASH_FILE):
        return today, 0.0

    try:
        with open(CASH_FILE, "r", encoding="utf-8") as f:
            date_str, cash = f.read().split("|")
            cash = float(cash)

        if date_str != today:
            return today, 0.0

        return date_str, cash

    except:
        return today, 0.0


def save_cash(date_str, cash):
    with open(CASH_FILE, "w", encoding="utf-8") as f:
        f.write(f"{date_str}|{cash}")


def main():
    try:
        response = requests.get(
            URL,
            headers=HEADERS,
            timeout=30
        )

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr")

        if len(rows) < 2:
            print("Продажи не найдены")
            return

        last_time = load_last_time()

        current_date, current_cash = load_cash()

        new_sales = []

        for row in rows[1:]:
            cols = row.find_all("td")

            if len(cols) < 5:
                continue

            sale_time = cols[2].text.strip()

            if sale_time == last_time:
                break

            amount_text = (
                cols[4]
                .text
                .replace("₽", "")
                .replace(" ", "")
                .replace(",", ".")
                .strip()
            )

            try:
                amount = float(amount_text)
            except:
                continue

            new_sales.append((sale_time, amount))

        if not new_sales:
            print("Новых продаж нет")
            return

        new_sales.reverse()

        for sale_time, amount in new_sales:
            current_cash += amount

            message = (
                f"💰 <b>Новая продажа</b>\n\n"
                f"📅 {sale_time}\n"
                f"🛒 Сумма: <b>{int(amount)} ₽</b>\n"
                f"🏦 Касса сегодня: <b>{int(current_cash)} ₽</b>"
            )

            send_telegram(message)

        save_last_time(new_sales[-1][0])
        save_cash(current_date, current_cash)

        print(f"Обработано продаж: {len(new_sales)}")

    except Exception as e:
        print("Ошибка:", e)


if __name__ == "__main__":
    main()

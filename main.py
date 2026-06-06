import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
cookies = os.environ.get('COOKIE_PART1', '') + os.environ.get('COOKIE_PART2', '')
HEADERS = {"User-Agent": "Mozilla/5.0", "Cookie": cookies}
URL = "https://p.vendista.ru/Transactions/Search?OrderByColumn=2&OrderDesc=True&ItemsOnPage=5&TerminalId=153950"

def send_telegram(msg):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

def main():
    try:
        response = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        
        last_time_file = "last_time.txt"
        cash_file = "cash.txt"
        today = datetime.now().strftime("%d.%m")
        
        # Читаем данные
        last_time = ""
        if os.path.exists(last_time_file):
            with open(last_time_file, "r") as f: last_time = f.read().strip()
        
        current_date, current_cash = "00.00", 0.0
        if os.path.exists(cash_file):
            with open(cash_file, "r") as f:
                data = f.read().split('|')
                if len(data) == 2: current_date, current_cash = data[0], float(data[1])
        
        # Обнуление при смене даты
        if current_date != today:
            current_cash, current_date = 0.0, today

        first_row = rows[1]
        cols = first_row.find_all('td')
        
        full_date = cols[2].text.strip()
        amount_text = cols[4].text.replace('₽', '').replace(',', '.').strip()
        amount = float(amount_text)
        
        if full_date != last_time:
            current_cash += amount
            msg = (f"💰 <b>Продажа</b>\n"
                   f"📅 {full_date[0:5]} 🕑 {full_date[11:16]}\n"
                   f"🛒 <b>Сумма продажи:</b> {int(amount)} ₽\n\n"
                   f"🏦 <b>Касса:</b> {int(current_cash)} ₽")
            
            send_telegram(msg)
            
            with open(last_time_file, "w") as f: f.write(full_date)
            with open(cash_file, "w") as f: f.write(f"{current_date}|{current_cash}")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()

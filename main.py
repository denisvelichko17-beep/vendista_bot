import os
import requests
from bs4 import BeautifulSoup

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
        
        # Файлы для «памяти»
        last_time_file = "last_time.txt"
        cash_file = "cash.txt"
        
        last_time = ""
        if os.path.exists(last_time_file):
            with open(last_time_file, "r") as f: last_time = f.read().strip()
        
        current_cash = 0.0
        if os.path.exists(cash_file):
            with open(cash_file, "r") as f: current_cash = float(f.read().strip())

        # Читаем первую строку
        first_row = rows[1]
        cols = first_row.find_all('td')
        
        full_date = cols[2].text.strip() # 06.06.2026 17:42:30
        amount_text = cols[4].text.replace('₽', '').replace(',', '.').strip()
        amount = float(amount_text)
        
        # Форматируем дату для сообщения
        date_short = full_date[0:5] # 06.06
        time_short = full_date[11:16] # 17:42

        if full_date != last_time:
            current_cash += amount
            
            msg = (f"💰 <b>Продажа</b>\n"
                   f"📅 {date_short} 🕑 {time_short}\n"
                   f"🛒 <b>Сумма продажи:</b> {int(amount)} ₽\n\n"
                   f"🏦 <b>Касса:</b> {int(current_cash)} ₽")
            
            send_telegram(msg)
            
            # Сохраняем новые данные в файлы
            with open(last_time_file, "w") as f: f.write(full_date)
            with open(cash_file, "w") as f: f.write(str(current_cash))
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()

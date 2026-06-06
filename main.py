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
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')
    
    # Файл для хранения времени последней увиденной транзакции
    last_time_file = "last_time.txt"
    last_time = ""
    if os.path.exists(last_time_file):
        with open(last_time_file, "r") as f: last_time = f.read().strip()

    new_tx = []
    total_sum = 0
    
    # Парсим (настройте индексы cols, если время/сумма не в 1 и 3 столбце)
    for row in rows[1:6]:
        cols = row.find_all('td')
        if len(cols) > 3:
            time = cols[1].text.strip()
            # Берем сумму из вашей ячейки <td> 159,00 ₽ </td>
            amount_str = cols[3].text.replace('₽', '').replace(',', '.').strip()
            amount = float(amount_str)
            
            if time == last_time: break
            
            new_tx.append(f"🛒 <b>Сумма:</b> {amount} ₽")
            total_sum += amount

    if new_tx:
        # Обновляем время последней транзакции
        with open(last_time_file, "w") as f: f.write(rows[1].find_all('td')[1].text.strip())
        
        msg = f"💰 <b>Новая продажа!</b>\n📅 {datetime.now().strftime('%d.%m %H:%M')}\n\n" + "\n".join(new_tx)
        send_telegram(msg)

if __name__ == "__main__":
    main()

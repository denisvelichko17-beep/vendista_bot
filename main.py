import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
cookies = os.environ.get('COOKIE_PART1', '') + os.environ.get('COOKIE_PART2', '')

url = "https://p.vendista.ru/Transactions/Search?OrderByColumn=2&OrderDesc=True&ItemsOnPage=5&TerminalId=153950"

def send_telegram(message):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": message})

def main():
    headers = {"User-Agent": "Mozilla/5.0", "Cookie": cookies}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Здесь мы ищем таблицу с транзакциями
        rows = soup.find_all('tr') # Ищем строки таблицы
        
        results = []
        total_sum = 0
        
        # Проходим по первым 5 строкам (транзакциям)
        for row in rows[1:6]: 
            cols = row.find_all('td')
            if len(cols) > 3:
                date_time = cols[1].text.strip()
                amount = float(cols[3].text.replace(',', '.').replace(' руб.', ''))
                total_sum += amount
                results.append(f"{date_time} | {amount} руб.")
        
        msg = "Последние продажи:\n" + "\n".join(results) + f"\n\nИТОГ 5 стаканов: {total_sum} руб."
        send_telegram(msg)
    else:
        print(f"Ошибка: {response.status_code}")

if __name__ == "__main__":
    main()

import os
import requests
from bs4 import BeautifulSoup

# Получаем данные из секретов GitHub
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
cookies = os.environ.get('COOKIE_PART1', '') + os.environ.get('COOKIE_PART2', '')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Cookie": cookies
}

url = "https://p.vendista.ru/Transactions/Search?OrderByColumn=2&OrderDesc=True&ItemsOnPage=5&TerminalId=153950"

def send_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(telegram_url, data={"chat_id": CHAT_ID, "text": message})

def main():
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Ищем таблицу с транзакциями
            rows = soup.find_all('tr')
            
            results = []
            total_sum = 0
            
            # Берем последние 5 транзакций
            for row in rows[1:6]:
                cols = row.find_all('td')
                if len(cols) > 3:
                    date_time = cols[1].text.strip()
                    # Убираем лишнее, чтобы получить число
                    amount_text = cols[3].text.replace(',', '.').replace(' руб.', '').strip()
                    amount = float(amount_text) if amount_text else 0
                    total_sum += amount
                    results.append(f"{date_time} — {amount} руб.")
            
            msg = "📊 Последние 5 продаж:\n" + "\n".join(results) + f"\n\n💰 ИТОГ 5 стаканов: {total_sum} руб."
            send_telegram(msg)
        else:
            send_telegram(f"Ошибка доступа к Vendista: {response.status_code}")
    except Exception as e:
        send_telegram(f"Ошибка бота: {str(e)}")

if __name__ == "__main__":
    main()

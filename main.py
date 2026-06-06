import os
import requests

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
cookies = os.environ.get('COOKIE_PART1', '') + os.environ.get('COOKIE_PART2', '')

def send_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(telegram_url, data=payload)
    print(f"Ответ Telegram: {response.status_code}, {response.text}") # Это поможет увидеть ошибку

def main():
    if not TOKEN or not CHAT_ID:
        print("Ошибка: Токен или CHAT_ID не найдены в секретах!")
        return
        
    print("Проверка подключения к Vendista...")
    url = "https://p.vendista.ru/Transactions/Search?ItemsOnPage=5&TerminalId=153950"
    headers = {"User-Agent": "Mozilla/5.0", "Cookie": cookies}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Сайт ответил успешно!")
        send_telegram("Бот работает и проверил транзакции!")
    else:
        print(f"Ошибка Vendista: {response.status_code}")
        send_telegram(f"Ошибка Vendista: {response.status_code}")

if __name__ == "__main__":
    main()

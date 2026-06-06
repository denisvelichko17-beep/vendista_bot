import os
import requests
import json

# Настройки
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
cookies = os.environ.get('COOKIE_PART1', '') + os.environ.get('COOKIE_PART2', '')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Cookie": cookies
}

# Ссылка для получения транзакций
url = "https://p.vendista.ru/Transactions/Search?OrderByColumn=2&OrderDesc=True&ItemsOnPage=5&TerminalId=153950"

def send_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(telegram_url, data={"chat_id": CHAT_ID, "text": message})

def main():
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Здесь мы получаем ответ. 
            # Поскольку это HTML, мы просто проверяем, что запрос прошел.
            # Для продвинутой логики нужно использовать библиотеку BeautifulSoup.
            send_telegram("Бот успешно проверил наличие транзакций!")
        else:
            send_telegram(f"Ошибка доступа к Vendista: {response.status_code}")
    except Exception as e:
        send_telegram(f"Ошибка бота: {str(e)}")

if __name__ == "__main__":
    main()

import os
import requests

# Собираем куки из двух секретов
cookies = os.environ.get('COOKIE_PART1', '') + os.environ.get('COOKIE_PART2', '')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Cookie": cookies
}

url = "https://p.vendista.ru/Transactions/Search?OrderByColumn=2&OrderDesc=True&ItemsOnPage=50&TerminalId=153950"

def main():
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Успешно получили данные с Vendista!")
        else:
            print(f"Ошибка доступа: {response.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()

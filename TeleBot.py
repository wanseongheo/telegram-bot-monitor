import os
import requests

def send_telegram():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    text = "GitHub Actions 자동 실행 테스트 성공!"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    
    response = requests.get(url, params=params)
    print(response.json())

if __name__ == "__main__":
    send_telegram()

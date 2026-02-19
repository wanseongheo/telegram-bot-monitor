import requests

def send_telegram():
    # 직접 토큰과 ID를 입력 (따옴표 필수)
    token = "8197870608:AAHP9j9M2xBlVeiXsOYZJ82JzW5eQeJdTO8"
    chat_id = "-1003664951133" 
    
    text = "GitHub Actions 자동 실행 테스트 성공!"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    
    response = requests.get(url, params=params)
    print(response.json())

if __name__ == "__main__":
    send_telegram()

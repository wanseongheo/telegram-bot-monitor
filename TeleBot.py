import requests

def send_telegram():
    token = "8197870608:AAHP9j9M2xBlVeiXsOYZJ82JzW5eQeJdTO8"
    chat_id = "-1003664951133"  # 확인하신 숫자 입력
    text = "문법 오류 해결! 동기 방식으로 보낸 메시지입니다."
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        print("전송 성공!")
    else:
        print(f"오류 발생: {response.text}")

# 즉시 실행
if __name__ == "__main__":
    send_telegram()
import os
import requests
import fear_and_greed

def get_cnn_fng():
    """fear-and-greed 라이브러리를 사용하여 실제 CNN 지수를 가져옵니다."""
    try:
        # CNN에서 데이터를 긁어옵니다.
        index_data = fear_and_greed.get()
        
        # 정수 값으로 변환 (예: 42.5 -> 42)
        value = int(index_data.value)
        return value
    except Exception as e:
        print(f"CNN 데이터 가져오기 실패: {e}")
        return None

def get_status_message(value):
    """요청하신 4단계 구간별 메시지 설정"""
    if value <= 25:
        return f"{value} : 극단적 공포(패닉셀 주의)😱"
    elif value <= 50:
        return f"{value} : 공포😨"
    elif value <= 75:
        return f"{value} : 탐욕🤩"
    else:
        return f"{value} : 극단적 탐욕(과열주의)🤑"

def send_telegram():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # 1. 실제 CNN 인덱스 값 가져오기
    fng_value = get_cnn_fng()
    
    if fng_value is not None:
        # 2. 메시지 구성
        status_text = get_status_message(fng_value)
        text = f"📊 [CNN 공식] Fear & Greed Index\n\n{status_text}"
    else:
        text = "❌ CNN 데이터를 불러오는 데 실패했습니다. (라이브러리/사이트 확인 필요)"

    # 3. 텔레그램 전송
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # HTTP 에러 발생 시 예외 처리
        print("메시지 전송 성공!")
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

if __name__ == "__main__":
    send_telegram()

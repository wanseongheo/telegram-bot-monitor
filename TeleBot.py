import os
import requests
import fear_and_greed
import yfinance as yf  # VIX 데이터를 위해 추가

def get_cnn_fng():
    """fear-and-greed 라이브러리를 사용하여 실제 CNN 지수를 가져옵니다."""
    try:
        index_data = fear_and_greed.get()
        return int(index_data.value)
    except Exception as e:
        print(f"CNN 데이터 가져오기 실패: {e}")
        return None

def get_vix_index():
    """yfinance를 사용하여 CBOE Volatility Index (^VIX)를 가져옵니다."""
    try:
        vix = yf.Ticker("^VIX")
        # 가장 최근의 종가를 가져옵니다.
        vix_value = vix.history(period="1d")['Close'].iloc[-1]
        return round(vix_value, 2)
    except Exception as e:
        print(f"VIX 데이터 가져오기 실패: {e}")
        return None

def get_fng_status(value):
    """CNN 공포 탐욕 지수 메시지 구성"""
    if value <= 25: return f"{value} : 극단적 공포 (Extreme Fear) 😱"
    elif value <= 44: return f"{value} : 공포 (Fear) 😨"
    elif value <= 55: return f"{value} : 중립 (Neutral) 😐"
    elif value <= 75: return f"{value} : 탐욕 (Greed) 🤩"
    else: return f"{value} : 극단적 탐욕 (Extreme Greed) 🤑"

def get_vix_status(value):
    """VIX 지수 5단계 상태 메시지 구성"""
    if value >= 30:
        return f"{value} : 극단적 변동 (Extreme Volatility) 🌋 - 시장 패닉 상태"
    elif value >= 20:
        return f"{value} : 높은 변동 (High Volatility) ⚠️ - 불안정한 시장"
    elif value >= 15:
        return f"{value} : 보통 (Normal) ⚖️ - 일반적인 변동성"
    elif value >= 12:
        return f"{value} : 안정 (Stable) ✅ - 차분한 시장 분위기"
    else:
        return f"{value} : 극단적 안정 (Extremely Calm) 🧘 - 과도한 낙관 경계"

def send_telegram():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # 1. 데이터 가져오기
    fng_value = get_cnn_fng()
    vix_value = get_vix_index()
    
    # 2. 메시지 조립
    message_lines = ["📊 [시장 지표 요약]"]
    
    # F&G 섹션
    if fng_value is not None:
        message_lines.append(f"\n✅ Fear & Greed Index\n{get_fng_status(fng_value)}")
    else:
        message_lines.append("\n❌ CNN 데이터 로드 실패")
        
    # VIX 섹션
    if vix_value is not None:
        message_lines.append(f"\n✅ VIX Index (변동성 지수)\n{get_vix_status(vix_value)}")
    else:
        message_lines.append("\n❌ VIX 데이터 로드 실패")

    full_text = "\n".join(message_lines)

    # 3. 텔레그램 전송
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": full_text}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print("통합 메시지 전송 성공!")
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

if __name__ == "__main__":
    send_telegram()

import os
import requests
import fear_and_greed
import yfinance as yf
import pandas as pd  # RSI 계산을 위해 추가 (yfinance와 함께 자동 설치됨)

def get_cnn_fng():
    """CNN 공포 탐욕 지수 가져오기"""
    try:
        index_data = fear_and_greed.get()
        return int(index_data.value)
    except Exception as e:
        print(f"CNN 데이터 가져오기 실패: {e}")
        return None

def get_vix_index():
    """VIX 변동성 지수 가져오기"""
    try:
        vix = yf.Ticker("^VIX")
        vix_value = vix.history(period="1d")['Close'].iloc[-1]
        return round(vix_value, 2)
    except Exception as e:
        print(f"VIX 데이터 가져오기 실패: {e}")
        return None

def get_sp500_rsi():
    """S&P 500 (^GSPC)의 14일 RSI 지수 계산하기"""
    try:
        sp500 = yf.Ticker("^GSPC")
        # 14일 RSI를 구하기 위해 넉넉하게 최근 3개월 데이터를 불러옵니다.
        hist = sp500.history(period="3mo")
        delta = hist['Close'].diff()
        
        # 상승분과 하락분 분리
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        
        # 지수이동평균(EMA)을 활용한 14일 평균 계산 (Wilder's 방식)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        
        # 가장 최근(오늘)의 RSI 값을 반환
        return round(rsi.iloc[-1], 2)
    except Exception as e:
        print(f"RSI 데이터 가져오기 실패: {e}")
        return None

def get_fng_status(value):
    if value <= 20: return f"{value} : 극단적 공포 (Extreme Fear) 😱 - 패닉셀 주의 및 저점 매수 검토"
    elif value <= 40: return f"{value} : 공포 (Fear) 😨 - 부정적인 시장 심리"
    elif value <= 60: return f"{value} : 중립 (Neutral) 😐 - 방향 탐색 중인 관망 구간"
    elif value <= 80: return f"{value} : 탐욕 (Greed) 🤩 - 긍정적인 매수세 유입"
    else: return f"{value} : 극단적 탐욕 (Extreme Greed) 🤑 - 시장 과열, 분할 익절 고려"

def get_vix_status(value):
    if value >= 30: return f"{value} : 극단적 변동 (Extreme Volatility) 🌋 - 시장 패닉 상태"
    elif value >= 20: return f"{value} : 높은 변동 (High Volatility) ⚠️ - 불안정한 시장"
    elif value >= 15: return f"{value} : 보통 (Normal) ⚖️ - 일반적인 변동성"
    elif value >= 12: return f"{value} : 안정 (Stable) ✅ - 차분한 시장 분위기"
    else: return f"{value} : 극단적 안정 (Extremely Calm) 🧘 - 과도한 낙관 경계"

def get_rsi_status(value):
    """RSI 5단계 구간 상태 메시지 구성"""
    if value > 70:
        return f"{value} : 과매수 (Overbought) 🔥\n➡️ 단기 과열 상태입니다. 수익 실현 시점을 고려해 보세요."
    elif value >= 56:
        return f"{value} : 매수 (Buy) 📈\n➡️ 상승 모멘텀이 유지 중입니다. 추세에 편승해 볼 수 있습니다."
    elif value >= 46:
        return f"{value} : 중립 (Neutral) ⚖️\n➡️ 뚜렷한 방향성이 없는 횡보 구간입니다. 관망을 추천합니다."
    elif value >= 30:
        return f"{value} : 매도 (Sell) 📉\n➡️ 하락 압력이 강한 구간입니다. 리스크 관리에 신경 쓰세요."
    else: # value < 30
        return f"{value} : 과매도 (Oversold) ❄️\n➡️ 과도한 하락 상태입니다. 반등을 노린 저점 매수 기회를 탐색해 보세요."

def send_telegram():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # 1. 지표 데이터 가져오기
    fng_value = get_cnn_fng()
    vix_value = get_vix_index()
    rsi_value = get_sp500_rsi()
    
    # 2. 메시지 조립
    message_lines = ["📊 [Daily 시장 지표 요약]"]
    
    # F&G 섹션
    if fng_value is not None:
        message_lines.append(f"\n1️⃣ Fear & Greed Index\n{get_fng_status(fng_value)}")
    else:
        message_lines.append("\n1️⃣ Fear & Greed Index: 로드 실패 ❌")
        
    # VIX 섹션
    if vix_value is not None:
        message_lines.append(f"\n2️⃣ VIX Index (변동성)\n{get_vix_status(vix_value)}")
    else:
        message_lines.append("\n2️⃣ VIX Index: 로드 실패 ❌")

    # RSI 섹션
    if rsi_value is not None:
        message_lines.append(f"\n3️⃣ S&P 500 RSI(14)\n{get_rsi_status(rsi_value)}")
    else:
        message_lines.append("\n3️⃣ S&P 500 RSI: 로드 실패 ❌")

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

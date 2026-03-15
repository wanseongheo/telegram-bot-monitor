import os
import requests
import fear_and_greed
import yfinance as yf
import pandas as pd

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
        hist = sp500.history(period="3mo")
        delta = hist['Close'].diff()
        
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi.iloc[-1], 2)
    except Exception as e:
        print(f"RSI 데이터 가져오기 실패: {e}")
        return None

# 🌟 숫자 시인성 강화 (백틱 ` 은 숫자 강조, 별표 * 는 굵게)
def get_fng_status(value):
    if value <= 24: return f"`{value}` : *극단적 공포 (Extreme Fear)* 😱"
    elif value <= 44: return f"`{value}` : *공포 (Fear)* 😨"
    elif value <= 55: return f"`{value}` : *중립 (Neutral)* 😐"
    elif value <= 75: return f"`{value}` : *탐욕 (Greed)* 🤩"
    else: return f"`{value}` : *극단적 탐욕 (Extreme Greed)* 🤑"

def get_vix_status(value):
    if value >= 30: return f"`{value}` : *극단적 변동 (Extreme Volatility)* 🌋"
    elif value >= 20: return f"`{value}` : *높은 변동 (High Volatility)* ⚠️"
    elif value >= 15: return f"`{value}` : *보통 (Normal)* ⚖️"
    elif value >= 12: return f"`{value}` : *안정 (Stable)* ✅"
    else: return f"`{value}` : *극단적 안정 (Extremely Calm)* 🧘"

def get_rsi_status(value):
    if value > 70: return f"`{value}` : *과매수 (Overbought)* 🔥"
    elif value >= 56: return f"`{value}` : *매수 (Buy)* 📈"
    elif value >= 46: return f"`{value}` : *중립 (Neutral)* ⚖️"
    elif value >= 30: return f"`{value}` : *매도 (Sell)* 📉"
    else: return f"`{value}` : *과매도 (Oversold)* ❄️"

def analyze_investment_stance(fng, vix, rsi):
    """3가지 지표를 종합하여 투자 스탠스 및 괴리 해석을 제공"""
    if fng is None or vix is None or rsi is None:
        return "⚠️ 데이터 누락으로 종합 분석을 수행할 수 없습니다."

    if fng <= 25 and vix >= 30 and rsi <= 30:
        return "🟢 *[최고의 매수 기회 (Capitulation)]*\n시장의 항복이 일어났습니다. 적극 매수를 고려하세요."
    elif 25 < fng <= 44 and 20 <= vix < 30 and 30 < rsi <= 50:
        return "🟡 *[조정 국면 진입 (Correction)]*\n하방 위험을 열어두고 분할 매수로 접근하세요."
    elif 45 <= fng <= 55 and 15 <= vix < 20 and 45 <= rsi <= 55:
        return "⚪ *[정상적 추세 (Normal)]*\n시장이 안정적입니다. 비중을 유지하세요."
    elif 56 <= fng <= 75 and 12 <= vix < 15 and 50 < rsi <= 70:
        return "🟠 *[과열 주의 (Overheating)]*\n수익을 확정 짓기 시작하며 현금 비중을 높이세요."
    elif fng > 75 and vix < 12 and rsi > 70:
        return "🔴 *[최고의 매도 기회 (Euphoria)]*\n광기의 고점입니다! 차익 실현에 집중하세요."

    # 지표 괴리 해석
    if fng <= 40 and vix < 18:
        return "⚠️ *[지표 괴리: 섣부른 바닥론 경계]*\n심리는 공포지만 변동성은 낮습니다. 추가 투매를 경계하세요."
    elif rsi <= 55 and fng >= 60:
        return "⚠️ *[지표 괴리: 불안한 과열]*\n심리만 과열된 상태일 수 있으니 신규 진입에 신중하세요."
    
    return "⚖️ *[지표 혼조세 / 리스크 관리]*\n방향성이 불분명하므로 확인 후 대응하세요."

def send_telegram():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    fng_value = get_cnn_fng()
    vix_value = get_vix_index()
    rsi_value = get_sp500_rsi()
    
    # 리스트 생성 시 모든 요소를 문자열로 관리 (TypeError 방지)
    message_lines = [
        "📊 *[Daily 시장 지표 & 투자 가이드]*",
        "_💡 변동성[VIX]범위: 12안정, 15보통, 20변동, 30극단적변동_",
        "------------------------------"
    ]
    
    message_lines.append(f"1️⃣ F&G 심리: {get_fng_status(fng_value) if fng_value is not None else '로드 실패 ❌'}")
    message_lines.append(f"2️⃣ VIX 변동: {get_vix_status(vix_value) if vix_value is not None else '로드 실패 ❌'}")
    message_lines.append(f"3️⃣ RSI(14) : {get_rsi_status(rsi_value) if rsi_value is not None else '로드 실패 ❌'}")
    message_lines.append("------------------------------")

    stance_message = analyze_investment_stance(fng_value, vix_value, rsi_value)
    message_lines.append("🤖 *[투자 파트너의 스탠스 제안]*")
    message_lines.append(stance_message)

    full_text = "\n".join(message_lines)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # parse_mode를 Markdown으로 설정해야 스타일이 적용됩니다.
    params = {
        "chat_id": chat_id, 
        "text": full_text, 
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print("통합 메시지 전송 성공!")
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

if __name__ == "__main__":
    send_telegram()

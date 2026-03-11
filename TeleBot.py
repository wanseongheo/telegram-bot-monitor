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

# 🌟 수정된 부분: 지표별 짧은 상태 평가 내용(코멘트) 복구
def get_fng_status(value):
    if value <= 24: return f"'{value}' : 극단적 공포 (Extreme Fear) 😱 - 패닉셀 주의 및 저점 매수 검토"
    elif value <= 44: return f"'{value}' : 공포 (Fear) 😨 - 부정적인 시장 심리"
    elif value <= 55: return f"'{value}'': 중립 (Neutral) 😐 - 방향 탐색 중인 관망 구간"
    elif value <= 75: return f"'{value}' : 탐욕 (Greed) 🤩 - 긍정적인 매수세 유입"
    else: return f"{value} : 극단적 탐욕 (Extreme Greed) 🤑 - 시장 과열, 분할 익절 고려"

def get_vix_status(value):
    if value >= 30: return f"'{value}' : 극단적 변동 (Extreme Volatility) 🌋 - 시장 패닉 상태"
    elif value >= 20: return f"'{value}' : 높은 변동 (High Volatility) ⚠️ - 불안정한 시장"
    elif value >= 15: return f"'{value}' : 보통 (Normal) ⚖️ - 일반적인 변동성"
    elif value >= 12: return f"'{value}' : 안정 (Stable) ✅ - 차분한 시장 분위기"
    else: return f"'{value}' : 극단적 안정 (Extremely Calm) 🧘 - 과도한 낙관 경계"

def get_rsi_status(value):
    if value > 70: return f"'{value}' : 과매수 (Overbought) 🔥 - 단기 과열 상태 (수익 실현 고려)"
    elif value >= 56: return f"'{value}' : 매수 (Buy) 📈 - 상승 모멘텀 유지"
    elif value >= 46: return f"'{value}' : 중립 (Neutral) ⚖️ - 뚜렷한 방향성이 없는 횡보 구간"
    elif value >= 30: return f"'{value}' : 매도 (Sell) 📉 - 하락 압력이 강한 구간"
    else: return f"'{value}' : 과매도 (Oversold) ❄️ - 과도한 하락 상태 (반등 탐색)"

def analyze_investment_stance(fng, vix, rsi):
    """3가지 지표를 종합하여 투자 스탠스 및 괴리 해석을 제공"""
    if fng is None or vix is None or rsi is None:
        return "⚠️ 데이터 누락으로 종합 분석을 수행할 수 없습니다."

    # 1. 명확한 종합 시장 국면 (완벽히 일치하는 경우)
    if fng <= 25 and vix >= 30 and rsi <= 30:
        return "🟢 [최고의 매수 기회 (Capitulation)]\n시장의 항복이 일어났습니다. 우량 자산을 헐값에 매수할 기회! 현금 비중을 최소화하고 적극 매수를 고려하세요."
    elif 25 < fng <= 44 and 20 <= vix < 30 and 30 < rsi <= 50:
        return "🟡 [조정 국면 진입 (Correction)]\n하방 위험을 열어두고 지지선을 확인하며 분할 매수로 보수적으로 접근하세요."
    elif 45 <= fng <= 55 and 15 <= vix < 20 and 45 <= rsi <= 55:
        return "⚪ [정상적 추세 (Normal)]\n시장이 안정적입니다. 포트폴리오 비중을 규칙에 따라 유지하세요."
    elif 56 <= fng <= 75 and 12 <= vix < 15 and 50 < rsi <= 70:
        return "🟠 [과열 주의 (Overheating)]\n수익을 확정 짓기 시작하며 현금 비중을 점진적으로 높이세요."
    elif fng > 75 and vix < 12 and rsi > 70:
        return "🔴 [최고의 매도 기회 (Euphoria)]\n시장의 광기가 고점입니다! 보수적 방어 및 차익 실현에 집중하세요."

    # 2. 지표 간 괴리 (Divergence) 발생 시 특별 해석
    if fng <= 40 and vix < 18:
        return "⚠️ [지표 괴리: 섣부른 바닥론 경계]\n심리는 '공포'지만 실제 변동성(VIX)은 안정적입니다.\n시장이 늪처럼 서서히 하락하는 구간일 수 있으며, 아직 '진짜 투매(바닥)'가 나오지 않았을 확률이 높습니다. 관망을 권장합니다."
    elif rsi <= 55 and fng >= 60:
        return "⚠️ [지표 괴리: 불안한 과열]\n가격(RSI)상 크게 비싸지 않은 구간이나, 투자자들의 심리(F&G)는 이미 탐욕에 차 있습니다.\n추가 상승 여력이 크지 않은 '데드캣 바운스'나 억지 상승장일 수 있으니 신규 진입은 신중하세요."
    elif rsi <= 45 and vix >= 25:
        return "⚠️ [지표 괴리: 떨어지는 칼날]\n기술적 지표(RSI)는 매수 구간을 가리키지만, 변동성(VIX)이 급등하고 있습니다.\n강력한 하락 압력이 진행 중이니 VIX가 진정될 때까지 절대 매수를 보류하세요."

    # 3. 그 외 애매한 혼조세
    else:
        return "⚖️ [지표 혼조세 / 다수결 리스크 관리]\n지표들이 서로 엇갈린 신호를 보내고 있습니다. 시장이 방향을 정하지 못했으므로, 투자 비중을 평소의 50% 이하로 축소하고 확인 후 대응하세요."

def send_telegram():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # 1. 지표 데이터 가져오기
    fng_value = get_cnn_fng()
    vix_value = get_vix_index()
    rsi_value = get_sp500_rsi()
    
    # 2. 메시지 조립
    message_lines = ["📊 [Daily 시장 지표 & 투자 가이드]"]
    message_lines = ["변동성[VIX]범위: 12안정, 15보통, 20변동, 30극단적변동"]
    message_lines.append("-" * 30)
    
    # 각 지표 상태 요약
    message_lines.append(f"1️⃣ F&G 심리: {get_fng_status(fng_value) if fng_value is not None else '로드 실패 ❌'}")
    message_lines.append(f"2️⃣ VIX 변동: {get_vix_status(vix_value) if vix_value is not None else '로드 실패 ❌'}")
    message_lines.append(f"3️⃣ RSI(14) : {get_rsi_status(rsi_value) if rsi_value is not None else '로드 실패 ❌'}")
    message_lines.append("-" * 30)

    # 🌟 스탠스 분석 (핵심 추가 파트)
    stance_message = analyze_investment_stance(fng_value, vix_value, rsi_value)
    message_lines.append("🤖 [투자 파트너의 스탠스 제안]")
    message_lines.append(stance_message)

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


import yfinance as yf
import pandas_ta as ta
import telegram
import asyncio
import os

# 1. 설정 (환경 변수)
TOKEN = os.environ.get('TELEGRAM_stockprice_bot_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 알림 종목 리스트
STOCKS = ['GOOGL', 'TSLA', 'NVDA', 'BRKB', 'PWR', 'VOO', 'JEPI'] 

async def send_stock_update():
    bot = telegram.Bot(token=TOKEN)
    message = "🔔 **오늘의 종목 실시간 리포트**\n\n"
    
    for ticker in STOCKS:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1mo")
            
            if df.empty:
                continue

            current_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # RSI(14) 계산
            df['RSI'] = ta.rsi(df['Close'], length=14)
            rsi_value = df['RSI'].iloc[-1]

            # --- [개선 포인트: 시각성 강화 로직] ---
            if change_pct > 0:
                status_emoji = "🔴 🔺"  # 상승 시 빨간색 원과 위쪽 삼각형
            elif change_pct < 0:
                status_emoji = "🔵 ⬇️"  # 하락 시 파란색 원과 아래쪽 화살표
            else:
                status_emoji = "⚪ ➖"  # 보합 시 회색
            
            # RSI 가이드 로직
            if rsi_value >= 70:
                rsi_guide = "⚠️ *[과매수]* - 조정 가능성 주의"
            elif rsi_value <= 30:
                rsi_guide = "🔵 *[과매도]* - 기술적 반등 기회"
            else:
                rsi_guide = "⚪ *[보통]* - 안정적 흐름"
            # ---------------------------------------

            # 메시지 포맷팅
            message += f"{status_emoji} **{ticker}**\n"
            message += f" └ 현재가: {current_price:,.2f}\n"
            message += f" └ 변화율: {change_pct:+.2f}%\n"
            message += f" └ RSI(14): {rsi_value:.2f}\n"
            message += f" └ **진단: {rsi_guide}**\n\n"
            
        except Exception as e:
            message += f"❌ {ticker}: 분석 오류 ({e})\n\n"

    # 메시지 전송
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_stock_update())

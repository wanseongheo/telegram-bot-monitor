import yfinance as yf
import pandas_ta as ta
import telegram
import asyncio
import os

# 1. 설정 (환경 변수)
TOKEN = os.environ.get('TELEGRAM_stockprice_bot_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 알림을 받고 싶은 종목 리스트
STOCKS = ['GOOGL', 'TSLA', 'NVDA', 'BRKB', 'PWR', 'VOO'] 

async def send_stock_update():
    bot = telegram.Bot(token=TOKEN)
    message = "🔔 **오늘의 종목 기술적 지표 리포트**\n\n"
    
    for ticker in STOCKS:
        try:
            # RSI 계산을 위해 1개월치 데이터 호출
            stock = yf.Ticker(ticker)
            df = stock.history(period="1mo")
            
            if df.empty:
                continue

            # 1. 가격 및 변화율 계산
            current_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # 2. RSI(14) 계산
            df['RSI'] = ta.rsi(df['Close'], length=14)
            rsi_value = df['RSI'].iloc[-1]

            # 3. 과매수/과매도 가이드 로직
            rsi_guide = ""
            if rsi_value >= 70:
                rsi_guide = "⚠️ *[과매수]* - 주의: 에너지가 과열되어 주가가 조정받을 가능성이 높습니다."
            elif rsi_value <= 30:
                rsi_guide = "🔵 *[과매도]* - 기회: 과하게 하락하여 기술적 반등이 나올 가능성이 있습니다."
            else:
                rsi_guide = "⚪ *[보통]* - 현재 안정적인 흐름을 보이고 있습니다."
            
            # 4. 메시지 포맷팅 (가독성 강화)
            change_emoji = "🔺" if change_pct > 0 else "🔻"
            message += f"{change_emoji} **{ticker}**\n"
            message += f" └ 현재가: {current_price:,.2f}\n"
            message += f" └ 변화율: {change_pct:+.2f}%\n"
            message += f" └ RSI(14): {rsi_value:.2f}\n"
            message += f" └ **진단: {rsi_guide}**\n\n"
            
        except Exception as e:
            message += f"❌ {ticker}: 분석 중 오류 발생 ({e})\n\n"

    # 메시지 전송
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    asyncio.run(send_stock_update())

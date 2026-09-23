import ccxt, asyncio, time, os
import google.generativeai as genai
from telegram import Bot
BINANCE_KEY=os.getenv("VPdMCjArmaRtvlJyvArIaz2ZnqqWMcZ7sKuQbQsm4zX8BXR0biiW1fiaGuvVj1dV",""); BINANCE_SECRET=os.getenv("SLPJzh2UD8XAJdwgkcTnOjQKaYgzwx Rt4OkXxupqe8qQBgU0hAYL0KJlVTGh3AB","")
BYBIT_KEY=os.getenv("BZJaXO5lBk3z7KzWBv",""); BYBIT_SECRET=os.getenv("hY3eToJFgIwMiG0CrDkMPFBSeh6g2ccShctN","")
GEMINI_KEY=os.getenv("AQ.Ab8RN6LbqWUfva4hEJmqO4NGqSzxHneg0gskmPsd_7BFeSbbUQ",""); TELEGRAM_TOKEN=os.getenv("8913440819:AAH8ibRL4-NZM3W2d-bofALpuUeIoSoXJ_0",""); TELEGRAM_CHAT_ID=os.getenv("8913440819","")
genai.configure(api_key= )
gemini=genai.GenerativeModel('gemini-2.0-flash-lite')
bot=Bot(token= )
binance=ccxt.binance({'apiKey':VPdMCjArmaRtvlJyvArIaz2ZnqqWMcZ7sKuQbQsm4zX8BXR0biiW1fiaGuvVj1dV,'secret':SLPJzh2UD8XAJdwgkcTnOjQKaYgzwxvRt4OkXxupqe8qQBgU0hAYL0KJlVTGh3AB,'enableRateLimit':True})
bybit=ccxt.bybit({'apiKey':BZJaXO5lBk3z7KzWBv,'secret':hY3eToJFgIwMiG0CrDkMPFBSeh6g2ccShctN,'enableRateLimit':True})
avg_cache={}
def get_wall(sym, cur):
    avg=avg_cache.get(sym,cur)
    avg_cache[sym]=avg*0.9+cur*0.1 if avg else cur
    return cur>avg_cache[sym]*8
def red_team(ob,tr):
    bids=ob['bids']; asks=ob['asks']
    if not bids or not asks: return False,""
    bid_vol=sum(b[1] for b in bids[:10])
    if bid_vol<500: return False,"Low"
    spread=(asks[0][0]-bids[0][0])/bids[0][0]*100
    if spread>1.5: return False,"Spread"
    buy=sum(t['amount'] for t in tr[-20:] if t['side']=='buy'); sell=sum(t['amount'] for t in tr[-20:] if t['side']=='sell')
    is_wall=get_wall("W",asks[0][1] if asks[0][1]>bids[0][1] else bids[0][1])
    score=10+(40 if is_wall else 0)+(20 if bid_vol>sum(a[1] for a in asks[:10])*2.5 else 0)+(20 if buy>sell*1.5 else 0)+(10 if spread<0.3 else 0)
    return score>=91 and is_wall,f"Score {score}% Wall {asks[0][1]:.0f}"
async def main():
    await bot.send_message(TELEGRAM_CHAT_ID,"✅ V4.4 ONLINE\n750 Alts | Avg*8 Wall | 91%")
    b=list(binance.load_markets().keys()); y=list(bybit.load_markets().keys())
    b_u=[s for s in b if '/USDT' in s][:400]; y_u=[s for s in y if '/USDT' in s][:350]
    uni=list(set(b_u+y_u))[:750]; active=[]; w_age={}
    while True:
        for sym in uni:
            try:
                ex=binance if sym in b_u else bybit
                tk=ex.fetch_ticker(sym)
                if tk['quoteVolume'] and tk['quoteVolume']>3000000 and sym not in active:
                    active.append(sym)
                    if len(active)>30: active.pop(0)
            except: pass
        for sym in active[:]:
            try:
                ex=binance if sym in b_u else bybit
                ob=ex.fetch_order_book(sym,20); tr=ex.fetch_trades(sym,30)
                key=sym+"_w"
                if ob['asks'][0][1]>1000:
                    if key not in w_age: w_age[key]=time.time()
                else: w_age.pop(key,None); continue
                if time.time()-w_age.get(key,0)<5: continue
                passed,reason=red_team(ob,tr)
                if passed:
                    ai=gemini.generate_content(f"{sym} {reason}. Give sniper entry SL TP RR 1:3 1 line").text
                    await bot.send_message(TELEGRAM_CHAT_ID,f"🚀 V4.4 {sym}\n{reason}\n{ai}\nEx:{ex.id}")
                    await asyncio.sleep(8)
            except: pass
        await asyncio.sleep(30)
asyncio.run(main())

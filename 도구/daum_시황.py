#!/usr/bin/env python3
"""다음금융 API로 시황·보유종목·후보 종목 가격을 한 번에 조회해요. 사용: python3 도구/daum_시황.py [코드...]"""
import json, sys, urllib.request

H = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.daum.net/domestic"}
def get(path):
    req = urllib.request.Request("https://finance.daum.net" + path, headers=H)
    return json.load(urllib.request.urlopen(req, timeout=20))

def eok(x): return f"{x/1e8:,.0f}억"
def idx(market):
    d = get(f"/api/market_index/days?market={market}&perPage=2&pagination=true&page=1")["data"][0]
    sign = 1 if d["change"] == "RISE" else (-1 if d["change"] == "FALL" else 0)
    pct = sign * abs(d["changePrice"]) / (d["tradePrice"] - sign * abs(d["changePrice"])) * 100
    print(f"{market} {d['tradePrice']:,.2f} ({pct:+.2f}%) | 개인 {eok(d['individualStraightPurchasePrice'])} 외국인 {eok(d['foreignStraightPurchasePrice'])} 기관 {eok(d['institutionStraightPurchasePrice'])}")

WATCH = {"A004170":"신세계 (보유)","A133690":"TIGER 미국나스닥100 (보유)","A069500":"KODEX 200","A005930":"삼성전자","A000660":"SK하이닉스","A069960":"현대백화점","A023530":"롯데쇼핑"}
codes = sys.argv[1:] or list(WATCH)
print("== 지수 =="); idx("KOSPI"); idx("KOSDAQ")
print("== 종목 ==")
for c in codes:
    c = c if c.startswith("A") else "A" + c
    try:
        q = get(f"/api/quotes/{c}")
        print(f"{WATCH.get(c, q.get('name',''))}: {q['tradePrice']:,.0f}원 ({q['changeRate']*100:+.2f}%) 전일 {q['prevClosingPrice']:,.0f} 시 {q['openingPrice']:,.0f} 고 {q['highPrice']:,.0f} 저 {q['lowPrice']:,.0f}")
    except Exception as e:
        print(c, "조회 실패:", e)

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 21:51:51 2021

@author: dobbyjang0
"""
import bs4
import requests
import time

IMG_URL_BASE = "https://ssl.pstatic.net/imgfinance/chart/item/area/day/%s.png?sidcode=%d"
MAIN_URL_BASE = "https://finance.naver.com/item/main.nhn?code="
SISE_URL_BASE = "https://finance.naver.com/item/sise.nhn?code=%s#"


class StockInfo:
    def __init__(self):
        self.name = "테스트" #주식명
        self.code = "000000" #주식코드
        self.price = "0" #현재가
        self.compared_price= "-0" #전일대비
        self.rate="+0.00%" #등락률
        self.volume = "0" #거래량(천주)
        self.transaction_price = "0" #거래대금(백만)
        self.high_price= "0" #장중고가
        self.low_price= "0" #장중저가
        self.chart_url="https://cdn.discordapp.com/attachments/804815694717911080/805011065950830592/error-image-generic.png"
        #차트 이미지 url
        self.naver_url="https://finance.naver.com/" #네이버 증권 url
    
    def __str__(self):
        strInfo = (f"주식명 : {self.name}\n"+
                   f"주식코드 : {self.code}\n"+
                   f"현재가 : {self.price}\n"+
                   f"전일대비 : {self.compared_price}\n"+
                   f"등락률 : {self.rate}\n"+
                   f"거래량(천주) : {self.volume}\n"+
                   f"거래대금(백만) : {self.transaction_price}\n"+
                   f"장중고가 : {self.high_price}\n"+
                   f"장중저가 : {self.low_price}\n"+
                   f"차트 이미지 url : {self.chart_url}\n"+
                   f"네이버 증권 url : {self.naver_url}\n")
                   
        return strInfo
    
    def get_stock(self, input_code):
        global IMG_URL_BASE, MAIN_URL_BASE, SISE_URL_BASE
        
        code = f"{input_code:0>6}"
        
        if code=="000000" or len(code) != 6:
            return
        
        self.code = code
        
        sise_url = SISE_URL_BASE % self.code
        main_url = MAIN_URL_BASE + self.code
        img_url = IMG_URL_BASE % ( self.code, int(time.time()*1000//1))
        
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }
        html = session.get(sise_url, headers=headers).content
        bs = bs4.BeautifulSoup(html, 'lxml')
        
        #주식명
        self.name = bs.find("div", {"class": "wrap_company"}).find("h2").get_text(strip=True)
        
        info_table = bs.find("table", {"class": "type2 type_tax"})
        
        #현재가
        self.price = info_table.find("strong", {"id":"_nowVal"}).get_text(strip=True)
        
        #전일대비
        compared_price_soup_list = info_table.find("strong", {"id":"_diff"}).find_all("span")
        sign_base = compared_price_soup_list[0].get_text(strip=True)
        
        if sign_base == "상승":
            compared_price_sign= "▲"
        elif sign_base == "하락":
            compared_price_sign= "▼"
        else:
            compared_price_sign= "-"

        compared_price_value = compared_price_soup_list[1].get_text(strip=True)
        
        self.compared_price = compared_price_sign + compared_price_value
        
        #등락률
        self.rate = info_table.find("strong", {"id":"_rate"}).get_text(strip=True)
        
        #거래량(천주)
        self.volume = info_table.find("span", {"id":"_quant"}).get_text(strip=True)
        
        #거래대금(백만)
        self.transaction_price = info_table.find("span", {"id":"_amount"}).get_text(strip=True)
        
        #장중고가
        self.high_price = info_table.find("span", {"id":"_high"}).get_text(strip=True)
        
        #장중저가
        self.low_price = info_table.find("span", {"id":"_low"}).get_text(strip=True)
        
        #차트 이미지 url
        self.chart_url = img_url
        
        #네이버 증권 url
        self.naver_url = main_url
        
        
hello=StockInfo()
hello.get_stock("192250")
#print(hello)
print("stock.py 불러오기 완료")

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 21:51:51 2021

@author: dobbyjang0
"""
import bs4
import requests
import time

#싱글톤 세션
class Session():
    def __new__(cls):
        if not hasattr(cls, 'session'):
            cls.session = requests.Session()
            
        return cls.session
    
#싱글톤 헤더
class Headers():
    def __new__(cls):
        if not hasattr(cls, 'headers'):
            cls.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }
            
        return cls.headers

class InfoBase:
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
        #차트 이미지 urlg
        self.naver_url="https://finance.naver.com/" #네이버 증권 url
        #main과의 연관성이 너무 많다. 증권사 api 쓸줄 알게 되면 갈아치울것
        self.market=None
    
    def change_graph_interval(self, interval_type):
        pass
    
    def get(self):
        pass
    
    def to_dict(self):
        return self.__dict__
    
    def __str__(self):
        return str(self.__dict__)

class StockInfo(InfoBase):
    def get(self, input_code):
        IMG_URL_BASE = "https://ssl.pstatic.net/imgfinance/chart/item/area/day/%s.png?sidcode=%d"
        MAIN_URL_BASE = "https://finance.naver.com/item/main.nhn?code="
        SISE_URL_BASE = "https://finance.naver.com/item/sise.nhn?code=%s#"
        
        if len(input_code) < 6:
            code = f"{input_code:0>6}"
        else:
            code = input_code
        
        if code=="000000":
            return
        
        self.code = code
        
        sise_url = SISE_URL_BASE % self.code
        main_url = MAIN_URL_BASE + self.code
        img_url = IMG_URL_BASE % ( self.code, int(time.time()*1000//1))
        
        html = Session().get(sise_url, headers=Headers()).content
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
        
    def change_graph_interval(self, interval_type):
        type_dic = {"일":"area/day", "주":"area/week", "월":"area/month3", "년":"area/year",
                    "3년":"area/year3", "5년":"area/year5", "10년":"area/year10",
                    "일봉":"candle/day", "주봉":"candle/week", "월봉":"candle/month"
                    }
        type_url = type_dic.get(interval_type)
        
        if type_url is None:
            print("오류")
            return
        else:
            self.chart_url = self.chart_url.replace("area/day", type_url)
            return

#코스피, 코스닥
class KOSInfo(InfoBase):
    def get(self, index_name):
        
        if index_name not in ["KOSPI", "KOSDAQ"]:
            print("올바른 지수입력이 아님")
            return
        else:
            self.name = index_name
        
        
        KOS_URL = f"https://finance.naver.com/sise/sise_index.nhn?code={index_name}"
        KOS_IMG_URL = f"https://ssl.pstatic.net/imgfinance/chart/sise/siseMain{index_name}.png?sid=%s"
        
        html = Session().get(KOS_URL, headers=Headers()).content
        bs = bs4.BeautifulSoup(html, 'lxml')
        
        info_table = bs.find("div", {"class": "subtop_sise_detail"})
        
        #현재가
        self.price = info_table.find("em", {"id":"now_value"}).get_text(strip=True)
        
        #전일대비
        change_value_and_rate = info_table.find("span", {"id":"change_value_and_rate"}).get_text().split()
        sign_base = change_value_and_rate[1][-2:]
        
        if sign_base == "상승":
            compared_price_sign= "▲"
        elif sign_base == "하락":
            compared_price_sign= "▼"
        else:
            compared_price_sign= "-"
        
        compared_price_value = change_value_and_rate[0]
        
        self.compared_price = compared_price_sign + compared_price_value
        
        #등락률
        self.rate = change_value_and_rate[1][:-2]
        
        #거래량(천주)
        self.volume = info_table.find("td", {"id":"quant"}).get_text(strip=True)
        
        #거래대금(백만)
        self.transaction_price = info_table.find("td", {"id":"amount"}).get_text(strip=True)
        
        #장중고가
        self.high_price = info_table.find("td", {"id":"high_value"}).get_text(strip=True)
        
        #장중저가
        self.low_price = info_table.find("td", {"id":"low_value"}).get_text(strip=True)
        
        #차트 이미지 url
        self.chart_url = KOS_IMG_URL % int(time.time()*1000//1)
        
        #네이버 증권 url
        self.naver_url = KOS_URL
        
    def change_graph_interval(self, interval_type):
        BASE_URL = f"https://ssl.pstatic.net/imgstock/chart3/day/{self.name}.png?sidcode=%s" % int(time.time()*1000//1)
        
        type_dic = {"일":"day", "월":"day90", "년":"day365", "3년":"day1095"}
        
        print(interval_type)
        type_url = type_dic.get(interval_type)
        
        if type_url is None:
            print("오류")
            return
        else:
            self.chart_url = BASE_URL.replace("day", type_url)
            return


def main():
    #체크용
    if __name__ == "__main__":
        print("메인으로 실행")
        
        hello=KOSInfo()
        hello.get("KOSDAQ")
        hello.change_graph_interval("년")
        print(hello)
        

main()
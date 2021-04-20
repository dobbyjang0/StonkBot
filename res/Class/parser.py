import bs4
import requests
import time

# bs가 None 값이어도 에러가 일어나지 않게 함
def text_safety(bs):
    if bs is None:
        return ''
    else:
        return bs.get_text(strip=True)
    
def text_safety_to_float(bs):
    if bs is None:
        return ''
    else:
        return float(bs.get_text(strip=True).replace(',',''))

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
        self.name = None #주식명
        self.code = "000000" #주식코드
        self.price = 0 #현재가
        self.compared_price= "-0" #전일대비
        self.compared_sign = 0
        self.rate = 0
        self.start_price = 0
        self.high_price= 0 #장중고가
        self.low_price= 0 #장중저가
    
    def get(self):
        pass
    
    def to_dict(self):
        return self.__dict__
    
    def __str__(self):
        return str(self.__dict__)

class StockInfo(InfoBase):
    def get(self, input_code):
        SISE_URL_BASE = "https://finance.naver.com/item/sise.nhn?code=%s#"
        
        if len(input_code) < 6:
            code = f"{input_code:0>6}"
        else:
            code = input_code
        
        if code=="000000":
            return
        
        self.code = code
        
        sise_url = SISE_URL_BASE % self.code

        
        html = Session().get(sise_url, headers=Headers()).content
        bs = bs4.BeautifulSoup(html, 'lxml')
        
        info_table = bs.find("table", {"class": "type2 type_tax"})
        
        #현재가
        self.price = text_safety(info_table.find("strong", {"id":"_nowVal"}))
        

#해외 지수
class IndexInfo(InfoBase):
    def get(self, index_name):
        index_dic = {'다우':('다우존스','DJI@DJI', 'DJI'), 
                     '미국':('다우존스','DJI@DJI', 'DJI'), 
                     '나스닥':('나스닥 종합', 'NAS@IXIC', 'IXIC'),
                     'S&P':('S&P 500', 'SPI@SPX', 'IXIC'),
                     '니케이':('니케이225', 'NII@NI225', 'N225'),
                     '일본':('니케이225', 'NII@NI225', 'N225'),
                     '상해':('상해종합', 'SHS@000001', 'SSEC'),
                     '중국':('상해종합', 'SHS@000001', 'SSEC'),
                     '항셍':('항셍', 'HSI@HSI', 'HSI'),
                     '홍콩':('항셍', 'HSI@HSI', 'HSI')
                     }
        for key in index_dic:
            if key in index_name:
                self.name, url_code, self.code = index_dic.get(key)
                break
        
        if self.name is None:
            print('검색결과 없음')
            return
        
        INDEX_URL = f"https://finance.naver.com/world/sise.nhn?symbol={url_code}"
        
        html = Session().get(INDEX_URL, headers=Headers()).content
        bs = bs4.BeautifulSoup(html, 'lxml')
        

        
        today_info = bs.find("table", {"id": "dayTable"}).find("tbody").find("tr")


        #현재가
        self.price = text_safety_to_float(today_info.find("td", {"class":"tb_td2"}))
        
        #전일대비
        sign_point = today_info.get('class').pop()
        
        if sign_point == 'point_dn':
            self.compared_sign = 4
        elif sign_point == 'point_up':
            self.compared_sign = 2
        else:
            self.compared_sign = 3
            
        def compared_sign_to_sign(compared_sign):
            if compared_sign<=1:
                return 1
            else:
                return -1
        self.compared_price = text_safety_to_float(today_info.find("td", {"class": "tb_td3"}))
        
        real_compared_price = self.compared_price*compared_sign_to_sign(self.compared_sign)
        
        self.rate = round(real_compared_price*100/(self.price-real_compared_price), 2)

        self.start_price = text_safety_to_float(today_info.find("td", {"class": "tb_td4"}))
        
        #장중고가
        self.high_price = text_safety_to_float(today_info.find("td", {"class": "tb_td5"}))
        
        #장중저가
        self.low_price = text_safety_to_float(today_info.find("td", {"class": "tb_td6"}))
        
        #네이버 증권 url
        self.naver_url = INDEX_URL
        

def main():
    #체크용
    if __name__ == "__main__":
        print("메인으로 실행")
        
        a=IndexInfo()
        a.get('미국')
        print(a.to_dict())

main()
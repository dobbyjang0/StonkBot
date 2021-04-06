import win32com.client
from xing_api import XASession
from xing_api import XAQuery
from xing_api import XAReal
from xing_api import Settings
from xing_api import EventHandler
import pandas as pd
import threading
import json

# 로그인
def login():
    file_path = "./xing_user2.json"
    with open(file_path, "r") as json_file:
        user = json.load(json_file)
    session = XASession()
    session.login(user)

# 모든종목 정보
# 데이터프레임으로
# market 열이 0이면 코스피 1이면 코스닥
# ETF 열이 0이면 일반종목, 1이면 ETF
def stock_name():
    query = XAQuery()
    in_field = {"gubun": '0'}
    query.set_inblock('t8430', in_field)
    query.request()
    out_count = query.get_count('t8430OutBlock')

    shcode = [query.get_outblock('t8430OutBlock', ["shcode"], i)["shcode"] for i in range(out_count)]
    hname = [query.get_outblock('t8430OutBlock', ["hname"], i)["hname"] for i in range(out_count)]
    gubun = [query.get_outblock('t8430OutBlock', ["gubun"], i)["gubun"] for i in range(out_count)]
    etfgubun = [query.get_outblock('t8430OutBlock', ["etfgubun"], i)["etfgubun"] for i in range(out_count)]

    data = {
        "code": shcode,
        "name": hname,
        "market": gubun,
        "ETF": etfgubun
    }

    df = pd.DataFrame(data, columns = ["code", "name", "market", "ETF"])
    return df


# 실시간 체결가 수신 전용 이벤트 핸들러
class Market(EventHandler):
    def __init__(self):
        super().__init__()
        self.context = {}

    def OnReceiveRealData(self, tr_code):
        outblock_field = self.user_obj.outblock_field
        shcode = self.com_obj.GetFieldData("OutBlock", "shcode")
        self.context[shcode] = {}
        if isinstance(outblock_field, str):
            outblock_field = [outblock_field]
        for i in outblock_field:
            self.context[shcode][i] = self.com_obj.GetFieldData("OutBlock", i)
        print(self.context)

def market_tickdata():
    """
    체결시간, 전일대비구분, 전일대비, 등락율, 현지가, 시가, 고가, 저가, 누적거래량, 누적거래대금
    """
    real = XAReal(Market)
    real.set_inblock("S3_", "005930")
    real.set_outblock(["chetime", "sign", "change", "drate", "price", "open", "high", "low", "volume", "value"])
    real.start()


# 뉴스 전용 실시간 이벤트 핸들러
class NewsEvent(EventHandler):
    def __init__(self):
        super().__init__()
        self.context = None

    def OnReceiveRealData(self, tr_code):
        outblock_field = self.user_obj.outblock_field
        result = {}
        if isinstance(outblock_field, str):
            outblock_field = [outblock_field]
        for i in outblock_field:
            result[i] = self.com_obj.GetFieldData("OutBlock", i)
        code = self.com_obj.GetFieldData("OutBlock", "code")
        if code != '':
            max_num = len(code) // 12
            result["code"] = [code[12 * num + 6 : 12 * (num + 1)] for num in range(max_num)]
        else:
            result["code"] = ''
        self.context = result
        print(result)

def news():
    news = XAReal(NewsEvent)
    news.set_inblock("NWS", "NWS001", field = "nwcode")
    news.set_outblock(["date", "time", "id", "title"])
    news.start()

def main():
    login()
    print(stock_name())
    news()


main()



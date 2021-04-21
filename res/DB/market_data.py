from .xing_api import XASession
from .xing_api import XAQuery
from .xing_api import XAReal
from .xing_api import EventHandler
from .xing_api import Settings
import json
from .db import StockInfoTable
from .db import KRXRealData
from .db import KRXNewsData
from .db import KRXIndexData
import pandas as pd
import multiprocessing
import threading
import datetime
import time
import pythoncom
import win32com.client

# 로그인
def login():
    """
    {"user_id" : "이베스트증권 ID",
    "user_pw" : "이베스트증권 비밀번호",
    "mock_pw" : "모의투자 비밀번호",
    "cert_pw" : "공인인증서 비밀번호"}
    형식의 ./xing_user2.json 파일을 읽어 api 로그인
    """
    file_path = "./xing_user2.json"
    with open(file_path, "r") as json_file:
        user = json.load(json_file)
    session = XASession()
    session.login(user)

def login_mock():
    """
    {"user_id" : "이베스트증권 ID",
    "user_pw" : "이베스트증권 비밀번호",
    "mock_pw" : "모의투자 비밀번호",
    "cert_pw" : "공인인증서 비밀번호"}
    형식의 ./xing_user2.json 파일을 읽어 api 로그인
    """
    file_path = "./xing_user2.json"
    with open(file_path, "r") as json_file:
        user = json.load(json_file)
    session = XASession()
    session.login(user, server_type=1)


# 실시간 체결가 수신 전용 이벤트 핸들러
class MarketEvent(EventHandler):
    """
    xing_api.XAReal 객체에 의해 ReceiveRealData 이벤트 수신 시 작동
    실시간 체결가 수신 전용 이벤트 핸들러
    얻은 데이터를 db의 KRX_real_data에 저장
    """
    def OnReceiveRealData(self, tr_code):
        result = {}
        outblock_field = self.user_obj.outblock_field
        if isinstance(outblock_field, str):
            outblock_field = [outblock_field]
        for i in outblock_field:
            result[i] = self.com_obj.GetFieldData("OutBlock", i)
        KRXRealData().update(result)

# 뉴스 전용 실시간 이벤트 핸들러
class NewsEvent(EventHandler):
    """
    xing_api.XAReal 객체에 의해 ReceiveRealData 이벤트 수신 시 작동
    실시간 뉴스 수신 전용 이벤트 핸들러
    krx_news_data 테이블에 저장
    """
    def OnReceiveRealData(self, tr_code):
        outblock_field = self.user_obj.outblock_field
        result = {}
        date_time = self.com_obj.GetFieldData("OutBlock", 'date')
        date_time = date_time + self.com_obj.GetFieldData("OutBlock", 'time')
        date_time = datetime.datetime.strptime(date_time, '%Y%m%d%H%M%S')
        result["datetime"] = str(date_time)
        if isinstance(outblock_field, str):
            outblock_field = [outblock_field]
        for i in outblock_field:
            result[i] = self.com_obj.GetFieldData("OutBlock", i)
        KRXNewsData().insert(result)

class IndexEvent(EventHandler):
    """
    xing_api.XAReal 객체에 의해 ReceiveRealData 이벤트 수신 시 작동
    업종별 지수 전용 이벤트 핸들러
    krx_index_data 테이블에 저장
    """
    def OnReceiveRealData(self, tr_code):
        result = {}
        outblock_field = self.user_obj.outblock_field
        if isinstance(outblock_field, str):
            outblock_field = [outblock_field]
        for i in outblock_field:
            result[i] = self.com_obj.GetFieldData("OutBlock", i)
        KRXIndexData().update(result)



def _shcode(market_type):
    """
    시장 구분별 종목코드를 모두 읽는다

    Args:
        market_type: 0 전체
                     1 코스피
                     2 코스닥
    Return:
        'list' of shcode
    """
    market_type = str(market_type)
    query = XAQuery()
    in_field = {"gubun": market_type}
    query.set_inblock('t8430', in_field)
    query.request()
    out_count = query.get_count('t8430OutBlock')
    result = [query.get_outblock('t8430OutBlock', "shcode", i)["shcode"] for i in range(out_count)]
    return result

def _index_code():
    """
    업종코드 정보를 읽는다

    Return:
        'list' of upcode(업종코드)
        001: 코스피
        301: 코스닥
    """
    query = XAQuery()
    in_field = {"gubun1": ''}
    query.set_inblock('t8424', in_field)
    query.request()
    out_count = query.get_count('t8424OutBlock')
    result = [query.get_outblock('t8424OutBlock', "upcode", i)["upcode"] for i in range(out_count)]
    return result


def kospi_tickdata():
    """
    KOSPI 모든종목 실시간 감시
    종목코드, 체결시간, 전일대비구분, 전일대비, 등락율, 현재가, 시가, 고가, 저가, 누적거래량, 누적거래대금
    실시간 감시, db에 업데이트
    """
    login()
    kospi = _shcode(1)
    kospi_data = XAReal(MarketEvent)
    kospi_data.set_inblock("S3_", kospi)
    kospi_data.set_outblock(["shcode", "chetime", "sign", "change", "drate", "price", "open", "high", "low", "volume", "value"])
    kospi_data.start()

def kosdaq_tickdata():
    """
    KOSDAQ 모든종목 실시간 감시
    종목코드, 체결시간, 전일대비구분, 전일대비, 등락율, 현재가, 시가, 고가, 저가, 누적거래량, 누적거래대금
    실시간 감시, db에 업데이트
    """
    login()
    kosdaq = _shcode(2)
    kosdaq_data = XAReal(MarketEvent)
    kosdaq_data.set_inblock("K3_", kosdaq)
    kosdaq_data.set_outblock(["shcode", "chetime", "sign", "change", "drate", "price", "open", "high", "low", "volume", "value"])
    kosdaq_data.start()

def index_tickdata():
    """
    업종별 지수
    (일단 코스피, 코스닥 지수만)
    업종코드, 시간, 전일대비구분, 전일대비, 등락율, 현재지수, 시가지수, 고가지수, 저가지수, 상한종목수, 하한종목수, 상승종목비율, 외인순매수금액, 기관순매수금액

    실시간 감시, db에 업데이트
    {'upcode': '001', 'time': '153210', 'sign': '2', 'change': '4.29', 'drate': '0.13', 'jisu': '3198.62', 'openjisu': '3194.08', 'highjisu': '3206.76', 'lowjisu': '3185.67', 'upjo': '5', 'downjo': '0', 'upjrate': '57.48', 'frgsvalue': '-213424', 'orgsvalue': '-479101'}
    """
    login_mock()
    # index = _index_code()
    index_data = XAReal(IndexEvent)
    # index_data.set_inblock("IJ_", index, field = "upcode")
    index_data.set_inblock("IJ_", ['001', '301'], field="upcode")
    index_data.set_outblock(["upcode", "time", "sign", "change", "drate", "jisu", "openjisu", "highjisu", "lowjisu", "upjo", "downjo", "upjrate", "frgsvalue", "orgsvalue"])
    index_data.start()

def news():
    """
    실시간 뉴스데이터 수신
    """
    login()
    news = XAReal(NewsEvent)
    news.set_inblock("NWS", "NWS001", field = "nwcode")
    news.set_outblock(["id", "title", "code"])
    news.start()

# 테스트용
def main():
    """
    작동 테스트용 함수
    """
    if __name__ == "__main__":
        login()
        # StockInfoTable().update_table()
        process_kospi = multiprocessing.Process(target = kospi_tickdata)
        process_kosdaq = multiprocessing.Process(target = kosdaq_tickdata)
        process_index = multiprocessing.Process(target = index_tickdata)
        # process_news = multiprocessing.Process(target = news)
        process_kospi.start()
        time.sleep(3)
        process_kosdaq.start()
        time.sleep(3)
        process_index.start()
        # process_news.start()

main()
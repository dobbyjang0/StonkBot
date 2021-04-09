from xing_api import XASession
from xing_api import XAQuery
from xing_api import XAReal
from xing_api import EventHandler
from save_log_yesalchemy import KRXRealData
import pandas as pd
import json
import multiprocessing

# 로그인
def login():
    """
    {"user_id" : "이베스트증권 ID",
    "user_pw" : "이베스트증권 비밀번호",
    "cert_pw" : "공인인증서 비밀번호"}
    형식의 ./xing_user2.json 파일을 읽어 api 로그인
    """
    file_path = "./xing_user2.json"
    with open(file_path, "r") as json_file:
        user = json.load(json_file)
    session = XASession()
    session.login(user)

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
        print(result)


# 실시간 체결가 수신 전용 클래스
# class Market(XAReal):
#     """
#     사용안함
#     """
#     def __init__(self, event_handler):
#         super().__init__(event_handler)
#         self.context = {}


# 뉴스 전용 실시간 이벤트 핸들러
class NewsEvent(EventHandler):
    """
    xing_api.XAReal 객체에 의해 ReceiveRealData 이벤트 수신 시 작동
    실시간 뉴스 수신 전용 이벤트 핸들러
    얻은 데이터를 어디에 저장하지??
    """
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
        print(result)

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

def kospi_tickdata():
    """
    KOSPI 모든종목
    종목코드, 체결시간, 전일대비구분, 전일대비, 등락율, 현지가, 시가, 고가, 저가, 누적거래량, 누적거래대금
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
    KOSDAQ 모든종목
    종목코드, 체결시간, 전일대비구분, 전일대비, 등락율, 현지가, 시가, 고가, 저가, 누적거래량, 누적거래대금
    실시간 감시, db에 업데이트
    """
    login()
    kosdaq = _shcode(2)
    kosdaq_data = XAReal(MarketEvent)
    kosdaq_data.set_inblock("K3_", kosdaq)
    kosdaq_data.set_outblock(["shcode", "chetime", "sign", "change", "drate", "price", "open", "high", "low", "volume", "value"])
    kosdaq_data.start()

# 모든종목 정보
# 데이터프레임으로
# market 열이 0이면 코스피 1이면 코스닥
# ETF 열이 0이면 일반종목, 1이면 ETF
def stock_name():
    """
    kospi, kosdaq에 존재하는 모든 종목에 대한 정보를 pandas 데이터프레임 객체로 반환

    Returns:
        pandas dataframe object

               code            name    market ETF
        0     000020          동화약품      1   0
        1     000040         KR모터스      1   0
        2     000050            경방      1   0
        3     000060         메리츠화재      1   0
        ...      ...           ...    ...  ..

        Columns:
            code: 종목코드
            name: 종목명
            market: 1 코스피
                    2 코스닥
            ETF: 0 일반 종목
                 1 ETF
    """
    query = XAQuery()
    in_field = {"gubun": '0'}
    query.set_inblock('t8430', in_field)
    query.request()
    out_count = query.get_count('t8430OutBlock')

    shcode = [query.get_outblock('t8430OutBlock', "shcode", i)["shcode"] for i in range(out_count)]
    hname = [query.get_outblock('t8430OutBlock', "hname", i)["hname"] for i in range(out_count)]
    gubun = [query.get_outblock('t8430OutBlock', "gubun", i)["gubun"] for i in range(out_count)]
    etfgubun = [query.get_outblock('t8430OutBlock', "etfgubun", i)["etfgubun"] for i in range(out_count)]

    data = {
        "code": shcode,
        "name": hname,
        "market": gubun,
        "ETF": etfgubun
    }

    df = pd.DataFrame(data, columns = ["code", "name", "market", "ETF"])
    return df

def news():
    """
    실시간 뉴스데이터 수신
    """
    login()
    news = XAReal(NewsEvent)
    news.set_inblock("NWS", "NWS001", field = "nwcode")
    news.set_outblock(["date", "time", "id", "title"])
    news.start()

# 테스트용
def main():
    """
    작동 테스트용 함수
    """
    if __name__ == "__main__":
        login()
        print(stock_name())
        process_kospi = multiprocessing.Process(target = kospi_tickdata)
        # process_kosdaq = multiprocessing.Process(target = kosdaq_tickdata)
        process_news = multiprocessing.Process(target = news)
        process_kospi.start()
        # process_kosdaq.start()
        process_news.start()

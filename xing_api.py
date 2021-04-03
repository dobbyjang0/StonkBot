import win32com.client
import pythoncom
import time
import json

# 기본 설정
# 싱글톤 패턴
class Settings:
    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True
            # 디폴트 값
            self.res_directory = "C:\\eBEST\\xingAPI\\Res"

    # res 파일 경로 설정
    def set_res_directory(self, path):
        self.res_directory = path



# 기본적인 이벤트 처리 구조
class EventHandler:
    def __init__(self):
        self.user_obj = None
        self.com_obj = None

    def connect(self, user_obj, com_obj):
        self.user_obj = user_obj
        self.com_obj = com_obj


# XASession 이벤트 처리
class XASessionEvents(EventHandler):
    # login 메서드의 이벤트 처리
    def OnLogin(self, code, msg):
        if code == "0000":
            self.user_obj.login_status = 1
            print(msg)
        else:
            print(code, msg)

    # 서버와의 연결이 끊어졌을 때 발생하는 이벤트
    def OnDisconnect(self):
        print("Session disconnected")


# XAQuery 이벤트 처리
class XAQueryEvents(EventHandler):
    # 요청한 조회 TR 에 대하여 서버로부터 데이터 수신시 발생하는 이벤트
    def OnReceiveData(self, tr_code):
        self.user_obj.receive_state = 1
        # print("Receive data")




# XAReal 이벤트 처리
class XARealEvents(EventHandler):
    def OnReceiveRealData(self, tr_code):
        self.user_obj.receive_state = 1




# 서버연결, 로그인 등
# 로그아웃은 증권사에서 지원하지 않음
class XASession:
    # 이벤트핸들러 지정: XASessionEvents
    def __init__(self):
        self.com_obj = win32com.client.Dispatch("XA_Session.XASession")
        self.event_handler = win32com.client.WithEvents(self.com_obj, XASessionEvents)
        self.event_handler.connect(self, self.com_obj)

        self.com_obj.ConnectServer("hts.ebestsec.co.kr", 20001)
        self.login_status = 0

    # 로그인
    def login(self, user_info, server_type = 0):
        user_id = user_info['user_id']
        user_pw = user_info['user_pw']
        cert_pw = user_info['cert_pw']
        self.com_obj.Login(user_id, user_pw, cert_pw, server_type, False)
        while self.login_status == 0:
            pythoncom.PumpWaitingMessages()
    
    # 보유중인 계좌 개수 리턴
    def account_count(self):
        return self.com_obj.GetAccountListCount()

    # 계좌번호 목록 중에서 인덱스에 해당하는 계좌번호 리턴
    def account_num(self, index):
        return self.com_obj.GetAccountList(index)


# 조회 TR
# 동일 TR에 종목코드만 바꾸어 다수의 조회를 요청하려면 종목코드 수만큼 객체를 생성해야함
# (여러종목을 동시조회하는 자체 메서드를 제공하지 않음)
class XAQuery:
    # 이벤트핸들러 지정: XAQueryEvents
    def __init__(self):
        self.com_obj = win32com.client.Dispatch("XA_DataSet.XAQuery")
        self.event_handler = win32com.client.WithEvents(self.com_obj, XAQueryEvents)
        self.event_handler.connect(self, self.com_obj)
        self.receive_state = 0

    # tr inblock 값 지정
    # attr 는 dict 객체
    def set_inblock(self, tr_code, attr):
        res_file = Settings().res_directory + "\\" + tr_code + ".res"
        inblock = tr_code + "InBlock"
        self.com_obj.LoadFromResFile(res_file)
        for key, value in attr.items():
            self.com_obj.SetFieldData(inblock, key, 0, value)

    # tr outblock 값 취득하여 리턴
    # field_name은 리스트나 튜플 객체
    def get_outblock(self, outblock, field_name, index):
        result = {}
        for i in field_name:
            result[i] = self.com_obj.GetFieldData(outblock, i, index)
        return result

    # tr 에 해당하는 outblock이 Occurs 일 경우 Occurs 갯수 반환
    def get_count(self, block_name):
        result = self.com_obj.GetBlockCount(block_name)
        return result

    # Inblock 의 개수 설정
    def set_count(self, block_name, count):
        self.com_obj.SetBlockCount(block_name, count)

    # 지정한 블록의 내용 삭제
    def clear_block(self, block_name):
        self.com_obj.ClearBlockData(block_name)

    # 블록의 전체 데이터 취득
    def get_all(self, block_name):
        result = self.com_obj.GetBlockData(block_name)
        return result

    # 조회 TR 요청
    def request(self, is_next = 0):
        result = self.com_obj.Request(is_next)
        # self.com_obj.Request(is_next)
        while self.receive_state == 0:
            pythoncom.PumpWaitingMessages()
        state = None
        if result >= 0:
            state = "TR received"
        else:
            state = result
        print(state)
        return state




# 실시간 TR
class XAReal:
    # 이벤트핸들러 지정: XARealEvents
    def __init__(self):
        self.com_obj = win32com.client.Dispatch("XA_DataSet.XAReal.1")
        self.event_handler = win32com.client.WithEvents(self.com_obj, XARealEvents)
        self.event_handler.connect(self, self.com_obj)
        self.receive_state = 0

    # inblock 세팅
    # (블록의 필드명, 데이터)
    def set_inblock(self, tr_code, *args):
        res_file = Settings().res_directory + "\\" + tr_code + ".res"
        self.com_obj.ResFileName(res_file)
        self.com_obj.SetFieldData("InBlock", *args)

    # outblock 세팅
    # (필요한 데이터의 필드명)
    def get_outblock(self, field_name):
        result = {}
        for i in field_name:
            result[i] = self.com_obj.GetFieldData("OutBlock", i)
        return result

    # 특정 종목의 실시간 데이터 수신 해제
    def del_realdata(self, shcode):
        self.com_obj.UnadviseRealDataWithKey(shcode)

    # 등록된 실시간 데이터 전부 해제
    def del_all(self):
        self.com_obj.UnadviseRealData()

    # 실시간 등록
    def run(self):
        self.com_obj.AdviseRealData()
        while self.receive_state == 0:
            pythoncom.PumpWaitingMessages()

# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *

# 지정할수 잇는 화면 최대 갯수는 200개
# TR 제한 1초에 5건, 1분에 100건, 1시간 1000건
# 같은 화면으로 같은 요청 반복하면 데이터가 안받아질 수도 있음
# 필요한 경우 두 화면번호로 같은 요청을 번갈아가며 전송
# 당연하게도 장중에만 실시간데이터 메소드 작동함. 추후 시간 확인 기능 추가예정

class KiwoomConnect:
    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    ##########################
    #       initialize       #
    ##########################
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.event_loop = QEventLoop()
        self.__received_trdata = None
        self.__received_realdata = None


    ##########################
    #     private method     #
    ##########################
    # OnEventConnect 처리하는 private 메소드
    # 로그인 요청 후 발생한 OnEventConnect 메소드의 인자가 0이면 로그인 성공, 다른 값이면 에러
    # 100: 사용자 정보교환 실패, 101: 서버접속 실패, 102: 버전처리 실패
    def __read_errcode(self, err_code):
        if err_code == 0:
            print("Kiwoom login success!")
        else:
            print("Kiwoom login Failed. error code: %d", err_code)
        self.event_loop.exit()

    # OnReceiveTrData 이벤트 처리하는 private 메소드
    # {종목명:{속성:값}} 형태의 dict 객체로 처리함
    def __receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        data_length = self.kiwoom.dynamicCall("GetDataCount(QString)",
                                              rqname)
        attribute = ["종목명", "종목코드", "현재가", "거래량", "거래대금", "전일대비", "등락율", "시가", "고가", "저가", "종가"]
        if data_length == 0:
            data_length += 1
        stock_info = {}
        for i in range(data_length):
            stock_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                 trcode, rqname, i, "종목코드")
            stock_code = stock_code.strip()
            stock_info[stock_code] = {}
            for j in attribute:
                 value = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                   trcode, rqname, i, j)
                 stock_info[stock_code][j] = value.strip()

        # class private 변수에 대입함(이렇게안하면 못빼냄)
        self.__received_trdata = stock_info
        self.event_loop.exit()
    
    # OnReceiveRealData 이벤트 처리하는 private 메소드
    def __receive_realdata(self, stock_code, real_type, real_data):
        context = {"현재가": 10,
                   "전일대비": 11,
                   "거래량": 13,
                   "거래대금": 14,
                   "시가": 16,
                   "고가": 17,
                   "저가": 18,
                   "전일대비기호": 25}
        data = {}
        for key, value in context.items():
            data[key] = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", stock_code, value)
        self.__received_realdata = data
        self.event_loop.exit()

    ###########################
    #      public method      #
    ###########################
    # 로그인
    # pyqt 이벤트 루프
    def login(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.__read_errcode)
        self.event_loop.exec_()

    # 서버 접속상태 확인
    # GetConnectState 메소드의 리턴값이 1이면 연결된상태, 0 이면 연결되지 않은 상태
    def connect_state(self):
        if self.kiwoom.dynamicCall("GetConnectState()") == 1:
            print("Connect")
        else:
            print("No connect")

    # 단일종목 기본정보 TR요청(opt10001) - 수신된 데이터 반환(초당 최대 5회만 실행)
    # stock_code는 str 타입으로 넣어야 함
    # screen_no는 0000을 제외한 네자리 양수(str 타입으로)
    # 주의) 종가, 거래대금 데이터 안넘어옴(공백으로 표시됨)
    def info_tr(self, stock_code, screen_no):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", '종목코드', stock_code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", 'singleinfo', 'opt10001', 0, screen_no)
        self.kiwoom.OnReceiveTrData.connect(self.__receive_trdata)
        self.event_loop.exec_()
        return self.__received_trdata


    # 여러종목 기본정보 TR요청(OPTKWFID) - 수신된 데이터 반환(초당 최대 5회만 실행)
    # stock_code는 각 요소가 str인 list 타입으로 넣어야 함
    # screen_no는 0000을 제외한 네자리 양수(str 타입으로)
    def manyinfo_tr(self, stock_code, screen_no):
        # !todo: 화면번호 유효성검사(?)
        join_code = ';'.join(stock_code)
        self.kiwoom.dynamicCall("CommKwRqData(QString, int, int, int, QString, QString)",
                                join_code, 0, len(stock_code), 0, 'multiinfo', screen_no)
        self.kiwoom.OnReceiveTrData.connect(self.__receive_trdata)
        self.event_loop.exec_()
        return self.__received_trdata

    # 실시간데이터 연결 해제
    # screen_no는 0000을 제외한 네자리 양의 정수(str 타입으로)
    def disconnect_real(self, screen_no):
        self.kiwoom.dynamicCall("DisconnectRealData(Qstring)", screen_no)

    # tr로 연결된 실시간데이터 조회
    def info_real(self, stock_code):
        self.kiwoom.OnReceiveRealData.connect(self.__receive_realdata)
        self.event_loop.exec_()
        return self.__received_realdata

inst = KiwoomConnect()
inst.login()
inst.connect_state()
a = inst.info_tr('005930', '0001')
a1 = inst.info_tr('035720', '0003')
stock = ['005930', '035720']
b = inst.manyinfo_tr(stock, '0002')
# c = inst.info_real('0035720')
print(a)
print(a1)
print(b)
# print(c)
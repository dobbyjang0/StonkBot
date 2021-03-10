import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *

class KiwoomConnect:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.event_loop = QEventLoop()

    # 로그인 처리상태 확인(login 메서드에서만 내부적으로 호출되어야함, 단독으로 사용 ㄴㄴ)
    # 로그인 요청 후 발생한 OnEventConnect 메소드의 인자가 0이면 로그인 성공, 다른 값이면 에러
    # 100: 사용자 정보교환 실패, 101: 서버접속 실패, 102: 버전처리 실패
    def read_errcode(self, err_code):
        if err_code == 0:
            print("login success!")
        else:
            print("login Failed. err_code: %d", err_code)
        self.event_loop.exit()

    # 로그인
    # pyqt 이벤트 루프
    def login(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.read_errcode)
        self.event_loop.exec_()

    # 서버 접속상태 확인
    # GetConnectState 메소드의 리턴값이 1이면 연결된상태, 0 이면 연결되지 않은 상태
    def state(self):
        if self.kiwoom.dynamicCall("GetConnectState()") == 1:
            print("Connect")
        else:
            print("No connect")




inst = KiwoomConnect()
inst.login()
inst.state()

from xing import xasession
from xing import xacom
from xing import xareal
import xing
import json



server = {
    "address" :"hts.ebestsec.co.kr",    # 서버주소
    "port" : 20001, # 서버포트
    "type" : 0  # 서버 타입
}

# user = {
#     "id" : "id",   # 아이디
#     "passwd" : "password",  # 비밀번호
#     "account_passwd" : "OOOO",  # 계좌 비밀번호
#     "certificate_passwd" : "OOOOOOOO"   # 공인인증서 비밀번호
# }

file_path = "./xing_user.json"
with open(file_path, "r") as json_file:
    user = json.load(json_file)

session = xasession.Session()
session.login(server, user)
xacom.parseJstatus("1")
xareal.Real

session.logout()

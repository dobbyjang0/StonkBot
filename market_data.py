from xing_api import XASession
from xing_api import XAQuery
from xing_api import XAReal
import pandas as pd
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
def stock_name():
    query = XAQuery()
    in_field = {"gubun": '0'}
    query.set_inblock('t8430', in_field)
    query.request()
    out_count = query.get_count('t8430OutBlock')

    shcode = [query.get_outblock('t8430OutBlock', ["shcode"], i)["shcode"] for i in range(out_count)]
    hname = [query.get_outblock('t8430OutBlock', ["hname"], i)["hname"] for i in range(out_count)]
    gubun = [query.get_outblock('t8430OutBlock', ["gubun"], i)["gubun"] for i in range(out_count)]

    data = {
        "code": shcode,
        "name": hname,
        "market": gubun
    }

    df = pd.DataFrame(data, columns = ["code", "name", "market"])
    return df

def main():
    login()




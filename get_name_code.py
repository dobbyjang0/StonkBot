# -*- coding: utf-8 -*-
# SQL문 연습용, 사이트에서 주식 코드와 이름을 받아서 불러온다.

from sqlalchemy import create_engine
from sqlalchemy import text as sql_text
import pymysql
import pandas

# db와 연결, 'dict' 객체 context 를 인풋으로, 'pymysql.connections.Connection' 객체 반환
# context 에 dict type 이 아니거나 필수 key가 존재하지 않으면 에러메세지 반환
def conn(user, password, host, port, db, charset):
    
    db_connection_str = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
    engine = create_engine(db_connection_str, encoding = charset)

    return engine

"""
context = {"user": '설정한 db 유저명', 
    "password": '설정한 db 유저 비밀번호', 
    "host": '서버 주소, 로컬일 경우 127.0.0.1', 
    "port": '포트 주소'
    "db": 'db 이름', 
    "charset": 'utf8'}
"""


# 어드민 인풋
if input("sql 기본값 사용? (y/n)")=="y":
    username, password, db_name = "dobbyjang0", "1234", "stonk_bot"
    print("기본값:" , username , password , db_name)
else:
    username= input("username 입력 :")
    password= input("password 입력 :")
    db_name= input("db 입력 :")


# db에 접근할 유저 정보 생성
context = {"user": username, 
    "password": password, 
    "host": '127.0.0.1', 
    "port": 3306,
    "db": db_name, 
    "charset": 'utf8'}

# connection 
connection = conn(**context)

# code, name pandas로 불러오기
df = pandas.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
df = df[['회사명', '종목코드']]
df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
df = df.reindex(columns=['code','name'])

# 저장시키기
df.to_sql(name='stock_code', con=connection, if_exists='append',index=False, method='multi')
print("저장완료")
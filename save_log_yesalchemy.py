# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import text as sql_text
import pymysql

# db와 연결, 'dict' 객체 context 를 인풋으로, 'pymysql.connections.Connection' 객체 반환
# context 에 dict type 이 아니거나 필수 key가 존재하지 않으면 에러메세지 반환
def conn(user, password, host, port, db, charset):
    
    db_connection_str = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
    engine = create_engine(db_connection_str, encoding = charset, echo = True)

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

sql = sql_text("""INSERT INTO log (
            guild_id, channel_id, author_id, stock_name
        )
        VALUES (2, 3, 4, "00000")
        """)

result=connection.execute(sql)


# LogTable 에 로그 저장
#access.insert(1, 2, 3, "000000")
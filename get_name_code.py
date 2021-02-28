# -*- coding: utf-8 -*-
# SQL문 연습용, 사이트에서 주식 코드와 이름을 받아서 불러온다.

import pymysql
import pandas

# db와 연결, 'dict' 객체 context 를 인풋으로, 'pymysql.connections.Connection' 객체 반환
# context 에 dict type 이 아니거나 필수 key가 존재하지 않으면 에러메세지 반환
def conn(context):
    if type(context) != dict:
        raise TypeError("Context should be 'dict' type")
    
    attr = ["user", "password", "host", "port", "db", "charset"]
    for i in attr:
        if context[i]:
            continue
        else:
            raise KeyError("Context should have key 'user', 'password', 'host', 'port', 'db', 'charset'")

    connection = pymysql.connect(
        user = context["user"], 
        password = context["password"], 
        host = context["host"],
        port = context["port"],
        db = context["db"], 
        charset = context["charset"]
    )
    return connection


# 커서 생성, 'dict' 객체 context 를 인풋으로, 'pymysql.cursors.Cursor' 객체 반환
# context 에 dict type 이 아니거나 필수 key가 존재하지 않으면 에러메세지 반환
def curs(context):
    if type(context) != dict:
        raise TypeError("Context should be 'dict' type")
    
    attr = ["user", "password", "host", "port", "db", "charset"]
    for i in attr:
        if context[i]:
            continue
        else:
            raise KeyError("Context should have key 'user', 'password', 'host', 'port', 'db', 'charset'")
        
    conn = pymysql.connect(
        user = context["user"], 
        password = context["password"], 
        host = context["host"],
        port = context["port"],
        db = context["db"], 
        charset = context["charset"]
    )
    curs_obj = conn.cursor()
    return curs_obj

# stock_code 테이블 생성, 이미 존재하면 에러메세지 반환
def create_code_table(conn_obj, curs_obj):
    if type(curs_obj) != pymysql.cursors.Cursor:
        raise TypeError("curs_obj should be cursor object")

    if type(conn_obj) != pymysql.connections.Connection:
        raise TypeError("conn_obj should be connection object")

    sql = """
        CREATE TABLE `stock_code` (
        `code` int PRIMARY KEY AUTO_INCREMENT,
        `name` varchar(20)
        );
        """
    try:
        curs_obj.execute(sql)
        conn_obj.commit()
    except:
        error_message = "Already exist"
        print(error_message)

# LogTable CRUD
class LogTable:
    __slots__ = ["conn_obj", "curs_obj"]
    def __init__(self, conn_obj, curs_obj):
        self.curs_obj = curs_obj
        self.conn_obj = conn_obj
    
    # Insert into log, id는 정수타입이어야함, stock_name 은 문자열이어야함
    def insert(self, guild_id, channel_id, author_id, stock_name):
        for i in [guild_id, channel_id, author_id]:
            if type(i) != int:  
                raise TypeError("guild_id, channel_id, author_id should be 'int' type")
        if type(stock_name) != str:
            raise TypeError("stock_name should be 'str' type")

        # !TODO: sql injecton 방어를 위한 데이터 검증 로직 추가

        #value = ','.join([guild_id, channel_id, author_id, stock_name])
        sql = """
        INSERT INTO `log` (
            guild_id, channel_id, author_id, stock_name
        )
        VALUES (%d, %d, %d, %s)
        """
        self.curs_obj.execute(sql, (guild_id, channel_id, author_id, stock_name))
        self.conn_obj.commit()

        

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
connection = conn(context)

# cursor
cursor = curs(context)

# log 테이블 생성
create_code_table(connection, cursor)

# code, name pandas로 불러오기
df = pandas.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
df = df[['회사명', '종목코드']]
df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
df = df.reindex(columns=['code','name'])



# LogTable 접근
#access = LogTable(connection, cursor)

# LogTable 에 로그 저장
#access.insert(1, 2, 3, "000000")
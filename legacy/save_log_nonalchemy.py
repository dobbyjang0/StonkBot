# -*- coding: utf-8 -*-
import pymysql

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

# log 테이블 생성, 이미 존재하면 에러메세지 반환
def create_log_table(conn_obj, curs_obj):
    if type(curs_obj) != pymysql.cursors.Cursor:
        raise TypeError("curs_obj should be cursor object")

    if type(conn_obj) != pymysql.connections.Connection:
        raise TypeError("conn_obj should be connection object")

    sql = """
        CREATE TABLE `log` (
        `index` int PRIMARY KEY AUTO_INCREMENT,
        `guild_id` int,
        `channel_id` int,
        `author_id` int,
        `stock_name` varchar(20)
        );
        """
        
    curs_obj.execute(sql)
    conn_obj.commit()
    

# LogTable CRUD
class LogTable:
    __slots__ = ["conn_obj", "curs_obj"]
    def __init__(self, conn_obj, curs_obj):
        self.curs_obj = curs_obj
        self.conn_obj = conn_obj
    
    def insert(self, guild_id, channel_id, author_id, stock_name):
        for i in [guild_id, channel_id, author_id], stock_name:
            if type(i) == int or type(i) == str:
                continue
            else:
                raise TypeError("guild_id, channel_id, author_id, stock_name should be int, str type")

        # sql injecton 방어를 위해 아래와 같이 쿼리 작성(인수가 이스케이프 됨)
        sql = """
        INSERT INTO `log` (
            guild_id, channel_id, author_id, stock_name
        )
        VALUES (%s, %s, %s, %s)
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
create_log_table(connection, cursor)

# LogTable 접근
access = LogTable(connection, cursor)

# LogTable 에 로그 저장
#access.insert(1, 2, 3, "000000")
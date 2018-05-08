# -*- coding: UTF-8 -*-
import pymssql
from odoo.tools.config import config

class MSSQL:
    def __init__(self,host,user,pwd,db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def __GetConnect(self):
        if not self.db:
            raise(NameError,"没有设置数据库信息")
        self.conn = pymssql.connect(host=self.host,user=self.user,password=self.pwd,database=self.db ,charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise(NameError,"连接数据库失败")
        else:
            return cur

    def ExecQuery(self,sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        resList = cur.fetchall()

        #查询完毕后必须关闭连接
        self.conn.close()
        return resList

    def ExecNonQuery(self,sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()


def Lz_test_SQLCa(self):
    Lz_test_SQLCa = MSSQL(config.get('lztest_host'),
                  config.get('lztest_user'),
                  config.get('lztest_pass'),
                  config.get('lztest_db'))
    return Lz_test_SQLCa

def Lz_read_SQLCa(self):
    Lz_read_SQLCa = MSSQL(config.get('lzread_host'),
                  config.get('lzread_user'),
                  config.get('lzread_pass'),
                  config.get('lzread_db'))
    return Lz_read_SQLCa

def Lz_write_SQLCa(self):
    Lz_write_SQLCa= MSSQL(config.get('lzwrite_host'),
                   config.get('lzwrite_user'),
                   config.get('lzwrite_pass'),
                   config.get('lzwrite_db'))
    return Lz_write_SQLCa


def Bnc_read_SQLCa(self):
    Bnc_read_SQLCa = MSSQL(config.get('bnc_read_host'),
                  config.get('bnc_read_user'),
                  config.get('bnc_read_pass'),
                  config.get('bnc_read_db'))
    return Bnc_read_SQLCa


def bn_SQLCa(para_db):
    bn_SQLCa = MSSQL(para_db['db_ip'],
                  para_db['db_user'],
                  para_db['db_password'],
                  para_db['db_name'])
    return bn_SQLCa

#取两位小数 四舍五入
def decimal_2(val):
    val_1000=int(val*1000)
    a=int(val*100)/100.00
    if val>=0:
        if abs(val_1000)%10>=5:
            a_1=(float(str(a*100))+1)/100
            return a_1
        else:
            return a
    else:
        if abs(val_1000)%10>=5:
            a_1=(float(str(a*100))-1)/100
            return a_1
        else:
            return a
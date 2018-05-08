# -*- coding: UTF-8 -*-
import hashlib
import time
import urllib
import requests
import json
import datetime
import psycopg2

class bn_eservice_connect(object):
    def __init__(self):
        
        self.db_connect={
        'db_host':'192.168.168.199',
        'db_info':'prod',
        'db_user':'pgquery',
        'db_pass':'buynow',
        }

    def _connect(self):
        conn = psycopg2.connect(database=self.db_connect['db_info'], user=self.db_connect['db_user'], password=self.db_connect['db_pass'], host=self.db_connect['db_host'], port="5432")
        return conn

    
    def exec_return(self, sql):
        cur = self._connect().cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        self._connect().close()  
        return rows



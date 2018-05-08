# -*- coding: UTF-8 -*-
import hashlib
import time
import urllib
import requests
import json
import datetime


class bn_2dfire_connect_Request(object):
    def __init__(self):
        pass

    def MD5(self, str):
        import hashlib
        import types
        if type(str) is types.StringType:
            m = hashlib.md5()
            m.update(str)
            return m.hexdigest()
        else:
            return ''

    def get_json(self, url, appid,data):
        strSign=SIGN(data,appid)
        data.update({"sign": strSign})
        post_date =urllib.urlencode(data)
        my_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        time.sleep(1)  # 休眠1秒
        obj = requests.post(url, headers=my_headers, data=post_date)
        return json.loads(obj.content)


class bn_2dfire_connect_api(object):
    def __init__(self,object):
        self.ewh_request    = bn_2dfire_connect_Request()
        self.url           =object['para_my_url']['bn_2dfire_function_api']
        self.method        =object['para_my_url']['bn_2dfire_function_method'] 
        self.methodtype    =object['para_my_url']['bn_2dfire_api_type'] 
        self.appid         =object['para_my_appid']
        self.store         =object['para_my_store']
        self.connection    =object['para_connection']

    
    def Get_ResultAll(self, data):
        appkey  = str(self.appid['bn_2dfire_app_key'])
        appsec  = str(self.appid['bn_2dfire_app_secret'])        
        if data:
            currDate = data['currdate'].strftime("%Y-%m-%d")
        MY_DATA={
            "method":str(self.method),
            "entityId":str(self.store['code']),
            "appKey":appkey,
            "v":"1.0",
            "timestamp": str(long(time.time() * 1000)),
            "currDate": currDate.replace('-', ''),            
            }
        
        if data and data['orderids'] is not None:
            MY_DATA["orderIds"]=str(data['orderids'])
        obj_json = self.ewh_request.get_json(self.url,self.appid ,MY_DATA)
        return obj_json



def MD5(str):
    return hashlib.md5(str.encode('utf-8')).hexdigest()

def ShA1(str):
    return hashlib.sha1(str.encode('utf-8')).hexdigest().upper()

def SIGN(mydict,appid):
    appkey  = str(appid['bn_2dfire_app_key'])
    appsec  = str(appid['bn_2dfire_app_secret'])
    obj = []
    obj.append(appsec)
    for key, value in sorted(mydict.iteritems()):
        obj.append(key)
        obj.append(value)
    obj.append(appsec)
    str1 = "".join(obj)
    return ShA1(str1)

def split_order_byMaxNum(list):
    #二维火规定每次查询做多20个订单号码
    max=20
    result=[]
    if len(list)>max:
        time=int(len(list)/max)
        for i in range(0,time+1):
            result.append(list[i*max:(i+1)*max])
    else:
        result.append(list)
    return result
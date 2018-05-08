# -*- coding: utf-8 -*-
# refer by 
# http://www.pospal.cn/openplatform/customerapi.html

import json
import time
import datetime
import requests
import sys
from odoo import api, fields, models
import hashlib
import types
import logging

_logger = logging.getLogger(__name__)

    
class bn_yinbao_connect_Request(object):
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

    def get_json(self, url, appkey, data):
        timeStamp = str(long(time.time() * 1000))
        data_signature = self.MD5(appkey + str(data).replace("u'", "'")).upper()
        my_headers = {
            'User-Agent': 'openApi',
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Encoding': 'gzip,deflate',
            'time-stamp': timeStamp,
            'data-signature': data_signature
        }
        time.sleep(1)  # 休眠1秒
        obj = requests.post(url, headers=my_headers, data=str(data).replace("u'", "'"))
        return json.loads(obj.content)
    
    

class bn_yinbao_connect_api(object):
    def __init__(self,object):
        self.yb_request    =bn_yinbao_connect_Request()
        self.url           =object['para_my_url']['bn_yinbao_function_api']
        self.method        =object['para_my_url'].id
        self.methodtype    =object['para_my_url']['bn_yinbao_api_type'] 
        self.connection    =object['para_connection']

    def Get_ResultAll(self, APPID, data=None):
        appkey = str(APPID['bn_yinbao_appkey'])
        appid  = str(APPID['bn_yinbao_appid'])
        
        if not data:
            data = {'appId': appid, }

        obj_json = self.yb_request.get_json(self.url, appkey, data)
        if obj_json['status']=='success':
            obj_data = obj_json['data']
            
        else :
             _logger.info("bn=>yinbao Get_ResultAll error =>%s=>%s=>%d" % (appid,obj_json['messages'][0],obj_json['errorCode'])) 
             return None

        pageSize = int(obj_data["pageSize"])
        count = len(obj_data["result"])

        if obj_data.has_key('postBackParameter'):
#                    if self.methodtype <> 'bn_api_yinbao_product':
                        self.Insertpostbackparameter(APPID, obj_data['postBackParameter'])
#                    else :
#                        self.Insertpostbackparameter(APPID, obj_data['postBackParameter'])                        

        if (count == 0):
            return

        if (count < pageSize):
            print obj_data["result"]

            return obj_data["result"]
        else:
            data.update({"postBackParameter": obj_data["postBackParameter"]})
#            _logger.info("bn=>yinbao Get_ResultAll %s" % str(appid))
            if   self.Get_ResultAll(APPID, data) is not None: 
#                _logger.info(obj_data["result"])   
                for items in self.Get_ResultAll(APPID, data):
                    obj_data["result"].append(items)
                _logger.info("bn=>yinbao Get_ResultAll=>%s=>%d" % (str(appid),len(obj_data["result"])))     
#                print len(obj_data["result"])
            return obj_data["result"]

    # 插入log
    def Insertpostbackparameter(self, appid, postbackparameter):
            vals = {
                    'bn_yinbao_appid': appid.id,
                    'bn_yinbao_url': self.method,
                    'bn_postBackParameter': str(postbackparameter),
                    'bn_parameterValue': postbackparameter["parameterValue"].encode('UTF-8'),
                }        
        
#            if category_key is not None:
#                vals['bn_yinbao_second_id']= category_key
         
            self.connection.env['bn.yinbao.log'].create(vals)









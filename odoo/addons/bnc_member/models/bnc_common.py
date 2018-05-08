# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import time
import datetime

def bnc_root_category(self,business):
        companys=self.env['res.company'].get_bussiness_stores(business)
        if not self.env['product.category'].search_bycode(business['strBuscode']):
            res= {
                'code' : business['strBuscode'],
                'name' : business['strBusName'],
                'buid':business['id'],

                }
            pd=self.env['product.category'].create(res).id
            pc=self.env['pos.category'].create(res).id
        else:
            pd=self.env['product.category'].search_bycode(business['strBuscode']).id
            pc=self.env['pos.category'].search_bycode(business['strBuscode']).id           
        #设置门店分类    
#        r02=self.env['product.category'].search_bycode(store_code)
        for store in companys:
            val1= {
                    'code' : store['bncode'],
                    'name' : store['name'],
                    'buid': business['id'],
                    'parent_id':pd,
                    'store_id':store['id'],
                    }
    
            val2= {
                    'code' : store['bncode'],
                    'name' : store['name'],
                    'buid': business['id'],
                    'parent_id':pc,
                    'store_id':store['id'],
                    }
            if not self.env['product.category'].search_bycode(store['bncode']):
                self.env['product.category'].create(val1)
                self.env['pos.category'].create(val2) 
            else:
                self.env['product.category'].write(val1)
                self.env['pos.category'].write(val2)                     
        return True
    
def bnc_get_product_lastupdatetime_byBussinessUnit(self,business):
        sql="""
            select max(write_date) from product_template where buid={0}
            """
        sql=sql.format(business['id'])  
        cr = self._cr 
        cr.execute(sql)
        res=cr.fetchall()
        if res[0][0] is not None:
            return res[0]
        else :
            return None

def bnc_get_storescode_byBussinessUnit(self,business):
    stores =  self.env['res.company'].search([('buid', '=',business.id)])
    entitylist=[]
    for entity in stores:
        entitylist.append(entity['bncode'])
    return entitylist

def bnc_get_NeedUpdateProduct_byBussinessUnit(self,business):
    enlist=bnc_get_storescode_byBussinessUnit(self,business)
    maxtime=bnc_get_product_lastupdatetime_byBussinessUnit(self,business)
    if maxtime is not None:
        productids = self.env['bn.2dfire.product'].search([('write_date', '>=',maxtime),('entityId','in',enlist)])
    else :
        productids = self.env['bn.2dfire.product'].search([('entityId','in',enlist)])        

    return productids


def bnc_char_to_date(ymd):
    day= datetime.datetime.strptime(ymd, '%Y-%m-%d %H:%M:%S') -datetime.timedelta(hours=8)
    return day

    
    
    


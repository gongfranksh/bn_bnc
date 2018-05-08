# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.bn_pospal.models.bn_yinbao_product import  *
from odoo.addons.bn_pospal.models.bn_yinbao import  *
from odoo.addons.bn_pospal.models.bn_yinbao_member import  *
from odoo.addons.bn_pospal.models.bn_yinbao_order import  *
from odoo.addons.bn_pospal.models.bn_yinbao import  *
from bnc_common import *
import logging

_logger = logging.getLogger(__name__)
TOTAL_DAY=10
SPLIT_NUMBER=5

   
def _get_business(self):
    res=self.env['bnc.business'].get_bnc_business_bycode('gam')  
    return res  
    

def sync_category_to_bnc(self):
    bnc_root_category(self,self._get_business())
    bnc_insert_category(self)
    return True

def sync_product_to_bnc(self):
#    bnc_root_category(self,self._get_business())
    bnc_insert_product(self)
    return True

def sync_sales_to_bnc(self):
#    bnc_root_category(self,self._get_business())
    bnc_insert_sales(self)
    return True





def bnc_insert_category(self):
    _logger.info("bnc=>yinbao bnc_insert_category")          
    business=self._get_business()
    for cateids in self.env['bn.yinbao.category'].search([]):
            p01=self.env['product.category'].search_bycode(cateids['store_code']).id
            res= {
                'code' : cateids['code'],
                'name' : cateids['name'],
                'buid':business['id'],
                'parent_id':p01,
                'store_id':self.env['res.company'].search_bycode(cateids['store_code']).id,
                }
            r01=self.env['product.category'].search_bycode(cateids['code'])
            if r01 :
                r01.write(res)
            else:
                self.env['product.category'].create(res).id
            
            p01=None
            p01=self.env['pos.category'].search_bycode(cateids['store_code']).id
            res.update({"parent_id": p01})
            
            r01=self.env['pos.category'].search_bycode(cateids['code'])
            if r01 :
                r01.write(res)
            else:
                self.env['pos.category'].create(res).id
    return True

def bnc_setparent_category(self):
        return True

def bnc_insert_product(self):
    business=self._get_business()
    maxtime=bnc_get_product_lastupdatetime(self)
    
    _logger.info("bnc=>yinbao bnc_insert_product")      
    if maxtime is not None:
        productids = self.env['bn.yinbao.product'].search([('write_date', '>=',maxtime)])
    else :
        productids = self.env['bn.yinbao.product'].search([])        
        
    i=0
    for pids in productids:
            i=i+1
            print i,
            print len(self.env['bn.yinbao.product'].search([]))
            res= {
                'code' : pids['code'],
                'name' : pids['name'],
#                'spec':spec,
#                'brand_id':b01,
                'list_price':pids['sellPrice'],
                'price':pids['sellPrice'],
#                'bn_barcode':tmp_code,
                'sale_ok':True,
                'default_code': pids['code'],
                'categ_id':self.env['product.category'].search_bycode(pids['categoryUid']).id,
#                'b_category':self.env['product.category'].search_bycode(store_code+'-'+classid[0:4]).id,
#                'm_category':self.env['product.category'].search_bycode(store_code+'-'+classid[0:6]).id,
#                'b_sup_id':s01.id,
#                'timestamp': timestamp,
                'buid':business['id'],
                'store_id':self.env['res.company'].search_bycode(pids['store_code']).id,             
                }
            #检查是插入还是更新            
            r01=self.env['product.template'].search_bycode(pids['code'])
            if r01:            
                r01.write(res)
#                print 'update'
#                print res            
            else:
                self.env['product.template'].create(res)
#                print 'create'
#                print res
#        self.set_jsport_category_parent()  
    return True  


def bnc_get_product_lastupdatetime(self):
        business=self._get_business()
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
        
        
def bnc_insert_sales(self):  
            print 'bnc_insert_sales'
            #proc_days 往前处理几天
            proc_days=TOTAL_DAY
            proc_date_task=check_pos_data_daily(self,proc_days)
#            if db['store_code'] =='02002':
            for d in proc_date_task:
                    if (d['local_records_count'] <> d['remote_records_count']) or (d['local_records_count']==0):    
                       _logger.info("bnc=>yinbao bnc_insert_sales"+d['proc_date']+'====>'+'local have====>'+str(d['local_records_count'])+'     remote have====>'+str(d['remote_records_count'])+'==>need to sync')          
                       print d['proc_date']+'====>'+'local have====>'+str(d['local_records_count'])+'     remote have====>'+str(d['remote_records_count'])+'==>need to sync'
                       delete_pos_data_daily(self,d['proc_date'])
                       insert_pos_data_daily(self,d['proc_date']) 
                    else :                                  
                       _logger.info("bnc=>yinbao bnc_insert_sales"+d['proc_date'] +'====>'+'already done!!!')          
                       print d['proc_date'] +'====>'+'already done!!!'
    
            return 
    
    
def delete_pos_data_daily(self,ymd):
            exec_sql=""" 
                        delete from pos_order 
                        where to_char(date_order,'yyyy-mm-dd')='{0}' and buid ={1}
                    """
            exec_sql=exec_sql.format(ymd,self._get_business().id)  
            cr = self._cr 
            cr.execute(exec_sql)
            return True
                
 
def insert_pos_data_daily(self,procdate):
        
        yinbao_pos_order_list = self.env['bn.yinbao.order'].search([('sale_datetime','>=',procdate+' 00:00:00'),
                                                                    ('sale_datetime','<=',procdate+' 23:59:59')])
        i=0
        for  yb in yinbao_pos_order_list:
            i=i+1
            print  i,len(yinbao_pos_order_list) 

            vals=[]
            res=[]
#            para_time =datetime.datetime.strptime(yb['sale_datetime'],'%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=8)
            
        
            br01=self.env['res.company'].search_bycode(yb['store_code']).id
                
            if  yb['customerUid'] :
                
                mt=self.env['bn.yinbao.member'].search([('code','=', yb['customerUid']),('store_code','=',yb['store_code'])])
                m01=self.env['res.partner'].search_bycardid(mt['phone']).id
            else :
                m01=None
            pos_order_line = self.env['bn.yinbao.order.detail'].search([('order_id','=',yb.id)])   
            for pl in pos_order_line:
                
                inter_pcode= pl['productUid']
                

                p01=self.env['product.template'].search_bycode(inter_pcode)  
                
                if not p01:
                    res_product= {
                        'code' : pl['productUid'],
                        'name' : pl['name'],
        #                'spec':spec,
        #                'brand_id':b01,
                        'list_price':pl['sellPrice'],
                        'price':pl['sellPrice'],
        #                'bn_barcode':tmp_code,
                        'sale_ok':True,
                        'default_code': pl['productUid'],
                        'categ_id':self.env['product.category'].search_bycode(yb['store_code']).id,
        #                'b_category':self.env['product.category'].search_bycode(store_code+'-'+classid[0:4]).id,
        #                'm_category':self.env['product.category'].search_bycode(store_code+'-'+classid[0:6]).id,
        #                'b_sup_id':s01.id,
        #                'timestamp': timestamp,
                        'buid':self._get_business().id,
                        'store_id':self.env['res.company'].search_bycode(yb['store_code']).id,             
                        }
                    #检查是插入还是更新            
                    val_temp={
                            'product_tmpl_id':self.env['product.template'].create(res_product).id
                            }
                    prod_tmp=self.env['product.product'].create(val_temp).id
                else :
                    prod_tmp=self.env['product.product'].search([('default_code', '=',inter_pcode)]).id

                res.append((0,0,{
                    'product_id':prod_tmp,
                    'price_unit':pl['sellPrice'],
                    'qty':pl['quantity'], 
                    }))
                

            vals={
                'date_order': yb['sale_datetime'],
                'company_id': br01,
                'user_id':self.env['res.users'].search([('login', '=','game-users')]).id,
                'note':yb['sn'],
                'partner_id':m01,
                'pos_reference':yb['sn'],
                'lines':res,
                'state':'done',
                'buid':self._get_business().id,
                'strstoreid':yb['store_code'], 
                }
            master=self.env['pos.order'].create(vals)
        
        return True

      
def check_pos_data_daily(self,para_interval):
        vals=[]           
        end_date= datetime.datetime.now()        
        for i in range(1,para_interval+1):
            servercnt=0
            localcnt=0
            day= end_date - datetime.timedelta(days=i)
            print day              
            exec_sql=""" 
                        select count(*)  from pos_order 
                        where to_char(date_order,'yyyy-mm-dd')='{0}' and buid ={1} 
                    """
            exec_sql=exec_sql.format(day.strftime('%Y-%m-%d'),self._get_business().id)  
            cr = self._cr 
            cr.execute(exec_sql)
            
            for local_count  in cr.fetchall():
                localcnt=local_count[0]
 
#            cr1 = self._cr 
                                                        
            remote_exec_sql=""" 
                        select count(*)  from bn_yinbao_order 
                        where to_char(sale_datetime,'yyyy-mm-dd')='{0}' 
                    """
            remote_exec_sql=remote_exec_sql.format(day.strftime('%Y-%m-%d')) 
            remote_cnt = cr.execute(remote_exec_sql)
            
            for rcnt in cr.fetchall():   
                servercnt= rcnt[0]
            

            vals.append({'proc_date':day.strftime('%Y-%m-%d'),'local_records_count':localcnt,'remote_records_count':servercnt})       

        return vals
    
def bnc_split_group(lst, n):
    num = len(lst) % n
    zipped = zip(*[iter(lst)] * n)
    return zipped if not num else zipped + [lst[-num:], ]


def bnc_split_by_date():
    res=[]
    
    vals=[]

    list=[]
    for i in range(TOTAL_DAY):
#         print TOTAL_DAY -i 
         list.append(TOTAL_DAY -i)
    result = bnc_split_group(list, SPLIT_NUMBER)
    for tmp in result:
         max_value=tmp[0]
         min_value=tmp[len(tmp)-1]
         print max_value,min_value
         val={'max':max_value,'min':min_value}
         res.append(val)
    vals.append(res[1])    
#    vals.append(res[2])    
#    vals.append(res[3])    
    return res        

#    return vals        
    
# -*- coding: utf-8 -*-
import logging
import threading
import datetime

from odoo import api, models, tools, registry
from BNmssql import  bn_SQLCa



#from idlelib.SearchEngine import get

_logger = logging.getLogger(__name__)
TOTAL_DAY=10

class proc_sync_jsport(models.TransientModel):
    _name = 'proc.sync.buynow'
    _description = 'sync.buynow'
    
    #获取事业部代码
    @api.model    
    def _get_business(self):
        res=self.env['bnc.business'].get_bnc_business_bycode('bn')  
        return res  
    
    
    def sync_buynow(self):
        print 'sync_buynow'
        return True           


    
    def sync_product_class_all_branch(self):
        print 'sync_product_class_all_branch'
        
        for db in self.env['bn.db.connect'].search([('bu_code', '=',self._get_business()['strBuscode'])]):
            list=self.get_product_class_recordset(bn_SQLCa(db),self.env['res.company'].search_bycode(db['store_code']).id)
            self.sync_product_class(list,db['store_code'])
            self.set_bn_category_parent(db['store_code'])
        return True  

    
    def sync_product_brand_all_branch(self):
        print 'sync_product_brand_all_branch'
        
        for db in self.env['bn.db.connect'].search([('bu_code', '=',self._get_business()['strBuscode'])]):
            list=self.get_product_brand_recordset(bn_SQLCa(db),db['store_code'])
#            self.sync_product_brand(list,db['store_code'])
#            self.set_bn_category_parent(db['store_code'])
        return True  

    def sync_supplier_all_branch(self):
        print 'sync_supplier_all_branch'
        
        for db in self.env['bn.db.connect'].search([('bu_code', '=',self._get_business()['strBuscode'])]):
            list=self.get_supplier_recordset(bn_SQLCa(db),db['store_code'])
            self.sync_supplier(list,db['store_code'])
#            self.set_bn_category_parent(db['store_code'])
        return True  


    def sync_product_all_branch(self):
        print 'sync_product_all_branch'
        
        for db in self.env['bn.db.connect'].search([('bu_code', '=',self._get_business()['strBuscode'])]):
            list=self.get_product_recordset(bn_SQLCa(db),db['store_code'])
            self.sync_product(list,db['store_code'])
#            self.set_bn_category_parent(db['store_code'])
        return True  


    def sync_pos_data_all_branch(self):
        print 'sync_pos_data_all_branch'
        #proc_days 往前处理几天
        proc_days=TOTAL_DAY
        for db in self.env['bn.db.connect'].search([('bu_code', '=',self._get_business()['strBuscode'])]):
            proc_date_task=self.check_pos_data_daily(bn_SQLCa(db),db['store_code'],proc_days)
#            if db['store_code'] =='02002':
            for d in proc_date_task:
                    if d['local_records_count'] <> d['remote_records_count']:                
                       print db['store_code']+ d['proc_date'] +'====>'+'local have'+str(d['local_records_count'])+'==>remote have'+str(d['remote_records_count'])+'==>need to sync'
                       _logger.info(db['store_code']+ d['proc_date'] +'====>'+'local have'+str(d['local_records_count'])+'==>remote have'+str(d['remote_records_count'])+'==>need to sync')          

                       self.delete_pos_data_daily(d['proc_date'],db['store_code'])
                       self.insert_pos_data_daily(bn_SQLCa(db),d['proc_date'],d['proc_date'],db['store_code']) 
                    else :                                  
                       print db['store_code']+d['proc_date'] +'====>'+'already done!!!'
                       _logger.info(db['store_code']+d['proc_date'] +'====>'+'already done!!!')
        return True  

    
    def delete_pos_data_daily(self,ymd,store_code):
            exec_sql=""" 
                        delete from pos_order 
                        where to_char(date_order,'yyyy-mm-dd')='{0}' and buid ={1}  and strstoreid='{2}'
                    """
            exec_sql=exec_sql.format(ymd,self._get_business().id,store_code)  
            cr = self._cr 
            cr.execute(exec_sql)
            return True
                
 
    
    def insert_pos_data_daily(self,ms,begin,end,store_code):
        #begin 和end之间的日期资料导入
        sql = """ 
            SELECT  bs.BraId,bs.saleid ,bs.MemCardNo,min(DATEADD(hour,-8,bs.SaleDate)) as saledate 
            FROM sale  bs
            where saledate between '{0}' and '{1}'
            group by  bs.BraId,bs.saleid,bs.MemCardNo ,salerid
            order by braid,saleid,min(DATEADD(hour,-8,bs.SaleDate))
             """
        sql = sql.format(begin+' 00:00:00',end+' 23:59:59')    
        pos_order_list =ms.ExecQuery(sql.encode('utf-8'))
        _logger.info("bnc=>buynow insert_pos_data_daily  total records have %d " % len(pos_order_list)) 
        _logger.info("bnc=>buynow insert_pos_data_daily  using  %s " % sql)   
             
        for (braid, saleid, memb_id,saledate_order) in pos_order_list:
            vals=[]
            res=[]
            if  braid :
                br01=self.env['res.company'].search_bycode(braid).id
            else :
                br01 = None
                
            if  memb_id :
                m01=self.env['res.partner'].search_bycardid(memb_id).id
            else :
                m01=None
                
#            if  salerid:
#                s01=self.env['hr.employee'].search_bycode(salerid).id
#            else :
                s01=None

            sql_order_line = """ 
            SELECT   bs.saleman,DATEADD(hour,-8,bs.SaleDate) AS SaleDate,bs.proid,bs.SaleQty,
                     bs.NormalPrice,bs.curprice,bs.SaleType,bs.PosNo
            FROM     sale  bs
            where    saleid='{0}'             
            """
            sql_order_line = sql_order_line.format(saleid)            
            pos_order_line= ms.ExecQuery(sql_order_line.encode('utf-8'))
 
            for (saleman, saledate_detail,proid,SaleQty,NormalPrice,curprice,SaleType,PosNo) in pos_order_line:
                
                inter_pcode=self._get_business()['strBuscode']+'-'+ store_code+'-'+ proid
                res.append((0,0,{
                    'product_id':self.env['product.product'].search([('default_code', '=',inter_pcode)]).id,
                    'price_unit':curprice,
                    'qty':SaleQty, 
#                    'lngsaleid':self.env['hr.employee'].search_bycode(saleman).id,
                    }))
                

            vals={
                'date_order': saledate_order,
                'company_id': br01,
                'user_id':self.env['res.users'].search([('login', '=','buynow-users')]).id,
                'note':self._get_business()['strBuscode']+'-'+braid+'-'+saleid,
                'partner_id':m01,
                'pos_reference':self._get_business()['strBuscode']+'-'+braid+'-'+saleid,
                'lines':res,
                'state':'done',
                'buid':self._get_business().id,
                'strstoreid':braid, 
#                'lngcasherid':s01,                
                }
#            print saleid
#            print inter_pcode
#            print res
#            print vals
            master=self.env['pos.order'].create(vals)
        
        return True


    @api.model  
    def get_product_recordset(self,ms,store_code):
        #获取更新记录范围，本地库的时间戳和服务端时间戳
        local_sql=""" 
                    select max(timestamp) AS timestamp from product_template where buid = {0} and store_id ={1}
                  """
        local_sql=local_sql.format(self._get_business()['id'],self.env['res.company'].search_bycode(store_code).id) 

        remote_sql= "select CONVERT (int,max(timestamp)) as timestamp  from product"
        btw=self.query_period(ms,local_sql,remote_sql)
          
        #获取更新记录   
        sql = """ 
               select  ProId,Barcode,cast(ProName as nvarchar(100)) as name,cast(spec as nvarchar(100)) as spec,
                       ClassId,SupId,isnull(NormalPrice,0),BrandId,CONVERT (int,timestamp) as timestamp  
               from product
               where  CONVERT(INT,timestamp) between {0} and {1}
               order by CONVERT (int,timestamp)
                  """
        sql = sql.format(btw['start_stamp'],btw['end_stamp'])  
        print sql 
        res = ms.ExecQuery(sql.encode('utf-8'))        
        return res


    @api.model  
    def get_supplier_recordset(self,ms,store_code):
        #获取事业部代码

           #获取更新记录范围，本地库的时间戳和服务端时间戳
        local_sql=""" 
                    select max(timestamp) AS timestamp from buynow_supplier where buid = {0} and store_id ={1}
                  """
        local_sql=local_sql.format(self._get_business()['id'],self.env['res.company'].search_bycode(store_code).id) 
                          
        remote_sql= "select CONVERT (int,max(timestamp)) as timestamp  from supplier"
        btw=self.query_period(ms,local_sql,remote_sql)
          
        #获取更新记录   
        sql = """ 
               select SupId,cast(SupName as nvarchar(100)) as name,cast(Addr as nvarchar(100)) as addr,
                   Tel,Fax,Zip,Email,CONVERT (int,timestamp) as timestamp  
               from supplier
               where  CONVERT(INT,timestamp) between {0} and {1}
                  """
        sql = sql.format(btw['start_stamp'],btw['end_stamp'])       
        res = ms.ExecQuery(sql.encode('utf-8'))        
        return res
    

    @api.model  
    def get_product_brand_recordset(self,ms,store_code):
        #获取事业部代码
        d01=self._get_business()

        #获取更新记录范围，本地库的时间戳和服务端时间戳
        local_sql=""" 
                    select max(timestamp) AS timestamp from product_brand where buid = {0} and store_id ={1}
                  """
        local_sql=local_sql.format(self._get_business()['id'],self.env['res.company'].search_bycode(store_code).id) 

        remote_sql= "SELECT CONVERT(INT,max(timestamp)) AS timestamp from product_brand"
        btw=self.query_period(ms,local_sql,remote_sql)
          
        #获取更新记录   
        sql = """ 
               select brandId,cast(brandName as nvarchar(100)) as name,CONVERT(INT,timestamp) AS timestamp from product_brand
               where  CONVERT(INT,timestamp) between {0} and {1}
                  """
        sql = sql.format(btw['start_stamp'],btw['end_stamp'])     
        res = ms.ExecQuery(sql.encode('utf-8'))        
        return res


    @api.model  
    def get_product_class_recordset(self,ms,storeid):
        #获取事业部代码

        #获取更新记录范围，本地库的时间戳和服务端时间戳
        local_sql=""" 
                    select max(timestamp) AS timestamp from product_category where buid = {0} and store_id ={1} 
                  """
        local_sql=local_sql.format(self._get_business()['id'],storeid) 
        
#        print local_sql

        remote_sql= "SELECT CONVERT(INT,max(timestamp)) AS timestamp from product_class"
        
#        print remote_sql
        
        btw=self.query_period(ms,local_sql,remote_sql)
          
        #获取更新记录   
        sql = """ 
               select ClassId,cast(ClassName as nvarchar(100)) as name,CONVERT(INT,timestamp) AS timestamp from product_class
               where  CONVERT(INT,timestamp) between {0} and {1}
                  """
        sql = sql.format(btw['start_stamp'],btw['end_stamp']) 
        print sql    
        res = ms.ExecQuery(sql.encode('utf-8'))        
        return res


    
    def proc_check_pos_data_weekly(self):
        #check_pos_data_daily(7) 7表示一周   
        proc_date_task = self.check_pos_data_daily(TOTAL_DAY)
        _logger.info(" bnc =>buynow  proc_check_pos_data_weekly  TOTAL_DAY IS %d " % TOTAL_DAY)          
          
        for d in proc_date_task:
            if d['local_records_count'] <> d['remote_records_count']:
               _logger.info("bnc=>buynow proc_check_pos_data_weekly" +  d['proc_date'] +'====>'+'local have'+str(d['local_records_count'])+'==>remote have'+str(d['remote_records_count'])+'==>need to sync')  
               print d['proc_date'] +'====>'+'local have'+str(d['local_records_count'])+'==>remote have'+str(d['remote_records_count'])+'==>need to sync'
               self.delete_pos_data_daily(d['proc_date'])
               self.insert_pos_data_daily(d['proc_date'],d['proc_date']) 
            else :
               _logger.info("bnc=>buynow proc_check_pos_data_weekly" +  d['proc_date'] ++'====>'+'already done!!!')  
               print d['proc_date'] +'====>'+'already done!!!'
        
        return True


    
    def proc_sync_buynow_all(self):
        self.env['proc.sync.buynow'].sync_product_class_all_branch()
        self.env['proc.sync.buynow'].sync_product_brand_all_branch()
        self.env['proc.sync.buynow'].sync_supplier_all_branch()
        self.env['proc.sync.buynow'].sync_product_all_branch()
        self.env['proc.sync.buynow'].sync_pos_data_all_branch()        
        return True


    @api.multi
    def check_pos_data_daily(self,ms,store_code,para_interval):
        vals=[]           
        end_date= datetime.datetime.now()        
        for i in range(1,para_interval+1):
            servercnt=0
            localcnt=0
            day= end_date - datetime.timedelta(days=i)
            print day              
            exec_sql=""" 
                        select count(*)  from pos_order 
                        where to_char(date_order,'yyyy-mm-dd')='{0}' and buid ={1} and strstoreid='{2}'
                    """
            exec_sql=exec_sql.format(day.strftime('%Y-%m-%d'),self._get_business().id,store_code)  
            cr = self._cr 
            cr.execute(exec_sql)
            
            remote_exec_sql=""" 
                    select count(*)  from (
                    SELECT  bs.BraId,bs.saleid ,bs.MemCardNo,min(DATEADD(hour,-8,bs.SaleDate)) as saledate 
                                FROM sale  bs
                                where datediff(day,saledate,'{0}')=0
                                group by  bs.BraId,bs.saleid,salerid,bs.MemCardNo
                                 ) a
                    """
            remote_exec_sql=remote_exec_sql.format(day) 
            remote_cnt = ms.ExecQuery(remote_exec_sql.encode('utf-8'))
            
            for rcnt in remote_cnt:   
                servercnt= remote_cnt[0]
            
            for local_count  in cr.fetchall():
                localcnt=local_count[0]
                                
            vals.append({'proc_date':day.strftime('%Y-%m-%d'),'local_records_count':localcnt,'remote_records_count':servercnt[0]})       

        return vals

    
    def sync_product(self,product_list,store_code):
        #获取待更新记录   
        for (proid,barcode, name,spec,classid,supid,normalprice,brandid, timestamp) in product_list:
            #封装product.category记录

#            b01=self.env['product.brand'].search_bycode(store_code+'-'+brandid).id
#            if not b01 :
            b01=None
            tmp_code=self._get_business()['strBuscode']+'-'+store_code+'-'+proid
            
            s01=self.env['buynow.supplier'].search_bycode(store_code+'-'+supid)
            
            res= {
                'code' : tmp_code,
                'name' : store_code+'-'+name,
                'spec':spec,
                'brand_id':b01,
                'list_price':normalprice,
                'price':normalprice,
                'bn_barcode':tmp_code,
                'sale_ok':True,
                'default_code':tmp_code,
                'categ_id':self.env['product.category'].search_bycode(store_code+'-'+classid).id,
                'b_category':self.env['product.category'].search_bycode(store_code+'-'+classid[0:4]).id,
                'm_category':self.env['product.category'].search_bycode(store_code+'-'+classid[0:6]).id,
                'b_sup_id':s01.id,
                'timestamp': timestamp,
                'buid':self._get_business()['id'],
                'store_id':self.env['res.company'].search_bycode(store_code).id,             
                }
            #检查是插入还是更新            
            r01=self.env['product.template'].search_bycode(tmp_code)
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



    
    def sync_supplier(self,supplier_list,store_code):
        #获取待更新记录   
        for (supid,name,addr,tel,fax,zip,email,timestamp) in supplier_list:
            #封装product.category记录
            vals={
                'name': store_code+'-'+supid+'-'+name,
                'phone': tel,
                'is_company': True,
                'strbnctype':'supplier',                
                'supplier': True,
                'customer': False,}

            #检查是插入还是更新            
            r01=self.env['buynow.supplier'].search_bycode(store_code+'-'+supid)
            if r01:            
                 self.env['buynow.supplier'].write( {
                        'supid' : store_code+'-'+supid,
                        'name' : name,
                        'address' : addr,
                        'telephone' : tel,   
                        'email' : email,   
                        'fax' : fax,   
                        'zip' : zip,   
                        'timestamp': timestamp,
                        'buid':self._get_business()['id'],
                        'store_id':self.env['res.company'].search_bycode(store_code).id,
                        'resid':self.env['res.partner'].write(vals),
                        })

            else:
                 self.env['buynow.supplier'].create( {
                        'supid' : store_code+'-'+supid,
                        'name' : name,
                        'address' : addr,
                        'telephone' : tel,   
                        'email' : email,   
                        'fax' : fax,   
                        'zip' : zip,   
                        'timestamp': timestamp,
                        'buid':self._get_business()['id'],
                        'store_id':self.env['res.company'].search_bycode(store_code).id,
                        'resid':self.env['res.partner'].create(vals).id,
                        })
        return True    
    
    
    def sync_product_class(self,para_product_class,store_code):
        #获取待更新记录   
        for (classid,name,timestamp) in para_product_class:
            #封装product.category记录
            res= {
                'code' : store_code+'-'+classid,
                'name' : name,
                'timestamp': timestamp,
                'buid':self._get_business()['id'],
                'store_id':self.env['res.company'].search_bycode(store_code).id,
                
                }
            #检查是插入还是更新            
            r01=self.env['product.category'].search_bycode(store_code+'-'+classid)
            if r01:            
                self.env['product.category'].write(res)
                self.env['pos.category'].write(res)
            else:
                self.env['product.category'].create(res)
                self.env['pos.category'].create(res)     
#        self.set_jsport_category_parent()    

        return True
    
    
    def set_bn_category_parent(self,store_code):
        
        #检查根分类             
        self.check_bn_category_root(store_code)
        
        #大分类      
        posroot=self.get_bn_pos_category_current_recordset(0,store_code)
        self.exec_set_bn_pos_category_parent(posroot,0,store_code)
                
        productroot=self.get_bn_product_category_current_recordset(0,store_code)  
        self.exec_set_bn_product_category_parent(productroot,0,store_code)        

        #中分类
        postoplevel=self.get_bn_pos_category_current_recordset(10,store_code)
        self.exec_set_bn_pos_category_parent(postoplevel,10,store_code)
        producttoplevel=self.get_bn_product_category_current_recordset(10,store_code)      
        self.exec_set_bn_product_category_parent(producttoplevel,10,store_code)
        
        #小分类
        posmidlevel=self.get_bn_pos_category_current_recordset(12,store_code)
        self.exec_set_bn_pos_category_parent(posmidlevel,12,store_code)
        productmidlevel=self.get_bn_product_category_current_recordset(12,store_code)    
        self.exec_set_bn_product_category_parent(productmidlevel,12,store_code)
        
        return True
    
    @api.multi
    def get_bn_pos_category_current_recordset(self,lens,store_code):

        if lens <> 0 :
            select_sql=""" 
                        select id,code from pos_category where length(code)='{0}' and store_id={1} and buid={2}
                      """
            select_sql=select_sql.format(lens,self.env['res.company'].search_bycode(store_code).id,self._get_business()['id'])  
        else:
            select_sql=""" 
                        select id,code from pos_category where code='{0}' and store_id={1} and buid={2} 
                      """
            select_sql=select_sql.format(store_code,self.env['res.company'].search_bycode(store_code).id,self._get_business()['id']) 
                     
#        print select_sql     
        cr = self._cr         
        cr.execute(select_sql)
        res=cr.fetchall()
        return res
    
    @api.multi
    def get_bn_product_category_current_recordset(self,lens,store_code):
     
        if lens <> 0 :
            select_sql=""" 
                        select id,code from product_category where length(code)='{0}' and store_id={1} and buid={2}
                      """
            select_sql=select_sql.format(lens,self.env['res.company'].search_bycode(store_code).id,self._get_business()['id'])  
        else :
            select_sql=""" 
                        select id,code from product_category where code='{0}' and store_id={1} and buid={2} 
                      """
            select_sql=select_sql.format(store_code,self.env['res.company'].search_bycode(store_code).id,self._get_business()['id']) 
#        print select_sql        
        cr = self._cr         
        cr.execute(select_sql)
        res=cr.fetchall()
        return res
        
    
    def check_bn_category_root(self,store_code):
        #设置事业部
#        r01=self.env['product.category'].search_bycode(self._get_business()['strBuscode'])
        if not self.env['product.category'].search_bycode(self._get_business()['strBuscode']):
            res= {
                'code' : self._get_business()['strBuscode'],
                'name' : self._get_business()['strBusName'],
                'buid':self._get_business()['id'],

                }
            pd=self.env['product.category'].create(res).id
            pc=self.env['pos.category'].create(res).id
        else:
            pd=self.env['product.category'].search_bycode(self._get_business()['strBuscode']).id
            pc=self.env['pos.category'].search_bycode(self._get_business()['strBuscode']).id           
        #设置门店分类    
#        r02=self.env['product.category'].search_bycode(store_code)
        if not self.env['product.category'].search_bycode(store_code):
            val1= {
                'code' : store_code,
                'name' : self.env['res.company'].search_bycode(store_code)['name'],
                'buid':self._get_business()['id'],
                'parent_id':pd,
                'store_id':self.env['res.company'].search_bycode(store_code).id,
                }

            val2= {
                'code' : store_code,
                'name' : self.env['res.company'].search_bycode(store_code)['name'],
                'buid':self._get_business()['id'],
                'parent_id':pc,
                'store_id':self.env['res.company'].search_bycode(store_code).id,
                }
            
            self.env['product.category'].create(val1)
            self.env['pos.category'].create(val2)     
            
            
        return True
    
    
    def exec_set_bn_pos_category_parent(self,vals,lens,store_code):
        for (parentid,code) in vals:
            if lens <> 0 :
                    sublens=lens+2
                    exec_sql=""" 
                                update pos_category set parent_id={0} where length(code)={1}  and substr(code,1,{2})='{3}'
                                 and  buid={4} and store_id={5}
                              """
                    exec_sql=exec_sql.format(parentid,sublens,lens,code,self._get_business()['id'],self.env['res.company'].search_bycode(store_code).id)  
            else:
                    exec_sql=""" 
                                update pos_category set parent_id={0} where length(code)=10  and  buid={1} and store_id={2}
    
                              """
                    exec_sql=exec_sql.format(parentid,self._get_business()['id'],self.env['res.company'].search_bycode(store_code).id)
#            print exec_sql  
            cr = self._cr 
            cr.execute(exec_sql)
        return  True
    
    
    def exec_set_bn_product_category_parent(self,vals,lens,store_code):
        for (parentid,code) in vals:
            if lens <> 0 :        
                        sublens=lens+2
                        exec_sql=""" 
                                    update product_category set parent_id={0} where length(code)={1}  and substr(code,1,{2})='{3}'
                                     and  buid={4} and store_id={5}
                                  """
                        exec_sql=exec_sql.format(parentid,sublens,lens,code,self._get_business()['id'],self.env['res.company'].search_bycode(store_code).id)  

            else:
                        exec_sql=""" 
                                    update product_category set parent_id={0}  where length(code)=10  and  buid={1} and store_id={2}
        
                                  """
                        exec_sql=exec_sql.format(parentid,self._get_business()['id'],self.env['res.company'].search_bycode(store_code).id) 
#            print exec_sql   
            cr = self._cr 
            cr.execute(exec_sql)
        return  True
                
        
    @api.multi    
    def query_period(self,ms,local,remote):        
        start_stamp=0
        end_stamp=0
        query_local = local
        query_remote = remote
        cr = self._cr 
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp=local_max_num[0]
            if local_max_num[0] is None:
                    start_stamp=0
        return_start=start_stamp
               

        remote_stamp = ms.ExecQuery(query_remote.encode('utf-8'))
        for remote_max_num in remote_stamp:
            end_stamp = remote_max_num[0]
            if remote_max_num[0] is None:
                    end_stamp=0
                    
        return_end=end_stamp
        
        res= {
            'start_stamp': return_start,
            'end_stamp': return_end,
        }
        return res        
        
              
        
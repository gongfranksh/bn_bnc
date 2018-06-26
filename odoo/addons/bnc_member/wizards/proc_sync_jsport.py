# -*- coding: utf-8 -*-
import logging
import threading
import datetime

from odoo import api, models, tools, registry
from BNmssql import Lz_read_SQLCa

# from idlelib.SearchEngine import get

_logger = logging.getLogger(__name__)

TOTAL_DAY = 10


class proc_sync_jsport(models.TransientModel):
    _name = 'proc.sync.jsport'
    _description = 'sync.jsport'

    # 获取事业部代码
    @api.model
    def _get_business(self):
        res = self.env['bnc.business'].get_bnc_business_bycode('jsp')
        return res

    @api.model
    def get_product_class_recordset(self):
        # 获取事业部代码
        d01 = self._get_business()

        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        local_sql = """ 
                    select max(timestamp) AS timestamp from product_category where buid = {0}
                  """
        local_sql = local_sql.format(d01['id'])

        remote_sql = "SELECT CONVERT(INT,max(timestamp)) AS timestamp from product_class "
        btw = self.query_period(local_sql, remote_sql)

        # 获取更新记录
        sql = """ 
               select ClassId,cast(ClassName as nvarchar(100)) as name,CONVERT(INT,timestamp) AS timestamp from product_class
               where  CONVERT(INT,timestamp) between {0} and {1}
                  """
        sql = sql.format(btw['start_stamp'], btw['end_stamp'])
        ms = Lz_read_SQLCa(self)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    @api.model
    def get_product_brand_recordset(self):
        # 获取事业部代码
        d01 = self._get_business()

        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        local_sql = """ 
                    select max(timestamp) AS timestamp from product_brand where buid = {0}
                  """
        local_sql = local_sql.format(d01['id'])

        remote_sql = "SELECT CONVERT(INT,max(timestamp)) AS timestamp from product_brand"
        btw = self.query_period(local_sql, remote_sql)

        # 获取更新记录
        sql = """ 
               select brandId,cast(brandName as nvarchar(100)) as name,CONVERT(INT,timestamp) AS timestamp from product_brand
               where  CONVERT(INT,timestamp) between {0} and {1}
                  """
        sql = sql.format(btw['start_stamp'], btw['end_stamp'])
        ms = Lz_read_SQLCa(self)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    @api.model
    def get_employee_recordset(self):
        # 获取事业部代码
        d01 = self._get_business()

        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        local_sql = """ 
                    select max(timestamp) AS timestamp from hr_employee where buid = {0}
                  """
        local_sql = local_sql.format(d01['id'])

        remote_sql = "SELECT CONVERT(INT,max(timestamp)) AS timestamp from branch_employee"
        btw = self.query_period(local_sql, remote_sql)

        # 获取更新记录
        sql = """ 
                select a.* from 
                    (SELECT be.EmpId,cast(be.EmpName as nvarchar(100)) as name,CONVERT(INT,max(timestamp)) AS timestamp 
                    FROM branch_employee be
                    group by be.EmpId,be.EmpName ) a
                 where  a.timestamp between {0} and {1}
                  """
        sql = sql.format(btw['start_stamp'], btw['end_stamp'])
        ms = Lz_read_SQLCa(self)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    @api.model
    def get_supplier_recordset(self):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        local_sql = """ 
                    select max(timestamp) AS timestamp from jsport_supplier
                  """
        remote_sql = "select CONVERT (int,max(timestamp)) as timestamp  from supplier"
        btw = self.query_period(local_sql, remote_sql)

        # 获取更新记录
        sql = """ 
               select SupId,cast(SupName as nvarchar(100)) as name,cast(Addr as nvarchar(100)) as addr,
                   Tel,Fax,Zip,Email,CONVERT (int,timestamp) as timestamp  
               from supplier
               where  CONVERT(INT,timestamp) between {0} and {1}
                  """
        sql = sql.format(btw['start_stamp'], btw['end_stamp'])
        ms = Lz_read_SQLCa(self)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    @api.model
    def get_product_recordset(self):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        local_sql = """ 
                    select max(timestamp) AS timestamp from product_template where buid = {0}
                  """
        local_sql = local_sql.format(self._get_business()['id'])

        remote_sql = "select CONVERT (int,max(timestamp)) as timestamp  from product"
        btw = self.query_period(local_sql, remote_sql)

        # 获取更新记录
        sql = """ 
               select  ProId,Barcode,cast(ProName as nvarchar(100)) as name,cast(spec as nvarchar(100)) as spec,
                       ClassId,SupId,isnull(NormalPrice,0),BrandId,CONVERT (int,timestamp) as timestamp  
               from product
               where  CONVERT(INT,timestamp) between {0} and {1}
               order by CONVERT (int,timestamp)
                  """
        sql = sql.format(btw['start_stamp'], btw['end_stamp'])
        ms = Lz_read_SQLCa(self)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    #
    def sync_product_class(self):
        bu_tmp = self._get_business()
        # 获取待更新记录
        jspot_product_class_list = self.get_product_class_recordset()
        for (classid, name, timestamp) in jspot_product_class_list:
            # 封装product.category记录
            res = {
                'code': classid,
                'name': name,
                'timestamp': timestamp,
                'buid': bu_tmp['id'],
            }
            # 检查是插入还是更新
            r01 = self.env['product.category'].search_bycode(classid)
            if r01:
                self.env['product.category'].write(res)
                self.env['pos.category'].write(res)
            else:
                self.env['product.category'].create(res)
                self.env['pos.category'].create(res)
        self.set_jsport_category_parent()

        return True

    #
    def sync_product_brand(self):
        bu_tmp = self._get_business()
        # 获取待更新记录
        jspot_product_brand_list = self.get_product_brand_recordset()
        for (brandid, name, timestamp) in jspot_product_brand_list:
            # 封装product.category记录
            res = {
                'code': brandid,
                'name': name,
                'timestamp': timestamp,
                'buid': bu_tmp['id'],

            }
            # 检查是插入还是更新
            r01 = self.env['product.brand'].search_bycode(brandid)
            if r01:
                self.env['product.brand'].write(res)
            else:
                self.env['product.brand'].create(res)
        return True

    #
    def sync_employee(self):
        bu_tmp = self._get_business()
        # 获取待更新记录
        jspot_employee_list = self.get_employee_recordset()
        for (empid, name, timestamp) in jspot_employee_list:
            # 封装product.category记录
            res = {
                'code': empid,
                'name': name,
                'timestamp': timestamp,
                'buid': bu_tmp['id'],

            }
            # 检查是插入还是更新
            r01 = self.env['hr.employee'].search_bycode(empid)
            if r01:
                self.env['hr.employee'].write(res)
            else:
                self.env['hr.employee'].create(res)
        return True

    def sync_supplier(self):
        # 获取待更新记录
        jspot_supplier_list = self.get_supplier_recordset()
        for (supid, name, addr, tel, fax, zip, email, timestamp) in jspot_supplier_list:
            # 封装product.category记录
            vals = {
                'name': supid + '-' + name,
                'phone': tel,
                'is_company': True,
                'strbnctype': 'supplier',
                'supplier': True,
                'customer': False, }

            # 检查是插入还是更新
            r01 = self.env['jsport.supplier'].search_bycode(supid)
            if r01:
                self.env['jsport.supplier'].write({
                    'supid': supid,
                    'name': name,
                    'address': addr,
                    'telephone': tel,
                    'email': email,
                    'fax': fax,
                    'zip': zip,
                    'timestamp': timestamp,
                    'buid': self._get_business()['id'],
                    'resid': self.env['res.partner'].write(vals),
                })

            else:
                self.env['jsport.supplier'].create({
                    'supid': supid,
                    'name': name,
                    'address': addr,
                    'telephone': tel,
                    'email': email,
                    'fax': fax,
                    'zip': zip,
                    'timestamp': timestamp,
                    'buid': self._get_business()['id'],
                    'resid': self.env['res.partner'].create(vals).id,
                })
        return True

    def sync_pos_machine(self):
        # 获取待更新记录
        # 获取更新记录
        sql = """ 
               
                select braid,posno  from pos_machine
             """
        sql = sql.format()
        ms = Lz_read_SQLCa(self)
        pos_mahcine_list = ms.ExecQuery(sql.encode('utf-8'))
        for (braid, posno) in pos_mahcine_list:
            # 封装product.category记录
            vals = {
                'name': braid + '-' + posno,
                #                'company_id':self.env['res.company'].search_bycode(braid).id
            }

            # 检查是插入还是更新
            r01 = self.env['pos.config'].search([('name', '=', braid + '-' + posno)])
            if not r01:
                self.env['pos.config'].create(vals)
        return True

    #
    def sync_pos_data(self):
        # 获取待更新记录
        # 获取更新记录
        date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        startdate = datetime.datetime.now()
        para_interval = 66

        #        self.check_pos_data(startdate,para_interval)

        self.check_pos_data_weekly()

        sql = """ 
            SELECT  bs.BraId,bs.saleid,bs.memb_id ,salerid,saleflag,min(DATEADD(hour,-8,bs.SaleDate)) as saledate 
            FROM v_bn_saledetail  bs
            where datediff(day,saledate,'{0}')<={1}
            group by  bs.BraId,bs.saleid,bs.memb_id ,salerid,saleflag   
            order by braid,saleid,min(DATEADD(hour,-8,bs.SaleDate))
             """
        sql = sql.format(date, para_interval)
        ms = Lz_read_SQLCa(self)
        pos_order_list = ms.ExecQuery(sql.encode('utf-8'))
        _logger.info(" bnc =>jspot  sync_pos_data total have %d records need to sync" % len(pos_order_list))
        _logger.info(" bnc =>jspot  sync_pos_data using  %s sql" % sql)
        for (braid, saleid, memb_id, salerid, saleflag, saledate_order) in pos_order_list:
            sql_order_line = """ 
            SELECT   bs.saleman,DATEADD(hour,-8,bs.SaleDate) AS SaleDate,bs.proid,bs.SaleQty,
                     bs.NormalPrice,bs.curprice,bs.amount,bs.SaleType,bs.PosNo,bs.profit 
            FROM     v_bn_saledetail  bs 
            where    saleid='{0}'             
            """
            vals = []
            res = []
            if braid:
                br01 = self.env['res.company'].search_bycode(braid).id
            else:
                br01 = None

            if memb_id:
                m01 = self.env['res.partner'].search_bycardid(memb_id).id
            else:
                m01 = None

            if salerid:
                s01 = self.env['hr.employee'].search_bycode(salerid).id
            else:
                s01 = None

            sql_order_line = sql_order_line.format(saleid)
            pos_order_line = ms.ExecQuery(sql_order_line.encode('utf-8'))

            for (saleman, saledate_detail, proid, SaleQty, NormalPrice, curprice, amount, SaleType, PosNo,
                 profit) in pos_order_line:
                res.append((0, 0, {
                    'product_id': self.env['product.template'].search_bycode(
                        self._get_business()['strBuscode'] + '-' + proid).id,
                    'price_unit': curprice,
                    'qty': SaleQty,
                    'lngsaleid': self.env['hr.employee'].search_bycode(saleman).id,
                }))
            vals = {
                'date_order': saledate_order,
                'company_id': br01,
                'user_id': self.env['res.users'].search([('login', '=', 'jspot-users')]).id,
                'note': self._get_business()['strBuscode'] + '-' + braid + '-' + saleid,
                'partner_id': m01,
                'pos_reference': self._get_business()['strBuscode'] + '-' + braid + '-' + saleid,
                'lines': res,
                'state': 'done',
                'buid': self._get_business().id,
                'strstoreid': braid,
                'lngcasherid': s01,
            }
            master = self.env['pos.order'].create(vals)
        return True

    #
    def sync_product(self):
        # 获取待更新记录

        jspot_product_list = self.get_product_recordset()
        _logger.info(" bnc =>jspot sync_product_jspot  total have %d records need to sync" % len(jspot_product_list))
        for (proid, barcode, name, spec, classid, supid, normalprice, brandid, timestamp) in jspot_product_list:
            # 封装product.category记录

            b01 = self.env['product.brand'].search_bycode(brandid).id
            if not b01:
                b01 = None

            s01 = self.env['jsport.supplier'].search_bycode(supid)

            res = {
                'code': self._get_business()['strBuscode'] + '-' + proid,
                'name': name,
                'spec': spec,
                'brand_id': b01,
                'list_price': normalprice,
                'price': normalprice,
                'bn_barcode': barcode,
                'sale_ok': True,
                'default_code': self._get_business()['strBuscode'] + '-' + proid,
                'categ_id': self.env['product.category'].search_bycode(classid).id,
                'b_category': self.env['product.category'].search_bycode(classid[0:4]).id,
                'm_category': self.env['product.category'].search_bycode(classid[0:6]).id,
                'sup_id': self.env['jsport.supplier'].search_bycode(supid).id,
                'timestamp': timestamp,
                'buid': self._get_business()['id'],
            }
            # 检查是插入还是更新
            r01 = self.env['product.template'].search_bycode(self._get_business()['strBuscode'] + '-' + proid)
            if r01:
                self.env['product.template'].write(res)
            else:
                self.env['product.template'].create(res)
        #        self.set_jsport_category_parent()

        return True

    #
    def _sync_jsport(self):
        self.env['proc.sync.jsport'].sync_product_class()
        self.env['proc.sync.jsport'].sync_product_brand()
        self.env['proc.sync.jsport'].sync_employee()
        self.env['proc.sync.jsport'].sync_supplier()
        self.env['proc.sync.jsport'].sync_product()
        self.env['proc.sync.jsport'].sync_pos_machine()
        self.env['proc.sync.jsport'].proc_check_pos_data_weekly()
        return True

    @api.multi
    def procure_sync_jsport(self):

        #       bnc_member = self.env['bnc.member']
        #       bnc_member.sync_bnc_member
        #        threaded_calculation = threading.Thread(target=self.sync_bnc_member, args=())
        #        threaded_calculation.start()
        self.env['proc.sync.jsport']._sync_jsport()
        return {'type': 'ir.actions.act_window_close'}

    def check_pos_data(self, para_date, para_interval):

        start_date = (para_date - datetime.timedelta(days=para_interval)).strftime("%Y-%m-%d") + ' 00:00:00'
        end_date = datetime.datetime.now().strftime("%Y-%m-%d") + ' 23:59:59'
        proc_posorder_ids = self.env['pos.order'].search([('date_order', '>=', start_date),
                                                          ('date_order', '<=', end_date),
                                                          ('buid', '=', self._get_business().id),
                                                          ]),

        if len(proc_posorder_ids[0]) <> 0:
            print "find records nees to delete"
            exec_sql = """ 
                        delete from pos_order where buid={0} and date_order between '{1}' and '{2}'
                    """
            exec_sql = exec_sql.format(self._get_business()['id'], start_date, end_date)
            cr = self._cr
            cr.execute(exec_sql)

        return True

    @api.multi
    def check_pos_data_daily(self, para_interval):
        vals = []
        end_date = datetime.datetime.now()
        for i in range(0, para_interval + 1):
            servercnt = 0
            localcnt = 0
            day = end_date - datetime.timedelta(days=i)
            print day
            exec_sql = """ 
                        select count(*)  from pos_order 
                        where to_char(date_order,'yyyy-mm-dd')='{0}' and buid ={1}
                    """
            exec_sql = exec_sql.format(day.strftime('%Y-%m-%d'), self._get_business().id)
            cr = self._cr
            cr.execute(exec_sql)

            remote_exec_sql = """ 
                    select count(*)  from (
                    SELECT  bs.BraId,bs.saleid,bs.memb_id ,salerid,saleflag,min(DATEADD(hour,-8,bs.SaleDate)) as saledate 
                                FROM v_bn_saledetail  bs
                                where datediff(day,saledate,'{0}')=0 
                                group by  bs.BraId,bs.saleid,bs.memb_id ,salerid,saleflag   
                                 ) a
                    """
            remote_exec_sql = remote_exec_sql.format(day)
            ms = Lz_read_SQLCa(self)
            remote_cnt = ms.ExecQuery(remote_exec_sql.encode('utf-8'))

            for rcnt in remote_cnt:
                servercnt = remote_cnt[0]

            for local_count in cr.fetchall():
                localcnt = local_count[0]

            _logger.info(" bnc =>jspot  check_pos_data_daily ")
            _logger.info(" bnc =>jspot  check_pos_data_daily local using  %s  " % exec_sql)
            _logger.info(" bnc =>jspot  check_pos_data_daily remote using  %s  " % remote_exec_sql)
            #            if localcnt==servercnt:
            #                    print 'ok '
            #            else:
            #                    print day.strftime('%Y%m%d')+'===>'+str(local_count[0]) +'===>' +'Need to clean'
            vals.append({'proc_date': day.strftime('%Y-%m-%d'), 'local_records_count': localcnt,
                         'remote_records_count': servercnt[0]})

        return vals

#     def proc_check_pos_data_weekly(self):
#         # check_pos_data_daily(7) 7表示一周
#         # proc_date_task = self.check_pos_data_daily(1)
#         procdate='2018-06-25'
# #        for d in proc_date_task:
#         self.delete_pos_data_daily(procdate)
#         self.insert_pos_data_daily(procdate, procdate)
#         return True

    def proc_check_pos_data_weekly(self):
        # check_pos_data_daily(7) 7表示一周
        proc_date_task = self.check_pos_data_daily(TOTAL_DAY)
        _logger.info(" bnc jspot => proc_check_pos_data_weekly TOTAL_DAY is %d " % TOTAL_DAY)
        for d in proc_date_task:
            if d['local_records_count'] <> d['remote_records_count']:

                print d['proc_date'] + '====>' + 'local have' + str(d['local_records_count']) + '==>remote have' + str(
                    d['remote_records_count']) + '==>need to sync'
                _logger.info(
                    d['proc_date'] + '====>' + 'local have' + str(d['local_records_count']) + '==>remote have' + str(
                        d['remote_records_count']) + '==>need to sync')
                self.delete_pos_data_daily(d['proc_date'])
                self.insert_pos_data_daily(d['proc_date'], d['proc_date'])
            else:

                print d['proc_date'] + '====>' + 'already done!!!'
                _logger.info(d['proc_date'] + '====>' + 'already done!!!')

        return True


    def delete_pos_data_daily(self, ymd):
        exec_sql = """ 
                        delete from pos_order 
                        where to_char(date_order,'yyyy-mm-dd')='{0}' and buid ={1}
                    """
        exec_sql = exec_sql.format(ymd, self._get_business().id)
        cr = self._cr
        cr.execute(exec_sql)
        return True

    def insert_pos_data_daily(self, begin, end):
        # begin 和end之间的日期资料导入
        sql = """ 
            SELECT  bs.BraId,bs.saleid,bs.memb_id ,salerid,saleflag,min(DATEADD(hour,-8,bs.SaleDate)) as saledate 
            FROM v_bn_saledetail  bs
            where saledate between '{0}' and '{1}'
            group by  bs.BraId,bs.saleid,bs.memb_id ,salerid,saleflag   
            order by braid,saleid,min(DATEADD(hour,-8,bs.SaleDate))
             """
        sql = sql.format(begin + ' 00:00:00', end + ' 23:59:59')
        ms = Lz_read_SQLCa(self)
        pos_order_list = ms.ExecQuery(sql.encode('utf-8'))
        _logger.info(" bnc =>jspot  insert_pos_data_daily have %d records need to sync" % len(pos_order_list))
        _logger.info(" bnc =>jspot  insert_pos_data_daily  %s sql" % sql)
        for (braid, saleid, memb_id, salerid, saleflag, saledate_order) in pos_order_list:
            sql_order_line = """ 
            SELECT   bs.saleman,DATEADD(hour,-8,bs.SaleDate) AS SaleDate,bs.proid,bs.SaleQty,
                     bs.NormalPrice,bs.curprice,bs.amount,bs.SaleType,bs.PosNo,bs.profit 
            FROM     v_bn_saledetail  bs 
            where    saleid='{0}'             
            """
            vals = []
            res = []
            if braid:
                br01 = self.env['res.company'].search_bycode(braid).id
            else:
                br01 = None

            if memb_id:
#                print memb_id
                m01 = self.env['res.partner'].search_bycardid(memb_id).id
            else:
                m01 = None

            if salerid:
                s01 = self.env['hr.employee'].search_bycode(salerid).id
            else:
                s01 = None

            sql_order_line = sql_order_line.format(saleid)
            pos_order_line = ms.ExecQuery(sql_order_line.encode('utf-8'))

            for (saleman, saledate_detail, proid, SaleQty, NormalPrice, curprice, amount, SaleType, PosNo,
                 profit) in pos_order_line:

                #数量为0的交易为促销折扣
                qty_tmp=SaleQty
                price_unit_tmp=curprice
                if SaleQty==0:
                    qty_tmp=1
                    price_unit_tmp=amount


                res.append((0, 0, {
                    'product_id': self.env['product.product'].search(
                        [('default_code', '=', self._get_business()['strBuscode'] + '-' + proid)]).id,
                    'price_unit': price_unit_tmp,
                    'qty': qty_tmp,
                    'lngsaleid': self.env['hr.employee'].search_bycode(saleman).id,
                }))
            vals = {
                'date_order': saledate_order,
                'company_id': br01,
                'user_id': self.env['res.users'].search([('login', '=', 'jspot-users')]).id,
                'note': self._get_business()['strBuscode'] + '-' + braid + '-' + saleid,
                'partner_id': m01,
                'pos_reference': self._get_business()['strBuscode'] + '-' + braid + '-' + saleid,
                'lines': res,
                'state': 'done',
                'buid': self._get_business().id,
                'strstoreid': braid,
                'lngcasherid': s01,
            }
            master = self.env['pos.order'].create(vals)

        return True

    @api.multi
    def query_period(self, local, remote):
        start_stamp = 0
        end_stamp = 0
        query_local = local
        query_remote = remote
        cr = self._cr
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp = local_max_num[0]
            if local_max_num[0] is None:
                start_stamp = 0
        return_start = start_stamp

        ms = Lz_read_SQLCa(self)
        remote_stamp = ms.ExecQuery(query_remote.encode('utf-8'))
        for end_stamp in remote_stamp:
            if remote_stamp[0] is None:
                end_stamp = 0
        return_end = end_stamp[0]

        res = {
            'start_stamp': return_start,
            'end_stamp': return_end,
        }
        return res

    def set_jsport_category_parent(self):

        # 检查根分类
        self.check_jsport_category_root()

        # 大分类
        posroot = self.get_jsport_pos_category_current_recordset(0)
        self.exec_set_jsport_pos_category_parent(posroot, 0)
        productroot = self.get_jsport_product_category_current_recordset(0)
        self.exec_set_jsport_product_category_parent(productroot, 0)

        # 中分类
        postoplevel = self.get_jsport_pos_category_current_recordset(4)
        self.exec_set_jsport_pos_category_parent(postoplevel, 4)
        producttoplevel = self.get_jsport_product_category_current_recordset(4)
        self.exec_set_jsport_product_category_parent(producttoplevel, 4)

        # 小分类
        posmidlevel = self.get_jsport_pos_category_current_recordset(6)
        self.exec_set_jsport_pos_category_parent(posmidlevel, 6)
        productmidlevel = self.get_jsport_product_category_current_recordset(6)
        self.exec_set_jsport_product_category_parent(productmidlevel, 6)

        return True

    def check_jsport_category_root(self):
        r01 = self.env['product.category'].search_bycode(self._get_business()['strBuscode'])
        if not r01:
            res = {
                'code': self._get_business()['strBuscode'],
                'name': self._get_business()['strBusName'],
                'buid': self._get_business()['id'],
            }
            self.env['product.category'].create(res)
            self.env['pos.category'].create(res)
        return True

    @api.multi
    def get_jsport_pos_category_current_recordset(self, lens):
        if lens <> 0:
            select_sql = """ 
                        select id,code from pos_category where length(code)={0} and buid={1}
                      """
            select_sql = select_sql.format(lens, self._get_business()['id'])
        else:
            select_sql = """ 
                        select id,code from pos_category where code='{0}' and buid={1}
                      """
            select_sql = select_sql.format(self._get_business()['strBuscode'], self._get_business()['id'])

        cr = self._cr
        cr.execute(select_sql)
        res = cr.fetchall()
        return res

    @api.multi
    def get_jsport_product_category_current_recordset(self, lens):
        if lens <> 0:

            select_sql = """ 
                        select id,code from product_category where length(code)={0} and buid={1}
                      """
            select_sql = select_sql.format(lens, self._get_business()['id'])
        else:
            select_sql = """ 
                        select id,code from product_category where code='{0}' and buid={1}
                      """
            select_sql = select_sql.format(self._get_business()['strBuscode'], self._get_business()['id'])
        cr = self._cr
        cr.execute(select_sql)
        res = cr.fetchall()
        return res

    def exec_set_jsport_pos_category_parent(self, vals, lens):
        for (parentid, code) in vals:
            if lens <> 0:
                sublens = lens + 2
                exec_sql = """ 
                                update pos_category set parent_id={0} where length(code)={1}  and substr(code,1,{2})='{3}'
                                 and  buid={4}
                              """
                exec_sql = exec_sql.format(parentid, sublens, lens, code, self._get_business()['id'])
            else:
                exec_sql = """ 
                                update pos_category set parent_id={0} where length(code)=4  and  buid={1}
    
                              """
                exec_sql = exec_sql.format(parentid, self._get_business()['id'])
            cr = self._cr
            cr.execute(exec_sql)
        return True

    def exec_set_jsport_product_category_parent(self, vals, lens):
        for (parentid, code) in vals:
            if lens <> 0:
                sublens = lens + 2
                exec_sql = """ 
                                    update product_category set parent_id={0} where length(code)={1}  and substr(code,1,{2})='{3}'
                                     and  buid={4}
                                  """
                exec_sql = exec_sql.format(parentid, sublens, lens, code, self._get_business()['id'])
            else:
                exec_sql = """ 
                                    update product_category set parent_id={0} where length(code)=4  and  buid={1}
        
                                  """
                exec_sql = exec_sql.format(parentid, self._get_business()['id'])
            cr = self._cr
            cr.execute(exec_sql)
        return True

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Author: weiliang
# Date :2018-02-14

import logging
import threading
import re
from odoo import api, models, tools, registry
from BNmssql import Bnc_read_SQLCa
from BNmysql import Bnc_Mysql_SQLCa

# from idlelib.SearchEngine import get

_logger = logging.getLogger(__name__)


class proc_sync_bnc_member(models.TransientModel):
    _name = 'proc.sync.bnc.member'
    _description = 'sync.bnc.member'

    def query_period(self):
        start_stamp = 0
        end_stamp = 0
        query_local = " select max(timestamp) as maxnum from bnc_member"
        query_remote = "SELECT CONVERT(INT,max(timestamp)) AS timestamp FROM bnc_member"
        # 取得本库最新的时间戳
        #        cr=registry(self._cr.dbname).cursor()
        cr = self._cr
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp = local_max_num[0]
            if local_max_num[0] is None:
                start_stamp = 0
        #        cr.close()
        return_start = start_stamp

        # 取得会员主库会员资料最大的时间戳
        ms = Bnc_read_SQLCa(self)
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

    def _sync_bnc_member(self):
        # 取得更新数据范围
        btw = self.query_period()
        ms = Bnc_read_SQLCa(self)
        # 待导入会员卡-本地时间戳和主服务器时间戳之间的记录导入，主服务器记录有更新时间戳就会变化
        i=0
        _logger.info("process sync_mssql_2_bnc")

        sql = """ 
               SELECT   lngbncid,lngbusid,strphone,strBncCode,
               DATEADD(hour,-8,opendate) as opendate, 
               DATEADD(hour,-8,regdate) as  regdate,
               DATEADD(hour,-8,updatedate) as  updatedate,
              lngvipgrade,dvipdate,CONVERT(INT,timestamp) AS timestamp,strsex,ishandset
               FROM bnc_member  
               where  CONVERT(INT,timestamp) between {0} and {1}
                  """
        sql = sql.format(btw['start_stamp'], btw['end_stamp'])
        #        sql = sql.format(0,58597)
        i=0
        bnc_memeber_list = ms.ExecQuery(sql.encode('utf-8'))
        for (lngbncid, lngbusid, strphone, strbncardid, opendate, regdate, UpdateDate, lngvipgrade, dvipdate, timestamp,
             strsex, ishandset) in bnc_memeber_list:
            # 封装bnc_member记录
            # 封装 res_partner记录
            _logger.info("Need Records:" +str(i)+"/"+str(len(bnc_memeber_list)) +" The Phone is "+strphone)
            i=i+1
            print strbncardid
            vals = {
                'strbncardid': strbncardid,
                'name': strbncardid,
                #                'phone': strphone,
                #                'mobile': strphone,
                'strbnctype': 'member',
                'is_company': False,
                'supplier': False,
                'customer': True,
                'company_id': False,
            }
            # 检查是插入还是更新
            #            r01=self.env['bnc.member'].search([('strBncCardid', '=',strbncardid)])
            print vals
            r01 = self.env['bnc.member'].get_mem_by_cardno(strbncardid)

            res = {
                'lngBncId': lngbncid,
                'lngBusId': lngbusid,
                'strPhone': strphone,
                'strBncCardid': strbncardid,
                'OpenDate': opendate,
                'RegDate': regdate,
                'lngvipgrade': lngvipgrade,
                'vip_level_name_by_vipgrade': str(lngvipgrade),
                'dvipDate': dvipdate,
                'timestamp': timestamp,
                #                'strSex': strsex,
                'ishandset': ishandset,
                #                        'resid':self.env['res.partner'].write(vals),
            }
            if r01:
                #mem_res_partner=r01['resid']
                r01['resid'].write(vals)
                r01.write(res)

            else:
                res['resid'] = self.env['res.partner'].create(vals).id,
                print res
                self.env['bnc.member'].create(res)
        return True

    def proc_volumn_and_amount(self):
        _logger.info("proc_volumn_and_amount")
        exec_sql = """
    		select bnc.resid,sale.volumn,sale.total_amt,total_bnc from 
                (select resid,COALESCE(total_amount,0) as total_bnc from bnc_member)
                bnc
                left join 
                (select
                                      po.partner_id,
                                      count(distinct order_id) as volumn,
                                      sum(pol.price_unit * pol.qty) as total_amt
                
                                    from pos_order po inner join pos_order_line pol on po.id = pol.order_id
                                    where po.partner_id is not null
                                    group by po.partner_id
                                    order by po.partner_id
                
                ) sale     on bnc.resid=sale.partner_id  
            where sale.total_amt <> bnc.total_bnc
    	"""
        cr = self._cr
        cr.execute(exec_sql)
        i=0
        partner_list = cr.fetchall()
        for (partner_tmp, volumns, amount,bnc_amount) in partner_list:
            print i ,len(partner_list),partner_tmp
            i=i+1
            mem_id = self.env['bnc.member'].search([('resid', '=', partner_tmp)])
            vals = {
                'pos_order_count': volumns,
                'total_amount': amount,
            }

            if mem_id:
                _logger.info("Need proc_volumn_and_amount:" + str(i) + "/" + str(len(partner_list))+" memberis  " +  str(mem_id[0]))
                mem_id[0].write(vals)

    def sync_member_personal_information(self):
        # TODO  'sync_member_personal_information'
        db = self.env['bn.db.connect'].search([('store_code', '=', 'bncard')])

        mem_list = self.get_personal_recordset(Bnc_Mysql_SQLCa(db[0]))
        for (mobile, bu_name, wxid, unionid, openid, nickname, sex,
             birthday, email, province, city, address,
             vip_level_name, agent, stamp) in mem_list:

            member = self.env['bnc.member'].search([('strPhone', '=', mobile)])
            if member:
                val = {
                    'wxid': wxid,
                    'unionid': unionid,
                    'openid': openid,
                    'nickname': nickname,
                    'agent': agent,
                    'bu_name': bu_name,
                    'strEMail': email,
                    'province': province,
                    'city': city,
                    'address': address,
                    # 'vip_level_name': vip_level_name,
                    'strSex': str(sex),
                    'Birthday': birthday,
                    'mysqlstamp': stamp,
                }
                _logger.info("sync_member_personal_information:" +  "/" + " the phones is =>  " + mobile)
                member[0].write(val)
        return True

    def sync_member_personal_information_for_null(self):
        # TODO  'sync_member_personal_information_for_null'

        Need_to_update_list = self.env['bnc.member'].search([('mysqlstamp', '=', None)])

        db = self.env['bn.db.connect'].search([('store_code', '=', 'bncard')])

        mem_list = self.get_personal_recordset_for_null(Bnc_Mysql_SQLCa(db[0]), Need_to_update_list)

        if mem_list:
            for (mobile, bu_name, wxid, unionid, openid, nickname, sex,
                 birthday, email, province, city, address,
                 vip_level_name, agent, stamp) in mem_list:

                member = self.env['bnc.member'].search([('strPhone', '=', mobile)])
                if member:
                    val = {
                        'wxid': wxid,
                        'unionid': unionid,
                        'openid': openid,
                        'nickname': nickname,
                        'agent': agent,
                        'bu_name': bu_name,
                        'strEMail': email,
                        'province': province,
                        'city': city,
                        'address': address,
                        'vip_level_name': vip_level_name,
                        'strSex': str(sex),
                        'Birthday': birthday,
                        'mysqlstamp': stamp,
                    }
                    _logger.info("sync_member_personal_information_for_null':" + "/" + " the phones is =>  " + mobile)
                    member[0].write(val)
        return True

    def sync_member_personal_mp_weixin(self):
        # TODO  'sync_member_personal_mp_weixin'
        db = self.env['bn.db.connect'].search([('store_code', '=', 'bncard')])
        mem_list = self.get_personal_mp_weixin(Bnc_Mysql_SQLCa(db[0]))
        for (mobile, reg, bu_id, bu_name, shopid, codeid, stamp
             ) in mem_list:
            print mobile
            print bu_id
            member = self.env['bnc.member'].search([('strPhone', '=', mobile)])

            if member:

                bnc_member_id = member[0].id
                # bnc_member_id = member.id
            else:
                bnc_member_id = None

            company = self.env['res.company'].search([('mp_bucode', '=', bu_id)])
            if company:
                bnc_company_id = company[0].id
            else:
                bnc_company_id = None

            seek_mobile = self.env['bnc.mobile.bu'].search([('strPhone', '=', mobile)])
            val = {
                'strPhone': mobile,
                'RegDate': reg,
                'strBuId': bu_id,
                'strBuName': bu_name,
                'strshopid': shopid,
                'strcodeid': codeid,
                'timestamp': stamp,
                'belong_bnc_member': bnc_member_id,
                'belong_company': bnc_company_id,
            }

            if seek_mobile:
                _logger.info("sync_member_personal_mp_weixin':" + "/" + " the phones is =>  " + mobile)
                seek_mobile[0].write(val)
            else:
                self.env['bnc.mobile.bu'].create(val)

        return True

    def sync_member_personal_integral_weixin(self):
        # TODO  'sync_member_personal_integral_weixin'
        db = self.env['bn.db.connect'].search([('store_code', '=', 'bncard')])
        mem_list = self.get_personal_integral_weixin(Bnc_Mysql_SQLCa(db[0]))
        # mem_list = self.get_personal_integral_weixin_test(Bnc_Mysql_SQLCa(db[0]))
        i=0
        for (ieid, mobile, name, teg_id, teg_name, type_name, integral, discount, validity_type,
             up_begin, up_end, addtime, vali_begin, vali_end, serial, statu, dt_endtime, stamp
             ) in mem_list:

            print i, len(mem_list), mobile
            i = i + 1

            member = self.env['bnc.member'].search([('strPhone', '=', mobile)])
            if member:
                bnc_member_id = member[0].id
            else:
                bnc_member_id = None
            val = {
                'intIeId': ieid,
                'strPhone': mobile,
                'strName': name,
                'intTegId': teg_id,
                'strTegName': teg_name,
                'strTypeName': type_name,
                'intIntegral': integral,
                'intDiscount': discount,
                'intValidityType': validity_type,
                'up_begin': up_begin,
                'up_end': up_end,
                'valid_begin': vali_begin,
                'valid_end': vali_end,
                'strSerial': serial,
                'strStatus': statu,
                'Addtime': addtime,
                'Endtime': dt_endtime,
                'timestamp': stamp,
                'belong_bnc_member': bnc_member_id,
            }
            mem_c = self.env['bnc.mobile.integral'].search([('intIeId', '=', ieid)])
            if mem_c:
                mem_c.write(val)
            else:
                self.env['bnc.mobile.integral'].create(val)
            _logger.info("sync_member_personal_integral_weixin':" + "/" + " the phones is =>  " + mobile)
        return True

    def sync_member_personal_accesslog_weixin(self):
        # TODO  'sync_member_personal_accesslog_weixin'
        db = self.env['bn.db.connect'].search([('store_code', '=', 'bncard')])
        mem_list = self.get_personal_accesslog_weixin(Bnc_Mysql_SQLCa(db[0]))
        i=0
        for (wxid, mobile, unionid, openid, login_time, update_time, bnc_login_time, stamp) in mem_list:

            print i,len(mem_list),mobile
            i=i+1


            member = self.env['bnc.member'].search([('strPhone', '=', mobile)])
            if member:
                bnc_member_id = member[0].id
                _logger.info("sync_member_personal_accesslog_weixin':" + str(i)+ "/" +str(len(mem_list))+ " the phones is =>  " + mobile)
                member.write({'login_time': login_time})
            else:
                bnc_member_id = None
            val = {
                'strWxit': wxid,
                'unionid': unionid,
                'openid': openid,
                'login_time': bnc_login_time,
                'timestamp': stamp,
                'belong_bnc_member': bnc_member_id,
            }
            mem_c = self.env['bnc.member.accesslog'].search([('strWxit', '=', wxid)])
            if mem_c:
                mem_c.write(val)
            else:
                self.env['bnc.member.accesslog'].create(val)



        return True

    def get_personal_recordset(self, ms):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        query_local = " select max(mysqlstamp) as maxnum from bnc_member"
        cr = self._cr
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp = local_max_num[0]
            if local_max_num[0] is None:
                start_stamp = 0
        sql = """
                select
                mobile,bu_name, wxid, unionid, openid, nickname, sex, 
                birthday, email, province, city, address, 
                vip_level_name, agent,unix_timestamp(update_time)
                from v_user 
                where unix_timestamp(update_time)>{0}
                order by update_time desc
                  """
        sql = sql.format(start_stamp)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    def get_personal_recordset_for_null(self, ms, proc_list):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳

        if proc_list is None:
            return None

        p_list = []
        for mem in proc_list:
            p_list.append(mem['strPhone'])

        para_str = str(tuple(p_list)).replace('u', '')
        sql = """
                select
                mobile,bu_name, wxid, unionid, openid, nickname, sex, 
                birthday, email, province, city, address, 
                vip_level_name, agent,unix_timestamp(update_time)
                from v_user 
                where mobile in {0}
                order by update_time desc
                  """
        sql = sql.format(para_str)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    def get_personal_mp_weixin(self, ms):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        query_local = " select max(timestamp) as maxnum from bnc_mobile_bu"
        cr = self._cr
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp = local_max_num[0]
            if local_max_num[0] is None:
                start_stamp = 0
        sql = """
                select mobile,reg,bu_id,bu_name,shopid,codeid,unix_timestamp(reg)
                from v_mobile_bu
                where unix_timestamp(reg)>{0}
                order by unix_timestamp(reg) 
                  """
        sql = sql.format(start_stamp)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    def get_personal_integral_weixin(self, ms):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        query_local = " select max(timestamp) as maxnum from bnc_mobile_integral"
        cr = self._cr
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp = local_max_num[0]
            if local_max_num[0] is None:
                start_stamp = 0
        sql = """
                select ieid,mobile,name,teg_id,teg_name,type_name,integral,discount,
                        validity_type,up_begin,up_end,
                        addtime,vali_begin,vali_end,serial,statu,
                        endtime,unix_timestamp(updatetime)
                from v_integral
                 where unix_timestamp(updatetime)>{0}
                 order by unix_timestamp(updatetime)
                   """

        # sql = """
        #         select ieid,mobile,name,teg_id,teg_name,type_name,integral,discount,
        #                 validity_type,up_begin,up_end,
        #                 addtime,vali_begin,vali_end,serial,statu,
        #                 endtime,unix_timestamp(updatetime)
        #         from v_integral
        #         where endtime is not null
        #            """
        #

        sql = sql.format(start_stamp)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    def get_personal_integral_weixin_test(self, ms):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        sql = """
                select ieid,mobile,name,teg_id,teg_name,type_name,integral,discount,
                        validity_type,up_begin,up_end,
                        addtime,vali_begin,vali_end,serial,statu,
                        endtime,unix_timestamp(updatetime)
                from v_integral
                 where ieid=1
                   """
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    def get_personal_accesslog_weixin(self, ms):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        query_local = " select max(timestamp) as maxnum from bnc_member_accesslog"
        cr = self._cr
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp = local_max_num[0]
            if local_max_num[0] is None:
                start_stamp = 0
        sql = """
                    select
                      wxid,mobile,unionid,openid,login_time,update_time,
                       date_add(login_time, interval -8 hour) as bnc_login_time,
                      unix_timestamp(
                      case when update_time is null
                        then login_time
                      else update_time
                      end) as stamps
                    from v_wx
                    where unix_timestamp(
                      case when update_time is null
                        then login_time
                      else update_time
                      end)  >{0}
                 order by unix_timestamp(case when update_time is null
                        then login_time
                      else update_time
                      end)
                    
                   """
        # start_stamp=0
        sql = sql.format(start_stamp)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res

    def identify_personal(self):
        recordset = self.env['bnc.member'].search([('phone_status', '!=', 'True')])
        for rec in recordset:
            if rec['agent']:
                info = rec['agent']
            else:
                info = ''

            result = self.re_phone(info)
            if len(result) <> 0:
                if len(result) == 2:
                    val = {
                        'phone_1': result[0],
                        'phone_2': result[1],
                        'phone_status': True
                    }
                if len(result) == 4:
                    val = {
                        'phone_1': result[0],
                        'phone_2': result[1],
                        'phone_3': result[2],
                        'phone_4': result[3],
                        'phone_status': True
                    }
                rec.write(val)

        return True

    def re_phone(self, agent):
        if len(agent) <> 0:
            res = re.findall(r'[^()]+', agent)
            phone = re.split(r';', res[1])
        else:
            phone = {}
        return phone

    # @api.multi
    def sync_bnc_member_from_mssql(self):
        self.env['proc.sync.bnc.member']._sync_bnc_member()


    def get_mg_guide_info(self, ms):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        query_local = " select max(lng_mg_id) as maxnum  from bnc_mg_guideinfo"
        cr = self._cr
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp = local_max_num[0]
            if local_max_num[0] is None:
                start_stamp = 0
        sql = """
                select id,realname,nickname,gender,phone,password,province,city,area,addtime 
                from mg_guide_info
                where id >{0}
                order by id
                   """
        sql = sql.format(start_stamp)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res


    def get_mg_guide_customer(self, ms):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        query_local = " select max(lng_mg_id) as maxnum  from bnc_mg_guidecustomer"
        cr = self._cr
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp = local_max_num[0]
            if local_max_num[0] is None:
                start_stamp = 0
        sql = """
                select id,guide_id,manager_id,customer_openid,addtime,realname,gender,phone,province,city,area,tags  
                from mg_guide_customer
                where id >{0}
                order by id
                   """
        sql = sql.format(start_stamp)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res




    def get_mg_weixinfans(self, ms):
        # 获取更新记录范围，本地库的时间戳和服务端时间戳
        query_local = " select max(lng_mg_id) as maxnum  from bnc_mg_weixinfans"
        cr = self._cr
        cr.execute(query_local)
        for local_max_num in cr.fetchall():
            start_stamp = local_max_num[0]
            if local_max_num[0] is None:
                start_stamp = 0
        sql = """
                select  id,wxid,openid,nickname,sex,province,city,country,headimgurl,unionid,
                          subscribe_time_dt,subscribe,groupid,tagid_list,addtime,lasttime,
                          last_baseauth_time,is_rec_msg,from_xcx,tags  
                from mg_weixin_fans
                where id >{0}
                order by id
                   """
        sql = sql.format(start_stamp)
        res = ms.ExecQuery(sql.encode('utf-8'))
        return res


    def sync_mg_2_bnc(self):
        # TODO  'sync_mg_2_bnc'
        db = self.env['bn.db.connect'].search([('store_code', '=', 'mgjspot')])
        mem_list = self.get_mg_guide_info(Bnc_Mysql_SQLCa(db[0]))
        # mem_list = self.get_personal_integral_weixin_test(Bnc_Mysql_SQLCa(db[0]))
        i=0
        for (id ,realname, nickname, gender ,phone ,password, province, city, area ,addtime
             ) in mem_list:

            i = i + 1

            member = self.env['bnc.member'].search([('strPhone', '=', phone)])

            if member:
                bnc_member_id = member[0].id
            else:
                bnc_member_id = None

            val = {
                'lng_mg_id': id,
                'realname': realname,
                'nickname': nickname,
                'gender': gender,
                'phone': phone,
                'password': password,
                'province': province,
                'city': city,
                'area': area,
                'addtime': addtime
            }
            mem_c = self.env['bnc.mg.guideinfo'].search([('lng_mg_id', '=', id)])
            if mem_c:
                mem_c.write(val)
            else:
                self.env['bnc.mg.guideinfo'].create(val)
            _logger.info("sync_guideinfo':" + "/" + " the phones is =>  " + phone)
        return True




    def sync_mg_customer_2_bnc(self):
        # TODO  'sync_mg_customer_2_bnc'
        db = self.env['bn.db.connect'].search([('store_code', '=', 'mgjspot')])
        mem_list = self.get_mg_guide_customer(Bnc_Mysql_SQLCa(db[0]))
        # mem_list = self.get_personal_integral_weixin_test(Bnc_Mysql_SQLCa(db[0]))
        i=0
        for ( id,guide_id,manager_id,customer_openid,addtime,realname,gender,phone,province,city,area,tags
             ) in mem_list:

            i = i + 1

            member = self.env['bnc.member'].search([('strPhone', '=', phone)])

            if member:
                bnc_member_id = member[0].id
            else:
                bnc_member_id = None

            val = {
                'lng_mg_id': id,
                'guide_id': guide_id,
                'manager_id': manager_id,
                'customer_openid': customer_openid,
                'addtime': addtime,
                'realname': realname,
                'gender': gender,
                'phone': phone,
                'province': province,
                'city': city,
                'area': area,
                'tags': tags
            }
            mem_c = self.env['bnc.mg.guidecustomer'].search([('lng_mg_id', '=', id)])
            if mem_c:
                mem_c.write(val)
            else:
                self.env['bnc.mg.guidecustomer'].create(val)
                self.env.cr.commit()

            # print("sync_guidecustomer':" + str(id) + "====>" + str(i) + "/" + str(len(mem_list)))

            if i % 100==0:
                _logger.info("sync_guidecustomer':" +str(id)+ "====>"+str(i)+"/"+ str(len(mem_list)))
        return True




    def sync_mg_weixinfans_2_bnc(self):
        # TODO  'sync_mg_weixinfans_2_bnc'
        db = self.env['bn.db.connect'].search([('store_code', '=', 'mgjspot')])
        mem_list = self.get_mg_weixinfans(Bnc_Mysql_SQLCa(db[0]))
        # mem_list = self.get_personal_integral_weixin_test(Bnc_Mysql_SQLCa(db[0]))
        i=0
        for ( id,wxid,openid,nickname,sex,province,city,country,headimgurl,unionid,subscribe_time_dt,subscribe,
              groupid,tagid_list,addtime,lasttime,last_baseauth_time,is_rec_msg,from_xcx,tags
             ) in mem_list:

            i = i + 1

            # member = self.env['bnc.member'].search([('strPhone', '=', phone)])
            #
            # if member:
            #     bnc_member_id = member[0].id
            # else:
            #     bnc_member_id = None

            val = {
                'lng_mg_id': id,
                'wxid': wxid,
                'openid': openid,
                'nickname': nickname,
                'sex': sex,
                'province': province,
                'city': city,
                'country': country,
                'headimgurl': headimgurl,
                'unionid': unionid,
                'subscribe_time_dt': subscribe_time_dt,
                'subscribe': subscribe,
                'groupid': groupid,
                'tagid_list': tagid_list,
                'addtime': addtime,
                'lasttime': lasttime,
                'last_baseauth_time': last_baseauth_time,
                'is_rec_msg': is_rec_msg,
                'tags': tags
            }
            mem_c = self.env['bnc.mg.weixinfans'].search([('lng_mg_id', '=', id)])
            if mem_c:
                mem_c.write(val)
            else:
                self.env['bnc.mg.weixinfans'].create(val)
                self.env.cr.commit()

            # print("sync_guidecustomer':" + str(id) + "====>" + str(i) + "/" + str(len(mem_list)))

            if i % 100==0:
                _logger.info("sync_bnc.mg.weixinfans':" +str(id)+ "====>"+str(i)+"/"+ str(len(mem_list)))
        return True








    def proc_sync_bnc_mg(self):
        print("proc_sync_bnc_mg")
        self.sync_mg_2_bnc()
        self.sync_mg_customer_2_bnc()
        self.sync_mg_weixinfans_2_bnc()
        self.env['bnc.tag.process'].process_for_mg()



    def procure_sync_bnc(self):

        self.env['proc.sync.bnc.member'].sync_bnc_member_from_mssql()
        self.env['proc.sync.bnc.member'].identify_personal()
        self.env['proc.sync.bnc.member'].sync_member_personal_information()
        self.env['proc.sync.bnc.member'].sync_member_personal_information_for_null()
        self.env['proc.sync.bnc.member'].sync_member_personal_mp_weixin()
        self.env['proc.sync.bnc.member'].sync_member_personal_integral_weixin()
        self.env['proc.sync.bnc.member'].sync_member_personal_accesslog_weixin()

        return {'type': 'ir.actions.act_window_close'}

# -*- coding: utf-8 -*-
import logging
import threading
import datetime

from odoo import api, models, tools, registry
from odoo.addons.bnc_member.wizards.BNmssql import bn_SQLCa

_logger = logging.getLogger(__name__)


class bnc_tag_process(models.TransientModel):
    _name = "bnc.tag.process"

    def seek_for_employee(self):
        print "seek_for_employee"
        tag01 = self.env['bnc.tags'].search([('code', '=', 'EMP')])
        hrdb = self.env['bn.db.connect'].search([('bu_code', '=', 'hr')])
        ms = bn_SQLCa(hrdb)

        if tag01:
            records = self.env['bnc.tags.log'].search([('tagids', '=', tag01.id)])
            mem_done = []
            for mlist in records:
                mem_done.append(mlist['mem_ids'].id)

            members = self.env['bnc.member'].search([('id', 'not in', mem_done)])
            total_lines = len(members)
            i = 0
            if total_lines <> 0:
                for mem in members:
                    print i, total_lines
                    tags = []
                    print mem['strPhone']
                    sql = """ 
                       select lngemployeeid,stremployeecode,stremployeename,strtelephone  from [dbo].[Employee]
                       where strtelephone like '%{0}%'
                      """
                    sql = sql.format(str(mem['strPhone']))
                    print sql
                    res = ms.ExecQuery(sql.encode('utf-8'))
                    print res
                    val = {
                        'mem_ids': mem.id,
                        'tagids': tag01.id
                    }

                    val2 = {
                        'memid': mem.id,
                        'tagid': tag01.id
                    }

                    tags.append((4, tag01.id))
                    if len(res) <> 0:
                        mem.write({'tagsid': tags})
                    self.env['bnc.tags.log'].create(val)

    def process_for_age(self):
        _logger.info(" process_for_age")
        tag_list = self.env['bnc.tags'].search([('internal_method', '=', 'ByAge'), ('isActive', '=', True)])
        cr = self._cr
        for tag in tag_list:
            # 删除原来的标签
            exec_sql = """
               delete from bnc_tags_member_rel where tagid ={0}
            """
            exec_sql = exec_sql.format(tag['id'])
            cr.execute(exec_sql)

            if tag['isRunScript']:
                sql = tag['run_sql']
                try:
                    cr.execute(sql)
                    result = cr.fetchall()
                    for rec in result:
                        mem = self.env['bnc.member'].search([('id', '=', rec[0])])
                        if mem:
                            tags = []
                            tags.append((4, tag.id))
                            mem.write({'tagsid': tags})

                except Exception:
                    continue

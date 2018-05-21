# -*- coding: utf-8 -*-
import logging
import threading
import datetime

from odoo import api, models, tools, registry, fields
from odoo.addons.bnc_member.wizards.BNmssql import bn_SQLCa
from odoo.addons.bnc_member.lead.proc_bnc_lead import *


class bnc_lead(models.Model):
    _name = "bnc.lead"

    buid = fields.Many2one('bnc.business', u'事业部')
    code = fields.Char(string=u'编号')
    name = fields.Char(string=u'名称')
    crmleadid = fields.One2many('crm.lead', 'bnc_lead_id', u'活动明细')
    tag_template_id = fields.Many2one('bnc.tags.template', u'标签模板')
    start = fields.Datetime(string=u'开始日期')
    end = fields.Datetime(string=u'结束日期')
    memo = fields.Text(string=u'备注说明')
    state = fields.Selection([('new', 'open'), ('doing', 'doing'), ('done', 'Done')], string=u'状态')
    color = fields.Integer('Color Index')

    def name_get(self):
        res = []
        for r in self:
            res.append((r.id, r.code + '---' + r.name))
        return res

    def select_memeber_set(self):
        # TODO 筛选记录
        base_record = self.get_tags_list('BASE')
        cond_record = self.get_tags_list('COND')

        memeber_list = list(set(base_record).intersection(cond_record))

        proc_lead_buynow(self, memeber_list)

    def get_tags_list(self, para_type):
        tags = self.env['bnc.tags.template'].search([('id', '=', self.tag_template_id.id)])
        if para_type == 'BASE':
            res = self.union_list(tags['base_tagids'])

        if para_type == 'COND':
            res = self.union_list(tags['cond_tagids'])

        return res

    def union_list(self, tags):
        mem_list = []
        for tag in tags:
            sql = """
                select distinct memid from bnc_tags_member_rel 
                where tagid = {0}
            """
            sql = sql.format(tag.id)
            result = self.get_rec(sql)
            mem_list.append(result)
        mem_tmp = []
        for mem in mem_list:
            mem_tmp = mem + mem_tmp
        return list(set(mem_tmp))

    def get_rec(self, sql):
        cr = self._cr
        cr.execute(sql)
        result = cr.fetchall()
        return result


class crm_lead(models.Model):
    _inherit = 'crm.lead'
    bnc_lead_id = fields.Many2one('bnc.lead', string='Order Ref', ondelete='cascade')

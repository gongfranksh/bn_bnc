# -*- coding: utf-8 -*-
import logging
import threading
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
from odoo import api, models, tools, registry, fields
from odoo.addons.bnc_member.mining.bnc_kmeans_tools import *

_logger = logging.getLogger(__name__)


class bnc_tags_rmf_template(models.Model):
    _name = "bnc.tags.rmf.template"

    name = fields.Char(string=u'名称')
    code = fields.Char(string=u'编号')
    memo = fields.Text(string=u'备注说明')
    col_r = fields.Integer(string=u'最近一次交易', default=2)
    col_f = fields.Integer(string=u'交易频率', default=2)
    col_m = fields.Integer(string=u'交易金额', default=2)
    isActive = fields.Boolean(string=u'有效标记')
    tagsid = fields.One2many('bnc.tags', 'rmf_template_ids', string=u'产生的标签')
    state = fields.Selection([('new', 'open'), ('doing', 'doing'), ('done', 'Done')], default='new', string=u'状态')
    internal_method = fields.Selection(
        [('ByYear', u'最近一年'), ('By6months', u'最近半年'), ('By3months', u'最近3个月')], string=u'计算周期')

    def create_rfm_tags(self):
        #TODO 删除原来的标签
        cr=self._cr
        exec_sql = """
           delete from bnc_tags where
           rmf_template_ids ={0} and internal_method='ByRMF'
        """
        exec_sql = exec_sql.format(self.id)
        cr.execute(exec_sql)

        # TODO 产生标签
        for r in range(self.col_r):
            for f in range(self.col_f):
                for m in range(self.col_m):
                    rmf_flag = str(r) + str(f) + str(m)
                    val = {
                        'code': 'RFM' + self.code + rmf_flag,
                        'name': self.name + rmf_flag,
                        'activeDate': datetime.now(),
                        'isActive': True,
                        'internal_method': 'ByRMF',
                        'rmf_flag': rmf_flag,
                        'rmf_template_ids': self.id,
                    }
                    self.env['bnc.tags'].create(val)


    def get_rfm_tags_recordset(self):
        _logger.info("proc_rfm_tags")
        end_date=datetime.now().date()

        if self.internal_method=='ByYear':
            begin_date = end_date - relativedelta(months=+12)

        if self.internal_method=='By6months':
            begin_date = end_date - relativedelta(months=+6)

        if self.internal_method=='By3months':
            begin_date = end_date - relativedelta(months=+3)

        val={
            'start': begin_date.strftime("%Y-%m-%d"),
            'end': end_date.strftime("%Y-%m-%d")

        }
        sale_records = get_orginal_kmeans(self,val)
        partner_list = get_qcut_result(self,sale_records )
        return partner_list



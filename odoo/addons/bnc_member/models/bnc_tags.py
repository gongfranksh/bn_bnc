# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import datetime


class bnc_tags(models.Model):
    _name = "bnc.tags"

    code = fields.Char(string=u'标签编号')
    name = fields.Char(string=u'名称')
    color = fields.Integer(string="Color", help="Choose your color")
    cateids = fields.Many2one('bnc.tags.category', string=u'所属分类')
    isActive = fields.Boolean(string=u'有效标记')
    activeDate = fields.Datetime(string=u'生效日期')
    rundate = fields.Datetime(string=u'最近一次执行日期')
    run_sql = fields.Text(string=u'运行脚本')
    isRunScript = fields.Boolean(string=u'是否由脚本运行')
    internal_method = fields.Selection([('ByAmount', 'amt'), ('ByQty', 'qty'), ('ByPhone', 'phone'), ('ByAge', 'age'),('ByPeriod', 'period')],
                                       string=u'内部类型')
    run_method = fields.Text(string=u'运行程序')
    memo = fields.Text(string=u'备注说明')


    def get_tags_member_count(self):
        sql = """
               select tagid,count(*) from bnc_tags_member_rel group by tagid
            """
        cr = self.env.cr.execute(sql)
        res = cr.fetchall()
        return res


class bnc_tags_category(models.Model):
    _name = "bnc.tags.category"
    code = fields.Char(string=u'标签编号')
    name = fields.Char(string=u'名称')
    isActive = fields.Boolean(string=u'有效标记')


class bnc_tags_log(models.Model):
    _name = "bnc.tags.log"
    tagids = fields.Many2one('bnc.tags', string=u'标签')
    mem_ids = fields.Many2one('bnc.member', string=u'会员')
    rundate = fields.Datetime(string=u'最近一次执行日期')

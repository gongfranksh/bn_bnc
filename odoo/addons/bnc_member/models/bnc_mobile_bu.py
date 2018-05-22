# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import datetime


class bnc_mobile_bu(models.Model):
    _name = "bnc.mobile.bu"

    strPhone = fields.Char(string=u'注册手机')
    RegDate = fields.Datetime(string=u'注册日期')
    strBuId = fields.Char(string=u'注册公众号代码')
    strBuName = fields.Char(string=u'注册公众号')
    strshopid = fields.Char(string=u'百脑汇店代码')
    strcodeid = fields.Char(string=u'其他代码')
    timestamp = fields.Integer(string=u'更新时间戳')
    belong_bnc_member = fields.Many2one('bnc.member', string=u'所属公司')
    belong_company = fields.Many2one('res.company', string=u'所属公司')

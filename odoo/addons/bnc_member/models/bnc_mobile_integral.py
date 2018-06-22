# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import datetime


class bnc_mobile_integral(models.Model):
    _name = "bnc.mobile.integral"

    intIeId = fields.Integer(string=u'券编号')
    strPhone = fields.Char(string=u'注册手机')
    strName = fields.Char(string=u'券名称')
    intTegId = fields.Integer(string=u'事业群ID')
    strTegName = fields.Char(string=u'事业群名称')
    strTypeName = fields.Char(string=u'类型名称')
    intIntegral = fields.Integer(string=u'商品积分')
    intDiscount = fields.Integer(string=u'折扣率')
    intValidityType =fields.Selection([(1, u'固定有效期'), (2, u'领取时开始有效期')], string=u'有效期类型')
    up_begin = fields.Datetime(string=u'上架开始时间')
    up_end = fields.Datetime(string=u'上架结束时间')
    valid_begin = fields.Datetime(string=u'有效期开始时间')
    valid_end = fields.Datetime(string=u'有效期结束时间')
    strSerial = fields.Char(string=u'兑换码')
    strStatus =fields.Selection([(-1, u'未生效'), (0, u'未使用'),(1, u'已使用')], string=u'状态')
    Addtime = fields.Datetime(string=u'建立时间')
    Endtime = fields.Datetime(string=u'核销时间')
    timestamp = fields.Integer(string=u'更新时间戳')
    belong_bnc_member = fields.Many2one('bnc.member', string=u'会员')

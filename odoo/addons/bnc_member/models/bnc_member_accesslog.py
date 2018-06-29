# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import datetime


class bnc_member_accesslog(models.Model):
    _name = "bnc.member.accesslog"

    strWxit = fields.Char(string=u'流水编号')
    unionid = fields.Char(string=u'微信unionid')
    openid = fields.Char(string=u'微信openid')
    login_time = fields.Datetime(string=u'最近一次登陆时间')
    timestamp = fields.Integer(string=u'更新时间戳')
    belong_bnc_member = fields.Many2one('bnc.member', string=u'会员')

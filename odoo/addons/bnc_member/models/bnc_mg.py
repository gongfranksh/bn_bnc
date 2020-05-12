# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import datetime


class bnc_mg_guideinfo(models.Model):
    _name = "bnc.mg.guideinfo"
    lng_mg_id = fields.Integer(string=u'mg_guid_info_id')
    realname = fields.Char(string='真实姓名')
    nickname = fields.Char(string='昵称')
    gender = fields.Char(string='性别')
    phone = fields.Char(string=u'注册手机')
    password = fields.Char(string=u'密码')
    province = fields.Char(string=u'省份')
    city = fields.Char(string=u'城市')
    area = fields.Char(string=u'区域')
    addtime = fields.Datetime(string=u'更新日期')




class bnc_mg_guidecustomer(models.Model):
    _name = "bnc.mg.guidecustomer"
    lng_mg_id = fields.Integer(string=u'mg_guid_icustomer_id')
    customer_openid = fields.Char(string='customer_openid')
    realname = fields.Char(string='真实姓名')
    gender = fields.Char(string='性别')
    phone = fields.Char(string=u'注册手机')
    province = fields.Char(string=u'省份')
    city = fields.Char(string=u'城市')
    area = fields.Char(string=u'区域')
    addtime = fields.Datetime(string=u'更新日期')
    area = fields.Char(string=u'区域')
    tags = fields.Char(string=u'标签')
    guide_id = fields.Integer(string=u'guide_id')
    manager_id = fields.Integer(string=u'manager_id')


class bnc_mg_weixin_fans(models.Model):
    _name = "bnc.mg.weixinfans"
    lng_mg_id = fields.Integer(string=u'mg_weixin_fans_id')
    wxid = fields.Integer(string=u'wxid')
    openid = fields.Char(string='openid')
    nickname = fields.Char(string='昵称')
    sex = fields.Char(string='性别')
    province = fields.Char(string=u'省份')
    city = fields.Char(string=u'城市')
    country = fields.Char(string=u'国家')
    headimgurl = fields.Char(string=u'头像地址')
    unionid = fields.Char(string='openid')
    language = fields.Char(string='language')
    subscribe_time_dt = fields.Datetime(string='subscribe_time_dt')
    subscribe = fields.Char(string='subscribe')
    un_subscribe = fields.Char(string='subscribe')
    groupid = fields.Char(string='groupid')
    tagid_list = fields.Char(string='tagid_list')
    addtime = fields.Datetime(string=u'加入日期时间')
    lasttime = fields.Datetime(string=u'更新日期')
    last_baseauth_time = fields.Datetime(string=u'last_baseauth_time')
    last_infoauth_time = fields.Datetime(string=u'last_infoauth_time')
    is_rec_msg = fields.Char(string=u'is_rec_msg')
    from_xcx = fields.Char(string='from_xcx')
    tags = fields.Char(string='tags')


# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


import datetime

class bnc_member(models.Model):
	_name ="bnc.member"

	lngBncId = fields.Char(string='lngBncId')
	lngBusId = fields.Char(string='lngBusId')
	lngvipgrade= fields.Char(string='lngvipgrade')
	timestamp= fields.Integer(string=u'更新时间戳')
	
	OpenDate= fields.Datetime(string=u'OpenDate')
	RegDate= fields.Datetime(string=u'注册日期')
	UpdateDate= fields.Datetime(string=u'更新日期')
	dvipDate= fields.Char(string=u'vip升级日期')
	Birthday=fields.Datetime(string=u'生日')	
	
	ishandset=fields.Char(string='ishandset' )
	strUid= fields.Char(string='strUid', )
	lngPayId=fields.Char(string='lngPayId' )
	strPhone= fields.Char(string=u'注册手机' )
	strBncName= fields.Char(string=u'姓名' )
#	strSex= fields.Char(string=u'性别' )
	strSex= fields.Selection([('1', u'男性'), ('2', u'女性')],string=u'性别' )

	strEMail=fields.Char(string=u'邮箱地址' )
	strProfessionl= fields.Char(string=u'职业')
	strStatus= fields.Char(string=u'状态',size=5 )
	strBncCardid= fields.Char(string=u'内部卡号' )
	Age= fields.Char(string=u'年龄' )
	UpdateMan= fields.Char(string='UpdateMan' )
#	resid = fields.Many2one('res.partner',u'合作伙伴')	
	resid = fields.Many2one('res.partner',u'合作伙伴',required=True, ondelete='cascade')	
	tagsid = fields.Many2many('bnc.tags','bnc_tags_member_rel','memid','tagid',string=u'用户标签')

#add for mysql
	wxid =fields.Integer(string=u'微信id')
	unionid= fields.Char(string=u'unionid' )
	openid= fields.Char(string=u'openid' )
	nickname= fields.Char(string=u'昵称' )
	agent= fields.Text(string=u'agent' )
	bu_name= fields.Char(string=u'bu_name' )
	province= fields.Char(string=u'省份' )
	city= fields.Char(string=u'城市' )
	address= fields.Char(string=u'地址' )
	vip_level_name=fields.Char(string=u'会员等级' )
	mysqlstamp=fields.Integer(string=u'资料更新日期戳' )


	phone_1=fields.Char(string=u'手机信息1' )
	phone_2=fields.Char(string=u'手机信息2' )
	phone_3=fields.Char(string=u'手机信息3' )
	phone_4=fields.Char(string=u'手机信息4' )

	phone_os=fields.Char(string=u'手机操作系统' )
	phone_brand=fields.Char(string=u'手机品牌' )
	phone_status=fields.Boolean(string=u'手机信息更新状态', default=False )
	age_period =fields.Integer(compute='_compute_age',string=u'年龄段')

	@api.one
	def query_bnc_member_timestamp(self):
		select_str = """
			  select max(timestamp) from bnc_member
		"""
		self.env.cr.execute(select_str)
		ids = dict(self._cr.fetchall())
		return ids

	@api.depends('Birthday')
	def _compute_age(self):
            if self.Birthday:
                d1= datetime.datetime.strptime(self.Birthday,'%Y-%m-%d %H:%M:%S')
            else:
                d1 = datetime.date.today()

            d2= datetime.date.today()
            self.age_period=d2.year-d1.year



	def name_get(self):
		res=[]
		for r in self:
			res.append((r.id,r.strBncCardid+'---'+r.strPhone))
		return res


	@api.model
	def get_mem_by_cardno(self, vals):
		res =self.search([('strBncCardid', '=',vals)])
		return res
		
	@api.model
	def get_mem_by_phone(self, vals):
		res =self.search([('strPhone', '=',vals)])
		return res	

	@api.multi
	def unlink(self):
		for res in self:
				super(bnc_member, res).unlink()

	

	
	

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
	strSex= fields.Selection([('0', u'未设置'),('1', u'男性'), ('2', u'女性')],string=u'性别' )

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

	num_1=fields.Char(string=u'归属地' )
	num_2=fields.Char(string=u'卡类型' )
	num_3=fields.Char(string=u'运营商' )
	num_4=fields.Char(string=u'区号' )
	num_5=fields.Char(string=u'邮编' )
	num_6=fields.Char(string=u'省份' )
	num_7=fields.Char(string=u'城市' )


	age_period =fields.Integer(compute='_compute_age',string=u'年龄段')

	pos_order_count = fields.Integer(
		compute='_compute_pos_order',
		string=u'交易数',
		help="The number of point of sale orders related to this customer",
	)

	total_amount = fields.Float(compute='_compute_total_amount', string='交易金额')

	tags_name = fields.Char(
		compute='_compute_tags_name',
		string=u'标签名称合并',
	)

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

	@api.depends('resid')
	def _compute_pos_order(self):
		res=[]
		for mem in self:
			res.append(mem["resid"].ids)

		partners_data = self.env['pos.order'].read_group([('partner_id', 'in', res)], ['partner_id'],
														 ['partner_id'])
		mapped_data = dict([(partner['partner_id'][0], partner['partner_id_count']) for partner in partners_data])
		for member in self:
			member.pos_order_count = mapped_data.get(member.resid.id, 0)


	@api.depends('resid')
	def _compute_total_amount(self):
		for record in self:
			record.total_amount = sum(
				line.amount_total for line in record.env['pos.order'].search([('partner_id', '=', record.resid.id)]))

	@api.depends('tagsid')
	def _compute_tags_name(self):
		member_data=[]
		for mem in self:
			label_tag=''
			for tag in mem["tagsid"]:
				tag_f=self.env['bnc.tags'].search([('id','=',tag.id)])
				if tag_f:

					# print len(label_tag)
					if  len(label_tag)<>0:
						label_tag= label_tag  +'||'+tag_f["name"]
					else:
						label_tag=tag_f["name"]

			member_data.append((mem.id,label_tag))

		mapped_data = dict([(mem[0], mem[1]) for mem in member_data ])

		for member in self:
			print member.id
			member.tags_name = mapped_data.get(member.id, 0)




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

	

	
	

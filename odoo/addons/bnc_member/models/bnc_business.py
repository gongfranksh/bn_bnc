# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import datetime

class bnc_business(models.Model):
	_name ="bnc.business"
#	lngBusId = fields.Integer(string=u'事业部ID')
	strBusName= fields.Char(string=u'事业部名称',size=20 )
	strBuscode= fields.Char(string=u'事业部代码',size=20 )
	
	@api.model
	def get_bnc_business_bycode(self, vals):
		res =self.search([('strBuscode', '=',vals)])
		return res	

	@api.multi
	def name_get(self):
		res=[]
		for r in self:
			res.append((r.id,r.strBuscode+'---'+r.strBusName))
		return res

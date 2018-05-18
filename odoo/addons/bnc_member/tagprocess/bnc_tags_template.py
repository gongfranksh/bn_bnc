# -*- coding: utf-8 -*-
import logging
import threading
import datetime
import re
from odoo import api, models, tools, registry, fields

_logger = logging.getLogger(__name__)


class bnc_tags_template(models.Model):
    _name = "bnc.tags.template"

    name = fields.Char(string=u'名称')
    code = fields.Char(string=u'编号')
    memo = fields.Text(string=u'备注说明')
    isActive = fields.Boolean(string=u'有效标记')
    tagids = fields.Many2many('bnc.tags', 'bnc_tags_template_rel', 'templateid', 'tagid', string=u'需要选择的标签')
    resultType = fields.Selection([('0', u'合并集合'),('1', u'交叉集合')],string=u'集合结果类型' )

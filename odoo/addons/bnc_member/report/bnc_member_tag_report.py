# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class bnc_member_tag_report(models.Model):
    _name = "bnc.member.tag.report"
    _description = "bnc.member.tag.report"
    _auto = False

    memid = fields.Many2one('bnc.member', string=u'会员卡', readonly=True)
    tagid = fields.Many2one('bnc.tags', string=u'标签', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'bnc_member_tag_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW bnc_member_tag_report AS (
             select row_number() over(order by tagid ) id,memid,tagid from  bnc_tags_member_rel
            )
        """)

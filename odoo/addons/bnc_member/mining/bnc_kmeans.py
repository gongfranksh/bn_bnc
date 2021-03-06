# -*- coding: utf-8 -*-
import logging
import threading
import datetime
import re
import math
import os, sys

from odoo import api, models, tools, registry, fields
import pandas as pd

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
# from odoo.addons.bnc_member.office.bnc_report_pptx import bnc_report_ppt
from odoo.addons.bnc_member.office.bnc_report_pptx import *
from odoo.addons.bnc_member.office.bnc_report_word import *

_logger = logging.getLogger(__name__)

k = 3  # 聚类的类别
iteration = 100000  # 聚类最大循环次数
pic_output = 'E://'


class bnc_mining_kmeans(models.Model):
    _name = "bnc.mining.kmeans"

    code = fields.Char(string=u'编号')
    name = fields.Char(string=u'名称')
    start = fields.Datetime(string=u'开始日期')
    end = fields.Datetime(string=u'结束日期')
    memo = fields.Text(string=u'备注说明')
    resultids = fields.One2many('bnc.mining.kmeans.result', 'kmeansids', u'结果')
    state = fields.Selection([('new', 'open'), ('doing', 'doing'), ('done', 'Done')], string=u'状态')

    def action_kmeans(self):
        print 'action_kmeans'
        t = self.start

        vals = {
            'start': self.start[0:10],
            'end': self.end[0:10]
        }

        records = self.get_orginal_kmeans(vals)
        result = self.get_kmeans_result(records)
        vals = []
        for rec in result:

            vals = {
                'kmeansids': self.id,
                'col_r': int("%0.f" % rec[1]),
                'col_f': int("%0.f" % rec[2]),
                'col_m': rec[3],
                'col_c': int("%0.f" % rec[4]),
                'member': None
            }
            if not math.isnan(rec[0]):
                vals['member'] = int("%0.f" % rec[0])
            self.env['bnc.mining.kmeans.result'].create(vals)

            self.write({'state': 'done'})
        #        print result
        return True

    def get_kmeans_result(self, para_data):

        print 'action_kmeans'
        data = pd.DataFrame(data=para_data, columns=['partner', 'R', 'F', 'M'])
        data = data.set_index('partner')

        data_zs = 1.0 * (data - data.mean()) / data.std()
        model = KMeans(n_clusters=k, max_iter=iteration)  # 分为k类，并发数4
        model.fit(data_zs)
        r1 = pd.Series(model.labels_).value_counts()  # 统计各个类别的数目
        r2 = pd.DataFrame(model.cluster_centers_)  # 找出聚类中心
        result = pd.concat([r2, r1], axis=1)  # 横向连接（0是纵向），得到聚类中心对应的类别下的数目
        result.columns = list(data.columns) + [u'类别数目']  #
        result = pd.concat([data, pd.Series(model.labels_, index=data.index)], axis=1)  # 详细输出每个样本对应的类别
        result.columns = list(data.columns) + [u'clusterlevel']  # 重命名表头
        res = result.to_records()
        return res

    def get_orginal_kmeans(self, vals):
        para_start = vals['start'] + ' 00:00:00'
        para_end = vals['end'] + ' 23:59:59'
        sql = """
                select c.partner_id,date_part('day','{1}'-"last_date")  ,"volums" ,"amount"
                from (
                select partner_id,max(date_order) as "last_date",count(distinct order_id) as "volums" ,sum(price_unit*qty) as "amount"
                    from pos_order  po
                 inner join pos_order_line pl  on po.id=pl.order_id
                where  date_order between '{0}' and '{1}'  and partner_id is not null
                and partner_id not in (4846)
                group by partner_id ) c
        """
        sql = sql.format(para_start, para_end)
        cr = self._cr
        cr.execute(sql)
        res = cr.fetchall()

        if len(res) <> 0:
            return res
        else:
            return None

    def density_plot(self):  # 自定义作图函数
        #    print data
        t = bnc_report_ppt()
        getdata = self._query_report_result()
        category_volumns = self._query_report_result()

        mapped_data = dict([(volmns[0], volmns[1]) for volmns in category_volumns])

        ppt = t.create_ppt(getdata)

        ref = {
            'filename': u'%s-%s.pptx' % (self.code, self.name),
            'res_model': 'bnc.mining.kmeans',
            'res_id': self.id,
            'datas': ppt,
        }
        self.add_attachment(ref)
        report_files = []
        for i in range(k):
            para_data = self._get_result(i)
            data = pd.DataFrame(data=para_data, columns=['partner', 'R', 'F', 'M'])
            data = data.set_index('partner')
            filename = u'%s-%s-%s.png' % (self.code, self.name, i)
            file_path = os.path.join(sys.path[0], filename)
            _logger.info("bnc.mining.kmeans ")
            _logger.info(file_path)

            if os.path.exists(file_path):
                os.remove(file_path)

            try:
                self.density_plot_draw(data).savefig(file_path)
                with open(file_path, 'rb') as fp:
                    data = fp.read().encode('base64')
                    print sys.path[0]
                    ref = {
                        'filename': filename,
                        'res_model': 'bnc.mining.kmeans',
                        'res_id': self.id,
                        'datas': data,
                    }

                    item_file = {
                        'filename': filename,
                        'name': u'%s-%s-%s类' % (self.code, self.name, i),
                        'volumns': mapped_data.get(i, 0),
                        'category': i,
                    }
                    report_files.append(item_file)
                    # self.add_attachment(ref)
            except Exception:
                continue

        w1 = bnc_report_word()

        # for member in self:
        #     member.pos_order_count = mapped_data.get(member.resid.id, 0)

        para_data = {
            'title': u'%s-%s' % (self.code, self.name),
            'files': report_files,
        }
        word = w1.create_word(para_data)

        ref = {
            'filename': u'%s-%s.docx' % (self.code, self.name),
            'res_model': 'bnc.mining.kmeans',
            'res_id': self.id,
            'datas': word,
        }
        self.add_attachment(ref)

        return True

    def add_attachment(self, ref):  # 添加附件
        IrAttachment = self.env['ir.attachment']
        vals = dict(
            name=ref['filename'],
            datas_fname=ref['filename'],
            res_model=ref['res_model'],
            res_name=ref['filename'],
            res_id=ref['res_id'],
            type='binary',
            datas=ref['datas'],
        )
        IrAttachment.create(vals)
        return

    def density_plot_draw(self, data):  # 自定义作图函数
        #    print data
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False

        # 用来正常显示负号
        p = data.plot(kind='kde', linewidth=2, subplots=True, sharex=False)
        #        [p[i].set_ylabel('some') for i in range(k)]
        plt.legend()
        return plt

    def _get_result(self, vals):

        dataset = self.env['bnc.mining.kmeans.result'].search([('kmeansids', '=', self.id), ('col_c', '=', vals)])
        vals = []
        for data in dataset:
            vals.append({
                'partner': data['member'].id,
                'R': data['col_r'],
                'F': data['col_f'],
                'M': data['col_m'],
                'col_c': data['col_c'],
            })
        return vals

    def _query_report_result(self):
        sql = """
                select col_c,count(*) as number  
                from bnc_mining_kmeans_result 
                where kmeansids={0}
                group by col_c
        """
        sql = sql.format(self.id)
        cr = self._cr
        cr.execute(sql)
        res = cr.fetchall()
        return res


class bnc_mining_kmeans_result(models.Model):
    _name = "bnc.mining.kmeans.result"

    kmeansids = fields.Many2one('bnc.mining.kmeans', string=u'编号')
    member = fields.Many2one('res.partner', string=u'会员', ondelete='cascade')
    col_r = fields.Integer(string=u'未消费天数')
    col_f = fields.Integer(string=u'消费总频次-交易单数')
    col_m = fields.Float(string=u'消费金额')
    col_c = fields.Integer(string=u'聚类级别')

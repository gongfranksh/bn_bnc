# -*- coding: utf-8 -*-
import logging
import threading
from datetime import datetime
from dateutil.relativedelta import relativedelta
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


def get_kmeans_result(self, para_data):
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


def get_qcut_result(self, para_data):
    data = pd.DataFrame(data=para_data, columns=['partner', 'R', 'F', 'M'])
    data = data.set_index('partner')
    data = data.astype(float)
    F_num = 3
    labels = [1, 0]
    R_S = pd.qcut(data.R, 2, labels=labels)

    labels = [0, 1]
    M_S = pd.qcut(data.M, 2, labels=labels)

    data['F_S'] = 0
    data.loc[(data['F']) >= F_num, 'F_S'] = 1
    data['RFM'] = R_S.astype(str) + data.F_S.astype(str) + M_S.astype(str)
    del data['F_S']

    res=data.to_records()

    return res

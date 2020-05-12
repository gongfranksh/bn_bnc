# -*- coding: utf-8 -*-
{
    'name': "Buynow Memeber Card",

    'summary': """
                百乐卡消费标签系统
        
        """,

    'description': """
        百乐卡消费标签系统
    """,

    'author': "weiliang ",
    'website': "http://www.buynow.com.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'buynow',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['bn_pospal','bn_2dfire','product', 'base', 'stock', 'hr', 'account', 'sale', 'mail','point_of_sale','crm'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/bnc_tags_view.xml',
        'views/bnc_member_view.xml',
        'views/bnc_tags_process.xml',
        'views/bnc_tags_template.xml',
        'views/bnc_tags_rmf_template.xml',
        'views/bnc_lead_dashbord.xml',
        'views/bnc_lead_view.xml',
        'views/bnc_lead_assign.xml',
        'views/bnc_mining.xml',
        'views/res_company.xml',
        'views/report_bnc_member_kmeans.xml',
        'views/report_bnc_member_tag_report.xml',
        'wizards/proc_sync_bnc_member.xml',
        'wizards/proc_sync_jsport.xml',
        'wizards/proc_sync_buynow.xml',
        'wizards/proc_sync_yinbao.xml',
        'wizards/proc_sync_2dfire.xml',
        'wizards/proc_sync_eservices.xml',
        'data/business_data.xml',
        'data/company_data.xml',
        'data/user_data.xml',
       # 'data/bn_db_data.xml',
       'security/bnc_security.xml',
       'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
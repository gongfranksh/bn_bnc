# -*- coding: utf-8 -*-
{
    'name': "bn_2dfire",

    'summary': """
                    二维火系统数据接口
                    """,

    'description': """
                    二维火系统数据接口
    """,

    'author': "weiliang",
#    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'data interface',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/2dfire_data.xml',
        'data/2dfire_data_branch.xml',
        'data/2dfire_data_api_url.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
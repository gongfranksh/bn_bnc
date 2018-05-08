# -*- coding: utf-8 -*-
{
    'name': "bn_pospal",

    'summary': """
                           银豹数据对接接口模块""",

    'description': """
                         银豹数据对接接口模块
    """,

    'author': "weiliang",
#    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'api',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/yinbao_data.xml',        
        'data/yinbao_data_api_url.xml',    
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
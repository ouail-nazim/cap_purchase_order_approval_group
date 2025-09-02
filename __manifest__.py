# coding: utf-8
{
    'name': "Purchase order approval group",
    'summary':""" Purchase order approval group""",
    'description': """Purchase order approval group""",
    'author': "David Verove",
    'website': "",
    'category':"",
    'version':"18.1",
    'depends': ['hr','purchase','mail'],
    'data': [
        "datas/email_template.xml",
        "security/ir.model.access.csv",
        "views/purchase_order_approval_group_views.xml",
        "views/purchase_order_views.xml",
        "views/purchase_order_approvals_views.xml",
        "views/res_config_settings_views.xml",
    ],
    'demo': [],
}

# coding: utf-8
{
    'name': "Purchase order approval group",

    'summary':
                   """
                   Purchase order approval group
                   """,

    'description': """
        Purchase order approval group
    """,

    'author': "David Verove",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category':    '',
    'version':     '18.1',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase',
        'mail',
    ],

    # always loaded
    'data': [
        "datas/email_template.xml",
        "security/ir.model.access.csv",
        "views/purchase_order_approval_group_views.xml",
        "views/purchase_order_views.xml",
        "views/res_config_settings_views.xml",
    ],
    # only loaded in demonstration mode
    'demo': [],

    # 'pre_init_hook':'test_double_validation_disabled',
}

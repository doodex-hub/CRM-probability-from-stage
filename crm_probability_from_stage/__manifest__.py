# -*- coding: utf-8 -*-
{
    'name': "CRM Probability From Stage",
    'summary': """
        this module assigns probability values to different CRM stages, 
        enabling more accurate sales forecasting and better decision-making throughout the sales process.""",

    'description': """
        module automates the assignment of probability values to each stage in the CRM pipeline. 
        By mapping specific probabilities to various sales stages, this module enhances forecasting accuracy and aids sales teams in making informed decisions, 
        ultimately improving overall sales performance and efficiency.
    """,
    'author': "Doodex",
    'website': "https://www.doodex.net/",
    'category': 'Marketing/Sales',
    'version': '18.0.1.0',
    'depends': ['base','crm'],
    'images': ["static/description/banner.png",],
    'license': 'LGPL-3',
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_views.xml',
        'views/res_config_settings.xml',
    ],
    'assets': {
        'web.assets_tests': [
            'crm_probability_from_stage/static/tests/tours/**/*',
        ],
    },
    'application': False,
    'installable': True,
}

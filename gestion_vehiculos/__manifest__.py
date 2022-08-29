# -*- coding: utf-8 -*-
{
    'name': "Gestion de Vehiculos",

    'summary': """
        Modulo de Gestion de vehiculos""",

    'description': """
        Modulo de Gestion de vehiculos
    """,

    'author': "It Solutions",
    'website': "https://www.itechnologysol.com",

    
    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/sale_view_vehiculos.xml',
        'views/account_move_views.xml',
        #'views/marcas_modelos.xml',
    ],
  
}

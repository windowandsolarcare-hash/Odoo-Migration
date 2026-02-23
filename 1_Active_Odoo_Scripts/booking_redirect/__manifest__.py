# -*- coding: utf-8 -*-
{
    'name': 'Booking Redirect to Calendly',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Redirect booking URLs to Calendly with prefilled contact data',
    'description': """
        Custom URL redirect for reactivation campaign.
        
        Creates short booking URLs like: /book/12345
        Looks up contact data from Odoo
        Redirects to Calendly with prefilled name and address
    """,
    'author': 'Window & Solar Care',
    'website': 'https://window-solar-care.odoo.com',
    'depends': ['website', 'contacts'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

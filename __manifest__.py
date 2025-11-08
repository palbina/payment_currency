# -*- coding: utf-8 -*-

{
    'name': 'Payment Provider Currencies',
    'category': 'Website / Sale / Payment',
    'author': 'Daniel Santibáñez Polanco',
    'summary': 'Payment Provider: Allowed Currencies or Force convert to Currency',
    'website': 'https://globalresponse.cl',
    'version': "19.0.0",
    'description': """
Payment Provider Currencies module for Odoo 19
============================================

This module allows configuring currency restrictions and forced conversion
for payment providers in Odoo 19.

Features:
---------
- Configure allowed currencies per payment provider
- Force currency conversion for transactions
- Enhanced logging and error handling
- Compatible with Odoo 19 payment API
- Improved performance and caching

Usage:
-----
1. Go to Settings > Payments > Payment Providers
2. Select or create a payment provider
3. Configure allowed currencies in the Currency tab
4. Optionally enable forced currency conversion
5. Test with different currencies

Technical Notes:
--------------
- Enhanced for Odoo 19 compatibility
- Improved error handling and logging
- Better performance with optimized queries
- Follows Odoo 19 coding guidelines
""",
    'depends': [
                'payment',
            ],
    'external_dependencies': {
            'python': [],
    },
    'data': [
        'views/payment_acquirer.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
    'pre_init_hook': 'pre_init_hook',
}

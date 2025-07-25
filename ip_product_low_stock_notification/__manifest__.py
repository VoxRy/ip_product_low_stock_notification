
{
    'name': 'Product Low Stock Report/ Notification',
    'version': '15.0.1.0.2',
    'summary': 'Product Low stock notification based on different types (Global, Individual and Reordering Rules).',
    'description': """
        Product Low Stock Notification
        ==============================
        Available Key Features
        ----------------------
        * Product Low stock notification based on different types (Global, Individual and Reordering Rules).
        * Get detail of low stock products via email and can filter by Company and Location.
        * Print Low Stock Report directly using company and location filter.
        * Automatic Product Low Stock Notification by email to allowed user on defined time
    """,
    'category': 'Warehouse',
    'author': 'Kais Akram',
    'website': 'https://www.linkedin.com/in/kaisakram/',
    'license': 'OPL-1',
    'depends': ['stock', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/low_stock_notification_data.xml',
        'views/res_config_settings_views.xml',
        'views/product_template_views.xml',
        'wizard/low_stock_report_wizard_views.xml',
        'report/low_stock_report_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}



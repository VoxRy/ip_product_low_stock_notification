# -*- coding: utf-8 -*-
import ast
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    low_stock_notification_type = fields.Selection([
        ('global', 'Global'),
        ('individual', 'Individual'),
        ('reorder_rules', 'Reordering Rules')
    ], string='Notification Rule Type', default='global',
       config_parameter='ip_product_low_stock_notification.notification_type')

    global_minimum_quantity = fields.Float(
        string='Global Minimum Quantity',
        default=0.0,
        config_parameter='ip_product_low_stock_notification.global_minimum_quantity'
    )

    auto_notification_enabled = fields.Boolean(
        string='Enable Auto Notification',
        default=False,
        config_parameter='ip_product_low_stock_notification.auto_notification_enabled'
    )

    notification_time = fields.Float(
        string='Notification Time (Hours)',
        default=24.0,
        config_parameter='ip_product_low_stock_notification.notification_time'
    )

    notification_user_ids = fields.Many2many(
        'res.users',
        string='Notification Users'
    )

    notification_email_template = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'stock.quant')],
        config_parameter='ip_product_low_stock_notification.notification_email_template'
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        user_ids_str = IrConfigParam.get_param(
            'ip_product_low_stock_notification.notification_user_ids', default='[]'
        )
        try:
            user_ids = ast.literal_eval(user_ids_str)
        except Exception:
            user_ids = []

        res.update({
            'notification_user_ids': [(6, 0, user_ids)],
        })
        return res

    def set_values(self):
        super().set_values()
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        IrConfigParam.set_param(
            'ip_product_low_stock_notification.notification_user_ids',
            str(self.notification_user_ids.ids)
        )

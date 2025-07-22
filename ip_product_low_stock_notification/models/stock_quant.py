# -*- coding: utf-8 -*-
import ast
from odoo import models, fields, api
from datetime import datetime, timedelta


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def send_low_stock_notification(self):
        """Send low stock notification email to configured users"""
        param_env = self.env['ir.config_parameter'].sudo()

        auto_notification = param_env.get_param(
            'ip_product_low_stock_notification.auto_notification_enabled', default='False'
        )
        
        if auto_notification in ['False', False, '0', '', None]:
            return

        # Get notification user IDs from config (stored as string list)
        user_ids_param = param_env.get_param('ip_product_low_stock_notification.notification_user_ids', default='[]')
        
        try:
            user_ids = ast.literal_eval(user_ids_param)
        except Exception:
            user_ids = []

        if not user_ids:
            return

        users = self.env['res.users'].browse(user_ids)

        # Get low stock products
        low_stock_products = self.env['product.template'].get_low_stock_products()
        if not low_stock_products:
            return

        # Prepare email content
        email_body = self._prepare_low_stock_email_body(low_stock_products)

        # Send email to each user
        for user in users:
            if user.email:
                mail_values = {
                    'subject': 'Low Stock Notification',
                    'body_html': email_body,
                    'email_to': user.email,
                    'auto_delete': True,
                }
                mail = self.env['mail.mail'].create(mail_values)
                mail.send()

    def _prepare_low_stock_email_body(self, low_stock_products):
        """Prepare email body for low stock notification"""
        body = """
        <div style="font-family: Arial, sans-serif;">
            <h2>Low Stock Notification</h2>
            <p>The following products have low stock levels:</p>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px;">Product</th>
                        <th style="padding: 8px;">Current Quantity</th>
                        <th style="padding: 8px;">Minimum Quantity</th>
                    </tr>
                </thead>
                <tbody>
        """

        for item in low_stock_products:
            product = item['product']
            current_qty = item['current_qty']
            min_qty = item['min_qty']

            body += f"""
                <tr>
                    <td style="padding: 8px;">{product.name}</td>
                    <td style="padding: 8px;">{current_qty}</td>
                    <td style="padding: 8px;">{min_qty}</td>
                </tr>
            """

        body += """
                </tbody>
            </table>
            <p>Please take necessary action to replenish the stock.</p>
        </div>
        """

        return body
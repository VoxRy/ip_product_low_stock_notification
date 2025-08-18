# -*- coding: utf-8 -*-
import ast
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

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
            _logger.info("Low stock notification is disabled.")
            return

        # Get notification user IDs from config (stored as string list)
        user_ids_param = param_env.get_param(
            'ip_product_low_stock_notification.notification_user_ids', default='[]'
        )

        try:
            user_ids = ast.literal_eval(user_ids_param)
        except Exception:
            user_ids = []

        if not user_ids:
            _logger.warning("No users configured for low stock notification.")
            return

        users = self.env['res.users'].browse(user_ids)

        # Get low stock products (no company arg)
        low_stock_products = self.env['product.template'].get_low_stock_products(
            location_id=self.env.ref('stock.stock_location_stock').id
        )
        if not low_stock_products:
            _logger.info("No low stock products found.")
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
                    'auto_delete': False,
                }
                mail = self.env['mail.mail'].create(mail_values)
                mail.send()
                _logger.info("Low stock email sent to %s", user.email)

    def _prepare_low_stock_email_body(self, low_stock_products):
        """Prepare email body for low stock notification (with Internal Reference)"""
        rows = ""
        for item in low_stock_products:
            product_tmpl = item['product']           # product.template
            current_qty = item['current_qty']
            min_qty = item['min_qty']

            # Determine Internal Reference (default_code)
            # Prefer single-variant code, else fallback to template code or '-'
            code = "-"
            try:
                if getattr(product_tmpl, 'product_variant_count', 0) == 1 and product_tmpl.product_variant_id:
                    code = product_tmpl.product_variant_id.default_code or "-"
                else:
                    code = (getattr(product_tmpl, 'default_code', None) or "-")
            except Exception:
                code = "-"

            rows += f"""
                <tr>
                    <td style="padding: 8px;">{code}</td>
                    <td style="padding: 8px;">{product_tmpl.name}</td>
                    <td style="padding: 8px; text-align:right;">{current_qty}</td>
                    <td style="padding: 8px; text-align:right;">{min_qty}</td>
                </tr>
            """

        body = f"""
        <div style="font-family: Arial, sans-serif;">
            <h2>Low Stock Notification</h2>
            <p>The following products have low stock levels:</p>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px;">Internal Reference</th>
                        <th style="padding: 8px;">Product</th>
                        <th style="padding: 8px;">Current Quantity</th>
                        <th style="padding: 8px;">Minimum Quantity</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <p>Please take necessary action to replenish the stock.</p>
        </div>
        """
        return body

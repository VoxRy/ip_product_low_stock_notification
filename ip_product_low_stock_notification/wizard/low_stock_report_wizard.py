# models/low_stock_report_wizard.py

# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class LowStockReportWizard(models.Model):
    _name = 'low.stock.report.wizard'
    _description = 'Low Stock Report Wizard'

    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        domain=[('usage', '=', 'internal')]
    )

    report_type = fields.Selection([
        ('pdf', 'PDF Report'),
        ('email', 'Send Email')
    ], string='Report Type', default='pdf', required=True)

    user_ids = fields.Many2many(
        'res.users',
        string='Send to Users',
        help="Users to send the low stock notification email"
    )

    low_stock_report_line_ids = fields.One2many(
        'low.stock.report.line',
        'wizard_id',
        string='Low Stock Report Lines',
        help="Lines for low stock report"
    )

    def action_generate_report(self):
        """Generate low stock report"""
        low_stock_products_data = self.env['product.template'].get_low_stock_products(
            location_id=self.location_id.id if self.location_id else None
        )

        if not low_stock_products_data:
            raise UserError("No low stock products found with the selected criteria.")

        for item in low_stock_products_data:
            product = item['product'].product_variant_id  # Use product.product
            self.env['low.stock.report.line'].create({
                'wizard_id': self.id,
                'product_id': product.id,
                'current_quantity': item['current_qty'],
                'minimum_quantity': item['min_qty'],
            })
            _logger.info("✅ Line created: %s (%s)", product.display_name, item['current_qty'])

        _logger.info("📊 Wizard %s has %s lines", self.id, len(self.low_stock_report_line_ids))

        if self.report_type == 'pdf':
            return self._generate_pdf_report()
        elif self.report_type == 'email':
            return self._send_email_report(low_stock_products_data)

    def _generate_pdf_report(self):
        """Generate PDF report for low stock products"""
        return self.env.ref('ip_product_low_stock_notification.action_low_stock_report').report_action(self)

    def _send_email_report(self, low_stock_products):
        """Send email report for low stock products"""
        if not self.user_ids:
            raise UserError("Please select users to send the email.")

        email_body = self.env['stock.quant']._prepare_low_stock_email_body(low_stock_products)

        for user in self.user_ids:
            if user.email:
                mail_values = {
                    'subject': 'Low Stock Report',
                    'body_html': email_body,
                    'email_to': user.email,
                    'auto_delete': True,
                }
                mail = self.env['mail.mail'].create(mail_values)
                mail.send()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Low stock notification sent to {len(self.user_ids)} users.',
                'type': 'success',
            }
        }

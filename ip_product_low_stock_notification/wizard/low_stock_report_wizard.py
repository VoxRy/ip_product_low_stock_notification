# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class LowStockReportWizard(models.TransientModel):
    _name = 'low.stock.report.wizard'
    _description = 'Low Stock Report Wizard'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
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

    def action_generate_report(self):
        """Generate low stock report"""
        low_stock_products = self.env['product.template'].get_low_stock_products(
            company_id=self.company_id.id if self.company_id else None,
            location_id=self.location_id.id if self.location_id else None
        )
        
        if not low_stock_products:
            raise UserError("No low stock products found with the selected criteria.")
            
        if self.report_type == 'pdf':
            return self._generate_pdf_report(low_stock_products)
        elif self.report_type == 'email':
            return self._send_email_report(low_stock_products)
            
    def _generate_pdf_report(self, low_stock_products):
        """Generate PDF report for low stock products"""
        data = {
            'company_id': self.company_id.id if self.company_id else None,
            'location_id': self.location_id.id if self.location_id else None,
            'low_stock_products': low_stock_products,
        }
        
        return self.env.ref('ip_product_low_stock_notification.action_low_stock_report').report_action(
            self, data=data
        )
        
    def _send_email_report(self, low_stock_products):
        """Send email report for low stock products"""
        if not self.user_ids:
            raise UserError("Please select users to send the email.")
            
        email_body = self.env['stock.quant']._prepare_low_stock_email_body(low_stock_products)
        
        for user in self.user_ids:
            if user.email:
                mail_values = {
                    'subject': f'Low Stock Report - {self.company_id.name if self.company_id else "All Companies"}',
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


# models/low_stock_report_line.py

# -*- coding: utf-8 -*-
from odoo import models, fields

class LowStockReportLine(models.Model):
    _name = 'low.stock.report.line'
    _description = 'Low Stock Report Line'

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    current_quantity = fields.Float(string='Current Quantity', readonly=True)
    minimum_quantity = fields.Float(string='Minimum Quantity', readonly=True)
    wizard_id = fields.Many2one('low.stock.report.wizard', string='Wizard', ondelete='cascade')

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    low_stock_notification_enabled = fields.Boolean(
        string='Enable Low Stock Notification',
        default=True,
        help="Enable low stock notification for this product"
    )
    
    minimum_stock_quantity = fields.Float(
        string='Minimum Stock Quantity',
        default=0.0,
        help="Minimum quantity for low stock notification"
    )
    
    @api.model
    def get_low_stock_products(self, company_id=None, location_id=None):
        """Get products with low stock based on configuration"""
        domain = [('type', '=', 'product')]
        
        if company_id:
            domain.append(('company_id', '=', company_id))
            
        products = self.search(domain)
        print(f"DEBUG: Found {len(products)} products.")
        low_stock_products = []
        
        notification_type = self.env['ir.config_parameter'].sudo().get_param(
            'ip_product_low_stock_notification.notification_type', 'global'
        )
        global_min_qty = float(self.env['ir.config_parameter'].sudo().get_param(
            'ip_product_low_stock_notification.global_minimum_quantity', 0.0
        ))
        
        print(f"DEBUG: Notification Type: {notification_type}, Global Min Qty: {global_min_qty}")

        for product in products:
            if not product.low_stock_notification_enabled:
                continue
                
            # Get current stock quantity
            quant_domain = [('product_id', 'in', product.product_variant_ids.ids)]
            if location_id:
                quant_domain.append(('location_id', '=', location_id))
            if company_id:
                quant_domain.append(('company_id', '=', company_id))
                
            quants = self.env['stock.quant'].search(quant_domain)
            current_qty = sum(quants.mapped('quantity'))
            
            print(f"DEBUG: Product: {product.name}, Current Qty: {current_qty}")

            # Determine minimum quantity based on notification type
            if notification_type == 'global':
                min_qty = global_min_qty
            elif notification_type == 'individual':
                min_qty = product.minimum_stock_quantity
            elif notification_type == 'reorder_rules':
                reorder_rule = self.env['stock.warehouse.orderpoint'].search([
                    ('product_id', 'in', product.product_variant_ids.ids)
                ], limit=1)
                min_qty = reorder_rule.product_min_qty if reorder_rule else 0.0
            else:
                min_qty = 0.0
                
            print(f"DEBUG: Product: {product.name}, Calculated Min Qty: {min_qty}")

            if current_qty <= min_qty:
                low_stock_products.append({
                    'product': product,
                    'current_qty': current_qty,
                    'min_qty': min_qty,
                })
                
        print(f"DEBUG: Low stock products found: {len(low_stock_products)}")
        return low_stock_products
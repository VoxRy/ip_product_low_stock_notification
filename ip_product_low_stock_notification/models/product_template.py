# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


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
    def get_low_stock_products(self, location_id=None):
        """Get products with low stock based on configuration (current env company)."""
        # Only storable products
        products = self.search([('type', '=', 'product')])
        _logger.debug("Found %s products.", len(products))
        low_stock_products = []

        icp = self.env['ir.config_parameter'].sudo()
        notification_type = icp.get_param(
            'ip_product_low_stock_notification.notification_type', 'global'
        )
        global_min_qty = float(icp.get_param(
            'ip_product_low_stock_notification.global_minimum_quantity', 0.0
        ))

        _logger.debug("Notification Type: %s, Global Min Qty: %s", notification_type, global_min_qty)

        # Safe stock context for the current company
        ctx = {
            'company_id': self.env.company.id,
            'allowed_company_ids': [self.env.company.id],
            'company_owned': True,
        }
        if location_id:
            ctx['location'] = location_id

        for product in products:
            if not product.low_stock_notification_enabled:
                continue

            # Sum available qty across variants under the context
            current_qty = sum(product.product_variant_ids.with_context(ctx).mapped('qty_available'))
            _logger.debug("Product: %s, Current Qty: %s", product.name, current_qty)

            # Determine minimum quantity per configuration
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

            _logger.debug("Product: %s, Calculated Min Qty: %s", product.name, min_qty)

            if min_qty > 0 and current_qty <= min_qty:
                low_stock_products.append({
                    'product': product,
                    'current_qty': current_qty,
                    'min_qty': min_qty,
                })

        _logger.info("Low stock products found: %s", len(low_stock_products))
        return low_stock_products

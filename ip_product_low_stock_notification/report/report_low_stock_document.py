# -*- coding: utf-8 -*-
from odoo import models
import logging

_logger = logging.getLogger(__name__)

class ReportLowStockDocument(models.AbstractModel):
    _name = 'report.low_stock_report_doc'
    _description = 'Low Stock Report PDF'

    def _get_report_values(self, docids, data=None):
        _logger.info("📄 Running _get_report_values")
        
        # docids doğrudan gelmeyebilir, data içinden al
        if not docids and data and 'doc_ids' in data:
            docids = data['doc_ids']

        wizard = self.env['low.stock.report.wizard'].browse(docids)

        if not wizard.exists():
            _logger.warning("⚠️ No wizard record found for docids: %s", docids)
            return {}

        return {
            'doc_ids': wizard.ids,
            'doc_model': 'low.stock.report.wizard',
            'docs': wizard,
        }

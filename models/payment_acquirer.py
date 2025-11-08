# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.tools import float_round
import logging
_logger = logging.getLogger(__name__)


class PaymentProviderCurrency(models.Model):
    _inherit = 'payment.provider'

    currency_ids = fields.Many2many(
        'res.currency',
        'payment_provider_currency_rel',
        'provider_id',
        'currency_id',
        string='Currencies',
        help="Use only these allowed currencies."
    )
    force_currency = fields.Boolean(
        string="Force Currency",
    )
    force_currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
    )

    def compute_fees(self, amount, currency_id, partner_country_id):
        """Compute fees for payment processing with currency support."""
        fees_method_name = f'{self.provider}_compute_fees'
        fees_amount = 0
        if hasattr(self, fees_method_name):
            fees = getattr(self, fees_method_name)(amount, currency_id, partner_country_id)
            fees_amount = float_round(fees, 2)
        return fees_amount

    def _get_available_currencies(self, partner_country_id=None):
        """Get available currencies for this acquirer."""
        self.ensure_one()
        
        if self.currency_ids:
            return self.currency_ids
        
        return self.env['res.currency'].search([('active', '=', True)])

    def _is_currency_available(self, currency_id):
        """Check if a currency is available for this acquirer."""
        self.ensure_one()
        
        if not self.currency_ids:
            return True
        
        return currency_id in self.currency_ids.ids


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _convert_to_currency(self, target_currency):
        """Convert the sale order to a different currency."""
        self.ensure_one()
        
        if self.currency_id == target_currency:
            return True
        
        # Update the pricelist to use the target currency
        pricelist = self.env['product.pricelist'].search([
            ('currency_id', '=', target_currency.id)
        ], limit=1)
        
        if not pricelist:
            # Create a temporary pricelist if none exists
            pricelist = self.env['product.pricelist'].create({
                'name': f'Temporary - {target_currency.name}',
                'currency_id': target_currency.id,
            })
        
        # Update the order with the new pricelist
        self.pricelist_id = pricelist.id
        
        # Recompute order lines
        self.order_line._compute_price_unit()
        
        return True
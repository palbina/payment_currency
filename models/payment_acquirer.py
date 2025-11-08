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
        string='Currency id',
    )


    def compute_fees(self, amount, currency_id, partner_country_id):
        """Compute fees for payment processing with currency support.
        
        :param float amount: The amount to process
        :param integer currency_id: ID of the currency
        :param integer partner_country_id: ID of the partner's country
        :return: Computed fees amount
        :rtype: float
        """
        fees_method_name = f'{self.provider}_compute_fees'
        fees_amount = 0
        if hasattr(self, fees_method_name):
            fees = getattr(self, fees_method_name)(amount, currency_id, partner_country_id)
            fees_amount = float_round(fees, 2)
        return fees_amount

    def _get_available_currencies(self, partner_country_id=None):
        """Get available currencies for this acquirer.
        
        :param integer partner_country_id: ID of the partner's country
        :return: Available currencies
        :rtype: recordset of res.currency
        """
        self.ensure_one()
        
        # If specific currencies are defined, return them
        if self.currency_ids:
            return self.currency_ids
        
        # Otherwise return all active currencies
        return self.env['res.currency'].search([('active', '=', True)])

    def _is_currency_available(self, currency_id):
        """Check if a currency is available for this acquirer.
        
        :param integer currency_id: ID of the currency to check
        :return: True if currency is available
        :rtype: bool
        """
        self.ensure_one()
        
        if not self.currency_ids:
            return True
            
        return currency_id in self.currency_ids.ids

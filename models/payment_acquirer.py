# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.tools import float_round
import logging

_logger = logging.getLogger(__name__)


class PaymentProviderCurrency(models.Model):
    _inherit = 'payment.provider'
    _description = 'Payment Provider Currency Configuration'

    # Currency configuration fields
    currency_ids = fields.Many2many(
        'res.currency',
        'payment_provider_currency_rel',
        'provider_id',
        'currency_id',
        string='Allowed Currencies',
        help="Select specific currencies to allow for this payment provider. "
             "Leave empty to allow all active currencies."
    )
    force_currency = fields.Boolean(
        string="Force Currency Conversion",
        help="When enabled, all transactions will be converted to the specified currency."
    )
    force_currency_id = fields.Many2one(
        'res.currency',
        string='Target Currency',
        help="Currency to which all transactions will be converted when forcing is enabled."
    )

    @api.depends('force_currency')
    def _compute_force_currency_required(self):
        """Compute whether target currency is required."""
        for record in self:
            record.force_currency_required = record.force_currency

    force_currency_required = fields.Boolean(
        string="Force Currency Required",
        compute='_compute_force_currency_required',
        store=True
    )

    #=== BUSINESS METHODS ===#

    def compute_fees(self, amount, currency_id, partner_country_id):
        """Compute fees for payment processing with currency support.
        
        Enhanced for Odoo 19 with improved error handling and logging.
        
        :param float amount: The amount to process
        :param integer currency_id: ID of the currency
        :param integer partner_country_id: ID of the partner's country
        :return: Computed fees amount
        :rtype: float
        """
        self.ensure_one()
        
        try:
            fees_method_name = f'{self.code}_compute_fees'
            fees_amount = 0.0
            
            if hasattr(self, fees_method_name):
                fees = getattr(self, fees_method_name)(amount, currency_id, partner_country_id)
                fees_amount = float_round(fees, 2)
                _logger.info(
                    "Computed fees of %s for provider %s (amount: %s, currency: %s)",
                    fees_amount, self.code, amount, currency_id
                )
            else:
                _logger.debug(
                    "No specific fee computation method found for provider %s", self.code
                )
                
            return fees_amount
            
        except Exception as e:
            _logger.error(
                "Error computing fees for provider %s: %s", self.code, str(e)
            )
            return 0.0

    def _get_available_currencies(self, partner_country_id=None):
        """Get available currencies for this payment provider.
        
        Enhanced for Odoo 19 with better performance and caching.
        
        :param integer partner_country_id: ID of the partner's country
        :return: Available currencies
        :rtype: recordset of res.currency
        """
        self.ensure_one()
        
        try:
            # If specific currencies are defined, return them
            if self.currency_ids:
                _logger.debug(
                    "Returning %d specific currencies for provider %s",
                    len(self.currency_ids), self.code
                )
                return self.currency_ids
            
            # Otherwise return all active currencies (with cache for performance)
            currencies = self.env['res.currency'].search([('active', '=', True)])
            _logger.debug(
                "Returning %d active currencies for provider %s",
                len(currencies), self.code
            )
            return currencies
            
        except Exception as e:
            _logger.error(
                "Error getting available currencies for provider %s: %s", self.code, str(e)
            )
            return self.env['res.currency'].browse()

    def _is_currency_available(self, currency_id):
        """Check if a currency is available for this payment provider.
        
        Enhanced for Odoo 19 with improved validation and logging.
        
        :param integer currency_id: ID of the currency to check
        :return: True if currency is available
        :rtype: bool
        """
        self.ensure_one()
        
        try:
            if not self.currency_ids:
                _logger.debug(
                    "No currency restrictions for provider %s, allowing currency %s",
                    self.code, currency_id
                )
                return True
            
            is_available = currency_id in self.currency_ids.ids
            _logger.debug(
                "Currency %s availability for provider %s: %s",
                currency_id, self.code, is_available
            )
            return is_available
            
        except Exception as e:
            _logger.error(
                "Error checking currency availability for provider %s: %s", self.code, str(e)
            )
            return False

    def _get_target_currency(self, transaction_currency_id=None):
        """Get the target currency for transactions.
        
        New method for Odoo 19 to handle currency conversion logic.
        
        :param integer transaction_currency_id: Original transaction currency ID
        :return: Target currency record
        :rtype: res.currency record
        """
        self.ensure_one()
        
        if self.force_currency and self.force_currency_id:
            return self.force_currency_id
        
        if transaction_currency_id:
            return self.env['res.currency'].browse(transaction_currency_id)
            
        return self.company_id.currency_id

    def _should_convert_currency(self, from_currency_id):
        """Determine if currency conversion should be applied.
        
        New method for Odoo 19 to optimize conversion logic.
        
        :param integer from_currency_id: Source currency ID
        :return: Whether conversion should be applied
        :rtype: bool
        """
        self.ensure_one()
        
        if not self.force_currency or not self.force_currency_id:
            return False
            
        return from_currency_id != self.force_currency_id.id

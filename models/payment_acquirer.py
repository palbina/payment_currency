# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.tools import float_round
from odoo.exceptions import ValidationError
from odoo import _
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

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _convert_to_currency(self, target_currency):
        """
        Convert the sale order to a different currency.
        
        :param target_currency: Target currency record
        :return: True if conversion successful
        :raises: ValidationError if conversion not allowed
        """
        self.ensure_one()
        _logger.info(f"Starting currency conversion for order {self.id} to {target_currency.name}")
        
        # Security validations
        if not target_currency or not target_currency.active:
            _logger.error(f"Invalid target currency for order {self.id}")
            raise ValidationError(_("Invalid target currency. Please select an active currency."))
        
        if self.state not in ['draft', 'sent']:
            _logger.warning(f"Cannot convert order {self.id} in state {self.state}")
            raise ValidationError(_("Currency conversion is only allowed for orders in draft or sent state."))
        
        # Check if conversion is needed
        if self.currency_id == target_currency:
            _logger.info(f"Order {self.id} already in target currency {target_currency.name}")
            return True
        
        try:
            # Search for existing pricelist
            _logger.info(f"Searching pricelist for currency {target_currency.name}")
            pricelist = self.env['product.pricelist'].search([
                ('currency_id', '=', target_currency.id)
            ], limit=1)
            
            if not pricelist:
                _logger.info(f"No pricelist found, creating temporary one for {target_currency.name}")
                # Create temporary pricelist
                pricelist = self.env['product.pricelist'].create({
                    'name': f'Temporal - {target_currency.name}',
                    'currency_id': target_currency.id,
                })
                _logger.info(f"Created pricelist {pricelist.id} for currency {target_currency.name}")
            
            # Update order with new pricelist
            _logger.info(f"Updating order {self.id} with pricelist {pricelist.id}")
            self.pricelist_id = pricelist.id
            
            # Recompute order lines
            _logger.info(f"Recomputing order lines for order {self.id}")
            self.order_line._compute_price_unit()
            
            _logger.info(f"Successfully converted order {self.id} to {target_currency.name}")
            return True
            
        except Exception as e:
            _logger.error(f"Error converting order {self.id} to {target_currency.name}: {str(e)}")
            raise

    def compute_fees(self, amount, currency_id, partner_country_id):
        """
        Compute fees for payment processing with currency support.
        
        :param float amount: The amount to process
        :param integer currency_id: ID of the currency
        :param integer partner_country_id: ID of the partner's country
        :return: Computed fees amount
        :rtype: float
        """
        _logger.info(f"Computing fees for provider {self.provider_code}, amount: {amount}, currency: {currency_id}")
        
        fees_method_name = f'{self.provider_code}_compute_fees'
        fees_amount = 0
        if hasattr(self, fees_method_name):
            try:
                fees = getattr(self, fees_method_name)(amount, currency_id, partner_country_id)
                fees_amount = float_round(fees, 2)
                _logger.info(f"Fees computed: {fees_amount} for provider {self.provider_code}")
            except Exception as e:
                _logger.error(f"Error computing fees for provider {self.provider_code}: {str(e)}")
                raise
        else:
            _logger.debug(f"No custom fee method found for provider {self.provider_code}")
            
        return fees_amount

    def _get_available_currencies(self, partner_country_id=None):
        """
        Get available currencies for this acquirer.
        
        :param integer partner_country_id: ID of the partner's country
        :return: Available currencies
        :rtype: recordset of res.currency
        """
        self.ensure_one()
        _logger.info(f"Getting available currencies for provider {self.provider_code}")
        
        # If specific currencies are defined, return them
        if self.currency_ids:
            _logger.info(f"Found {len(self.currency_ids)} specific currencies for provider {self.provider_code}")
            return self.currency_ids
        
        # Otherwise return all active currencies
        all_currencies = self.env['res.currency'].search([('active', '=', True)])
        _logger.info(f"No specific currencies defined, returning {len(all_currencies)} active currencies")
        return all_currencies

    def _is_currency_available(self, currency_id):
        """
        Check if a currency is available for this acquirer.
        
        :param integer currency_id: ID of the currency to check
        :return: True if currency is available
        :rtype: bool
        """
        self.ensure_one()
        _logger.debug(f"Checking if currency {currency_id} is available for provider {self.provider_code}")
        
        if not self.currency_ids:
            _logger.debug(f"No currency restrictions for provider {self.provider_code}, currency available")
            return True
            
        is_available = currency_id in self.currency_ids.ids
        _logger.info(f"Currency {currency_id} available for provider {self.provider}: {is_available}")
        return is_available

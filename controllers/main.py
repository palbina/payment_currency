# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class WebsiteSaleCurrency(WebsiteSale):
    """
    Enhanced website sale controller with currency support and automatic conversion.
    """

    def _get_shop_payment_values(self, order, **kwargs):
        """
        Override to filter payment providers by allowed currencies.
        
        :param order: Sale order record
        :param kwargs: Additional arguments
        :return: Updated payment values
        """
        _logger.info(f"Getting shop payment values for order {order.id if order else 'None'}")
        
        vals = super(WebsiteSaleCurrency, self)._get_shop_payment_values(order, **kwargs)
        
        # Security check
        if not order:
            _logger.warning("No order provided for payment values")
            return vals
        
        pricelist_context = dict(request.env.context)
        pricelist = False
        
        if not pricelist_context.get('pricelist'):
            try:
                pricelist = request.website.get_current_pricelist()
                pricelist_context['pricelist'] = pricelist.id
                _logger.info(f"Using current pricelist {pricelist.id} for order {order.id}")
            except Exception as e:
                _logger.error(f"Error getting current pricelist: {str(e)}")
                return vals
        else:
            try:
                pricelist = request.env['product.pricelist'].browse(
                                pricelist_context['pricelist'])
                _logger.info(f"Using context pricelist {pricelist.id} for order {order.id}")
            except Exception as e:
                _logger.error(f"Error browsing pricelist: {str(e)}")
                return vals
        
        # Validate pricelist and currency
        if not pricelist or not pricelist.currency_id:
            _logger.error(f"Invalid pricelist or currency for order {order.id}")
            return vals
        
        form_acquirers = []
        s2s_acquirers = []
        
        # Filter form acquirers by currency
        for acq in vals.get('form_acquirers', []):
            try:
                if acq.currency_ids and pricelist.currency_id.id not in acq.currency_ids.ids:
                    _logger.debug(f"Skipping acquirer {acq.id} - currency {pricelist.currency_id.id} not allowed")
                    continue
                form_acquirers.append(acq)
                _logger.debug(f"Added form acquirer {acq.id} for order {order.id}")
            except Exception as e:
                _logger.error(f"Error processing form acquirer {acq.id}: {str(e)}")
                continue
        
        # Filter s2s acquirers by currency
        for acq in vals.get('s2s_acquirers', []):
            try:
                if acq.currency_ids and pricelist.currency_id.id not in acq.currency_ids.ids:
                    _logger.debug(f"Skipping s2s acquirer {acq.id} - currency {pricelist.currency_id.id} not allowed")
                    continue
                s2s_acquirers.append(acq)
                _logger.debug(f"Added s2s acquirer {acq.id} for order {order.id}")
            except Exception as e:
                _logger.error(f"Error processing s2s acquirer {acq.id}: {str(e)}")
                continue
        
        vals.update(
            form_acquirers=form_acquirers,
            s2s_acquirers=s2s_acquirers
        )
        
        _logger.info(f"Filtered payment values for order {order.id}: {len(form_acquirers)} form, {len(s2s_acquirers)} s2s acquirers")
        return vals

    @http.route()
    def shop_payment_validate(self, sale_order_id=None, **post):
        """
        Override to handle currency conversion if needed before payment validation.
        
        :param sale_order_id: ID of the sale order
        :param post: POST data containing provider_id
        :return: Result of parent method
        """
        _logger.info(f"Validating payment for order {sale_order_id}")
        
        # Security validation
        if not sale_order_id:
            _logger.warning("No sale_order_id provided for payment validation")
            return super().shop_payment_validate(sale_order_id=sale_order_id, **post)
        
        try:
            order = request.env['sale.order'].sudo().browse(int(sale_order_id))
            
            if not order.exists():
                _logger.error(f"Order {sale_order_id} does not exist")
                return super().shop_payment_validate(sale_order_id=sale_order_id, **post)
            
            _logger.info(f"Processing payment validation for existing order {order.id}")
            
            provider_id = post.get('provider_id')
            if provider_id:
                try:
                    provider_id_int = int(provider_id)
                    provider = request.env['payment.acquirer'].sudo().browse(provider_id_int)
                    
                    if not provider.exists():
                        _logger.error(f"Provider {provider_id_int} does not exist")
                        return super().shop_payment_validate(sale_order_id=sale_order_id, **post)
                    
                    _logger.info(f"Found provider {provider.id} for order {order.id}")
                    
                    # Check if currency conversion is needed
                    if provider.force_currency and provider.force_currency_id:
                        if order.currency_id != provider.force_currency_id:
                            _logger.info(f"Converting order {order.id} from {order.currency_id.name} to {provider.force_currency_id.name}")
                            try:
                                order._convert_to_currency(provider.force_currency_id)
                                _logger.info(f"Successfully converted order {order.id} currency")
                            except Exception as e:
                                _logger.error(f"Error converting order {order.id} currency: {str(e)}")
                                # Don't block payment if conversion fails, log and continue
                        else:
                            _logger.info(f"Order {order.id} already in correct currency {provider.force_currency_id.name}")
                    else:
                        _logger.debug(f"No currency forcing for provider {provider.id}")
                        
                except ValueError:
                    _logger.error(f"Invalid provider_id format: {provider_id}")
                except Exception as e:
                    _logger.error(f"Error processing provider {provider_id}: {str(e)}")
            else:
                _logger.debug(f"No provider_id in post data for order {order.id}")
                
        except ValueError:
            _logger.error(f"Invalid sale_order_id format: {sale_order_id}")
        except Exception as e:
            _logger.error(f"Unexpected error in payment validation: {str(e)}")
        
        _logger.info(f"Calling parent shop_payment_validate for order {sale_order_id}")
        return super().shop_payment_validate(sale_order_id=sale_order_id, **post)


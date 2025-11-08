# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)


class WebsiteSaleCurrency(WebsiteSale):
    
    def _get_shop_payment_values(self, order, **kwargs):
        """Override to filter payment providers by allowed currencies."""
        vals = super()._get_shop_payment_values(order, **kwargs)
        
        # Get the order currency
        order_currency = order.currency_id
        
        # Filter payment providers by currency
        if 'payment_methods_sudo' in vals:
            # v19 uses payment_methods_sudo
            filtered_methods = vals['payment_methods_sudo'].filtered(
                lambda pm: pm.provider_id._is_currency_available(order_currency.id)
            )
            vals['payment_methods_sudo'] = filtered_methods
        
        # Also filter providers directly if present
        if 'providers_sudo' in vals:
            filtered_providers = vals['providers_sudo'].filtered(
                lambda p: p._is_currency_available(order_currency.id)
            )
            vals['providers_sudo'] = filtered_providers
        
        return vals
    
    @http.route()
    def shop_payment_validate(self, sale_order_id=None, **post):
        """Override to handle currency conversion if needed."""
        order = request.env['sale.order'].sudo().browse(sale_order_id)
        
        if order.exists():
            # Get the selected payment provider
            provider_id = post.get('provider_id')
            if provider_id:
                provider = request.env['payment.provider'].sudo().browse(int(provider_id))
                
                # Check if currency conversion is needed
                if provider.force_currency and provider.force_currency_id:
                    if order.currency_id != provider.force_currency_id:
                        # Convert order to provider currency
                        order._convert_to_currency(provider.force_currency_id)
        
        return super().shop_payment_validate(sale_order_id=sale_order_id, **post)
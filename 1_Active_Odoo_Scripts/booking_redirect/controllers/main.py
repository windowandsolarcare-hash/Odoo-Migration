# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

class BookingRedirect(http.Controller):
    
    @http.route('/book/<int:contact_id>', type='http', auth='public', website=True)
    def booking_redirect(self, contact_id, **kwargs):
        """
        Redirect to Calendly with prefilled contact data.
        
        URL format: https://window-solar-care.odoo.com/book/12345
        
        This will:
        1. Look up contact by ID
        2. Determine appropriate Calendly event slug based on city
        3. Redirect to Calendly with name and address prefilled
        """
        
        try:
            # Look up contact (sudo to allow public access to read contact data)
            contact = request.env['res.partner'].sudo().browse(contact_id)
            
            # Validate contact exists
            if not contact.exists():
                return request.render('website.404')
            
            # Get contact data
            full_name = contact.name or "Client"
            street_address = contact.street or ""
            city = contact.city or ""
            
            # Determine Calendly event slug based on city
            city_slug = "gb"  # Default: General Booking
            
            if "Palm Springs" in city:
                city_slug = "pmsg"
            elif "Rancho Mirage" in city:
                city_slug = "rm"
            elif "Palm Desert" in city:
                city_slug = "pd"
            elif "Indian Wells" in city:
                city_slug = "iw"
            elif "Indio" in city or "La Quinta" in city:
                city_slug = "indlaq"
            elif "Hemet" in city:
                city_slug = "ht"
            
            # URL encode name and address (simple encoding for spaces and special chars)
            name_encoded = full_name.replace(' ', '+').replace('&', '%26')
            address_encoded = street_address.replace(' ', '+').replace('#', '%23').replace('&', '%26')
            
            # Build Calendly URL with prefilled data
            calendly_url = (
                f"https://calendly.com/wasc/{city_slug}"
                f"?name={name_encoded}"
                f"&a1={contact_id}"
                f"&a2={address_encoded}"
            )
            
            # Redirect to Calendly
            return redirect(calendly_url, code=302)
            
        except Exception as e:
            # Log error and show 404
            request.env['ir.logging'].sudo().create({
                'name': 'booking_redirect',
                'type': 'server',
                'level': 'error',
                'message': f"Error in booking redirect for contact {contact_id}: {str(e)}",
                'path': 'booking_redirect.controllers.main',
                'line': '0',
                'func': 'booking_redirect'
            })
            return request.render('website.404')

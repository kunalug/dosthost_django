from io import BytesIO
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from invoicing.formatters.html import HTMLFormatter
from django.conf import settings
import os
from django.contrib.staticfiles import finders

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources.
    """
    if uri.startswith(settings.STATIC_URL):
        path = uri.replace(settings.STATIC_URL, "")
        result = finders.find(path)
        if result:
            if not isinstance(result, (list, tuple)):
                result = [result]
            return result[0]
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        return path
    return uri

class PDFFormatter(HTMLFormatter):
    template_name = 'invoicing/invoice_template.html'

    def _parse_description(self, description):
        """Helper function to parse plan descriptions into a dictionary."""
        if not description:
            return {}
        
        features = {}
        for line in description.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                features[key.strip()] = value.strip()
        return features

    def get_response(self, context={}):
        from .models import Logo, BillingConfig
        template = get_template(self.template_name)
        
        # The `invoice` object is the order instance
        order = self.invoice
        
        # Get plan features
        billing_cycle = order.billing_cycle
        if billing_cycle == 'yearly':
            details = order.hosting_plan.yearly_details
        elif billing_cycle == 'quarterly':
            details = order.hosting_plan.quarterly_details
        else:
            details = order.hosting_plan.monthly_details
        
        plan_features = self._parse_description(details)
        
        subtotal = order.total_amount - order.tax_amount + order.discount_amount

        context.update({
            'order': order,
            'invoice': order,  # For backward compatibility if needed
            'customer': order.user,
            'plan': order.hosting_plan,
            'subtotal': subtotal,
            'billing_address': {
                'name': f"{order.first_name} {order.last_name}",
                'address': order.address,
                'city': order.city,
                'state': order.state,
                'zip_code': order.zip_code,
                'country': order.country,
                'email': order.email,
                'phone': order.phone,
            },
            'plan_details': plan_features,
            'payment_method': order.payment_method,
            'transaction_id': order.transaction_id,
            'logo': Logo.objects.first(),
            'billing_config': BillingConfig.objects.first(),
        })
        
        html = template.render(context)
        result = BytesIO()
        
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{order.pk}.pdf"'
            return response
            
        return HttpResponse(f'We had some errors<pre>{html}</pre>')
from .models import Logo, Footer

def site_logo(request):
    try:
        logo = Logo.objects.first()
    except Logo.DoesNotExist:
        logo = None
    return {'site_logo': logo}

def footer_links(request):
    try:
        footer = Footer.objects.first()
    except Footer.DoesNotExist:
        footer = None
    return {'footer_links': footer}
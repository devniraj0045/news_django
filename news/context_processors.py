from .models import SiteConfiguration

def site_configuration(request):
    try:
        config = SiteConfiguration.objects.first()
        if not config:
            # Create default if missing
            config = SiteConfiguration.objects.create()
    except:
        config = None
        
    return {'site_config': config}

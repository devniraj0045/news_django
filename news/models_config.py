from django.db import models

class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=100, default="News Portal")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Recommended size: 200x50px")
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Upload .ico or .png")
    
    # Meta
    meta_description = models.TextField(blank=True, help_text="For SEO: Description of the website")
    
    # Header / Footer
    breaking_news_title = models.CharField(max_length=50, default="BREAKING")
    breaking_news_content = models.TextField(default="Welcome to the News Portal! This is a demo of the Breaking News Ticker.", help_text="Text to scroll in the header.")
    footer_text = models.CharField(max_length=200, default="© 2026 News Portal. All rights reserved.")
    
    # Contact
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return "Website Settings (Edit This)"

    def save(self, *args, **kwargs):
        # Singleton pattern: Ensure only one config exists
        if not self.pk and SiteConfiguration.objects.exists():
            return # Block creation of new instance if one exists
        return super(SiteConfiguration, self).save(*args, **kwargs)

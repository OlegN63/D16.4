from django.apps import AppConfig


class NewsPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'News_Portal'

    def ready(self):
        import News_Portal.signals



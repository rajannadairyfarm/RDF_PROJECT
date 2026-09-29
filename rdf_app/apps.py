from django.apps import AppConfig


# class RdfAppConfig(AppConfig):
#     name = 'rdf_app'


from django.apps import AppConfig


class RdfAppConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"

    name = "rdf_app"

    verbose_name = "Rajanna Dairy Farm"

    icon_name = "store"
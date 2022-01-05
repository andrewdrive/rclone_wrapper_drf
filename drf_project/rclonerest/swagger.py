from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title='Rclone API',
        description='Documentation',
        default_version=1,
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],

)
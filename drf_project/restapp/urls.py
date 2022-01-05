from django.urls import path
from rest_framework import routers
from restapp import views
from .views import CopyNoteViewSet


urlpatterns = [
       path('list_remotes/', views.list_remotes),
       path('config_dump/', views.config_dump),
       path('path_listing/', views.path_listing),
       path('rewrite_config/', views.rewrite_config),
       path('copy/', views.copy),
       path('core_stats/<jobid>', views.core_stats),
]

router = routers.SimpleRouter()
router.register('copy_notes', CopyNoteViewSet)
# router.register('existing_remotes', RcloneRemoteViewSet)
urlpatterns += router.urls
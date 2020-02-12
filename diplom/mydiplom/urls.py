from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import ClientClaimCreateView

urlpatterns = [
    path('newclaim/', ClientClaimCreateView.as_view(), name='new_claim'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
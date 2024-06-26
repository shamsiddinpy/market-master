from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import set_language

from apps.views.users import change_language
from root.settings import MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('apps.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
    path('change_language/<str:language>/', change_language, name='change_language'),
    path("i18n/", set_language, name='set_language'),
    path("__debug__/", include("debug_toolbar.urls")),
) + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL, document_root=STATIC_ROOT)

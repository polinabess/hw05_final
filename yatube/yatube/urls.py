from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


handler404 = 'core.views.page_not_found'
handler403 = 'core.views.csrf_failure'
handler500 = 'core.views.server_error'

urlpatterns = [
    path('', include('posts.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    # Все адреса с префиксом auth/
    # будут перенаправлены в модуль django.contrib.auth
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

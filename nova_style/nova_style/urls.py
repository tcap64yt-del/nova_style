from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("", include("user.urls")),
    path("admin/", include("staff.urls")),
    path("accounts/", include("allauth.urls")),
    path("product/", include("product.urls")),
    path("cart/", include("cart.urls")),
    path("order/", include("order.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path

from shopify_app.apps.shopify import views

urlpatterns = [
    path('login', views.Login.as_view(), name="login"),
    path('finalise', views.Finalise.as_view(), name="finalise"),
]

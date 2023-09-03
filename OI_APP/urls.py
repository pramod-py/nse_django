from django.urls import path
from . import views

# app_name = 'oi'  # Optional namespace for your app's URLs

urlpatterns = [
    # Define your app's URLs here
    path('', views.option_chain_view, name='index'),  # Example URL pattern
]

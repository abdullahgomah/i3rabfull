from django.urls import path
from .views import i3rab_view

app_name = 'api'

urlpatterns = [
    path('i3rab/', i3rab_view, name='i3rab_view'),
]

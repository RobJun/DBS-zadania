from django.urls import path
from  . import views

urlpatterns = [
    path('matches/<int:id>/top_purchases/',views.getTopPurchases),
    path('abilities/<int:id>/usage/', views.getUsage),
    path('statistics/tower_kills/',views.getTowerKills)
]
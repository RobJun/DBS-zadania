from django.urls import path
from  . import views

urlpatterns = [
    path('patches/', views.getPatches),
    path('players/<int:id>/game_exp/',views.getGame_exp),
    path('players/<int:id>/game_objectives/', views.getObjectives),
    path('players/<int:id>/abilities/',views.getAbilities)
]
from django.urls import path
from . import views

urlpatterns = [
    path("latest/", views.latestFound),
    path("new/", views.newItem),
    path("userfound/", views.markUserFound),
    path("user/<user_id>/", views.getItemOfUser),
    path("search/tag/<tag_id>/", views.getItemsByTag),
    path("search/", views.searchItem),
    path("<id>/", views.getItem),

    path("latest", views.latestFound),
    path("new", views.newItem),
    path("userfound", views.markUserFound),
    path("user/<user_id>", views.getItemOfUser),
    path("search/tag/<tag_id>", views.getItemsByTag),
    path("search", views.searchItem),
    path("<id>", views.getItem)
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_posts, name='get_all_posts'),
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/', views.get_post, name='get_post'),
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
]

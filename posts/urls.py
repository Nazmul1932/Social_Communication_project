from django.urls import path
from .views import post_comment_create_and_list_view,like_unlike_post_view,PostDeleteView,\
    PostUpdateView


app_name = 'posts'

urlpatterns = [
    path('', post_comment_create_and_list_view, name='post_comment_create_and_list'),
    path('like_unlike/', like_unlike_post_view, name='like_unlike_post'),
    path('delete/<pk>/', PostDeleteView.as_view(), name='post_delete_view'),
    path('update/<pk>/', PostUpdateView.as_view(), name='post-update-view'),
]
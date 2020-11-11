from django.urls import path
from .views import *

app_name = 'profiles'

urlpatterns = [
    path('myprofile/', my_profile_view, name='my-profile'),
    path('invites_received_view/', invites_received, name='invites_received_view'),
    path('profiles_list/', ProfileListView.as_view(), name='profiles_list'),
    path('invites_profiles_list/', invites_profiles_list, name='invites_profiles_list'),
    path('send_invitation/', send_invitation, name='send_invitation'),
    path('remove_from_friends/', remove_from_friends, name='remove_from_friends'),
    path('invites_received_view/accept/', accept_invitation, name='accept_invite'),
    path('invites_received_view/reject/', reject_invitation, name='reject_invite'),
    path('<slug>/', ProfileDetailView.as_view(), name='profile-detail-view'),
]
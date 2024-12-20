from django.urls import path
from .views import register,profile,scenario_question_view,game_complete_view,custom_login_view,home,game_results_view,leaderboard
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',home, name = 'home'),
    path('register/', register, name='register'),
    path('login/', custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/profile/', profile, name='profile'),
    path('scenario/<int:scenario_id>/question/<int:question_index>/', scenario_question_view, name='scenario_question'),
    path('scenario/<int:scenario_id>/complete/', game_complete_view, name='game_complete'),
    path('results/', game_results_view, name='game_results'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]



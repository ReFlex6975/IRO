from django.urls import path
from .views import SignUpView, CustomLoginView, profile_view, CustomLogoutView, ProfileEditView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/<int:id>/', profile_view, name='profile'),  # URL для просмотра профиля по id
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
]
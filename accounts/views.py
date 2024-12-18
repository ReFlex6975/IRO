from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .forms import CustomUserCreationForm, ProfileEditForm, CustomLoginForm
from django.contrib.auth.views import LoginView, LogoutView

from .models import CustomUser


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/pages/signup.html'


class CustomLoginView(LoginView):
    template_name = 'accounts/pages/login.html'
    form_class = CustomLoginForm

    def get_success_url(self):
        return reverse_lazy('home')


def profile_view(request, id):
    user = get_object_or_404(CustomUser, id=id)
    return render(request, 'accounts/pages/profile.html', {'user': user})


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class ProfileEditView(UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'accounts/pages/profile_edit.html'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'id': self.request.user.id})

    def get_object(self):
        return self.request.user

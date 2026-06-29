from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import gettext as _


class PasswordChange(LoginRequiredMixin, View):
    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, 'registration/password_change.html', {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if not form.is_valid():
            messages.warning(request, _('Veuillez remplir le formulaire correctement'))
            return render(request, 'registration/password_change.html', {'form': form})

        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, _('Votre mot de passe a été mis à jour avec succès'))
        return redirect('core:home')

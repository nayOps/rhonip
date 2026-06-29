from django.contrib.auth.views import LoginView

from core.auth_forms import EmployeeAuthenticationForm


class EmployeeLogin(LoginView):
    template_name = 'registration/login.html'
    authentication_form = EmployeeAuthenticationForm
    redirect_authenticated_user = True

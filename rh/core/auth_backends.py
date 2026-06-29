from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmployeeIdentifierBackend(ModelBackend):
    """Connexion avec l'e-mail pro, le matricule ou l'e-mail du compte utilisateur."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if not username or not password:
            return None

        user = self._resolve_user(username.strip())
        if user is None:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def _resolve_user(self, identifier):
        User = get_user_model()
        user = User.objects.filter(email__iexact=identifier).select_related('employee').first()
        if user:
            return user

        from employee.models import Employee

        employee = Employee.objects.filter(email_professional__iexact=identifier).first()
        if employee:
            return User.objects.filter(employee=employee).first()

        employee = Employee.objects.filter(registration_number__iexact=identifier).first()
        if employee:
            return User.objects.filter(employee=employee).first()

        return None

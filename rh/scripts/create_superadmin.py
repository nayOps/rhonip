from django.contrib.auth import get_user_model

User = get_user_model()
EMAIL = "admin@onip.local"
PASSWORD = "OnipAdmin2025!"

user, created = User.objects.get_or_create(
    email=EMAIL,
    defaults={"is_staff": True, "is_superuser": True, "is_active": True},
)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.set_password(PASSWORD)
user.save()

print("created" if created else "updated")
print(f"email={EMAIL}")

```markdown
# Payday ONIP

## Environment Variables

The following environment variables are required for the application:

- `DEBUG`: Set to 1 or 0 to enable or disable activity logging.
- `SECRET_KEY`: Used to generate a unique password hash.
- `ALLOWED_HOSTS`: Replace with the deployed host domain. If multiple, separate with commas.
- `DATABASE_URL`: Connection with the chosen database. PostgreSQL is recommended.

### File System Storage Settings

- `STATIC_URL`
- `AWS_LOCATION`
- `AWS_DEFAULT_ACL`
- `AWS_S3_REGION`
- `AWS_ACCESS_KEY_ID`
- `AWS_S3_ENDPOINT_URL`
- `AWS_S3_CUSTOM_DOMAIN`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `STATICFILES_STORAGE`
- `PUBLIC_MEDIA_LOCATION`
- `DEFAULT_FILE_STORAGE`
- `MEDIA_URL`

### Email Settings

Depends on `DEBUG` variable. If disabled, the SMTP Backend will be activated.

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `ADMIN_EMAIL`: Receives all maintenance or error messages.
- `DEFAULT_FROM_EMAIL`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`

### Other Settings

- `PASSWORD_RESET_REDIRECT_URL`
- `CELERY_RESULT_BACKEND`: Redis broker URL.
- `CELERY_BROKER_URL`: Redis broker URL.

### Keycloak Settings

- `KEYCLOAK_BASE_URL`: External URL.
- `KEYCLOAK_INTERNAL_URL`: Docker compose URL.
- `KEYCLOAK_BASE_PATH`
- `KEYCLOAK_REALM`
- `KEYCLOAK_CLIENT_ID`
- `KEYCLOAK_CLIENT_SECRET_KEY`
- `KEYCLOAK_CLIENT_ADMIN_ROLE`
- `KEYCLOAK_REALM_ADMIN_ROLE`
- `KEYCLOAK_EXEMPT_URIS`

- `CORS_ORIGIN_WHITELIST`: List of origin whitelist with comma. Use the deployed host URL.

## Installation

1. Place the base source code into the targeted folder for deployment.
2. Ensure Docker's latest version is installed.
3. Run the following command: `docker-compose -f docker-compose-onip.yml up`.
4. Create a realm & app that will be linked to the Payday core app.
    - Include or replace the generated information in `docker/.env`. Ensure the values are correctly copied.
5. Stop the running Docker stacks & restart with the `.env` updated according to the provided information from the third stack.
```
Please replace the placeholders with the actual values.

Note:
Run this command
python manage.py shell < loader.py
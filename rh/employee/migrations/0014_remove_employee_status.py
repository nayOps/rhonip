from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0013_employee_marital_divorced_agent_situation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='status',
        ),
    ]

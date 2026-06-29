# Generated manually — tous les champs employé / inlines optionnels

import core.models.fields.date_field
import core.models.fields.model_select_field
import core.utils
import phonenumber_field.modelfields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('employee', '0005_payroll_period_and_line'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='registration_number',
            field=models.CharField(
                blank=True,
                default=None,
                max_length=50,
                null=True,
                unique=True,
                verbose_name='matricule',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='agreement',
            field=core.models.fields.model_select_field.ModelSelect(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='employee.agreement',
                verbose_name='type de contrat',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='branch',
            field=core.models.fields.model_select_field.ModelSelect(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='employee.branch',
                verbose_name='site',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='direction',
            field=core.models.fields.model_select_field.ModelSelect(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='employee.direction',
                verbose_name='direction',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='gender',
            field=models.CharField(
                blank=True,
                choices=[('male', 'masculin'), ('female', 'féminin')],
                default=None,
                max_length=10,
                null=True,
                verbose_name='genre',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='type_of_identity',
            field=models.CharField(
                blank=True,
                choices=[
                    ('driver_license', 'permis de conduire'),
                    ("voter's card", 'carte d\'électeur'),
                    ('national_id', 'national id'),
                    ('passport', 'passeport'),
                    ('document', 'document'),
                    ('other', 'other'),
                ],
                default=None,
                max_length=100,
                null=True,
                verbose_name="type de pièce d'identité",
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='marital_status',
            field=models.CharField(
                blank=True,
                choices=[('maried', 'marié(e)'), ('single', 'célibataire')],
                default=None,
                max_length=12,
                null=True,
                verbose_name='état civil',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='telephone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True,
                default=None,
                max_length=128,
                null=True,
                region=None,
                verbose_name='numéro de téléphone professional',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='mobile_number',
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True,
                default=None,
                max_length=128,
                null=True,
                region=None,
                verbose_name='numéro de téléphone mobile',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='emergency_information',
            field=models.TextField(
                blank=True,
                default=None,
                null=True,
                verbose_name="informations d'urgence",
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='emergency_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True,
                default=None,
                max_length=128,
                null=True,
                region=None,
                verbose_name="numéro de téléphone d'urgence",
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='refering_doctor_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True,
                default=None,
                max_length=128,
                null=True,
                region=None,
                verbose_name='numéro de téléphone du médecin référent',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='payment_method',
            field=models.CharField(
                blank=True,
                choices=[
                    ('cash', 'cash'),
                    ('bank', 'banque'),
                    ('mobile money', 'mobile money'),
                ],
                default=None,
                max_length=20,
                null=True,
                verbose_name='mode de paiement',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='payer_name',
            field=models.CharField(
                blank=True,
                default=None,
                max_length=50,
                null=True,
                verbose_name='nom du payeur',
            ),
        ),
        migrations.AlterField(
            model_name='child',
            name='full_name',
            field=models.CharField(
                blank=True,
                default=None,
                max_length=100,
                null=True,
                verbose_name='nom complet',
            ),
        ),
        migrations.AlterField(
            model_name='document',
            name='document',
            field=models.FileField(
                blank=True,
                default=None,
                null=True,
                upload_to=core.utils.upload_directory_file,
                verbose_name='document',
            ),
        ),
        migrations.AlterField(
            model_name='document',
            name='name',
            field=models.CharField(
                blank=True,
                default=None,
                max_length=100,
                null=True,
                verbose_name='nom',
            ),
        ),
        migrations.AlterField(
            model_name='education',
            name='degree',
            field=models.CharField(
                blank=True,
                default=None,
                max_length=100,
                null=True,
                verbose_name='diplôme',
            ),
        ),
        migrations.AlterField(
            model_name='experience',
            name='start_date',
            field=core.models.fields.date_field.DateField(
                blank=True,
                default=None,
                null=True,
                verbose_name='date de début',
            ),
        ),
    ]

from django.utils.translation import gettext as _
from celery import shared_task
from django.apps import apps
import pandas as pd

from core.models import ImporterStatus
from core.utils import notify

@shared_task(name='daily')
def daily():
    qs = apps.get_model('core', 'job').objects.all()
    for obj in qs:
        try:
            exec(obj.job, locals(), globals())
        except:
            pass

@shared_task(name='importer')
def importer(pk):
    model = apps.get_model('core', 'importer')
    obj = model.objects.get(pk=pk)

    # Check if user has permission to add
    permission = '{}.add_{}'.format(obj.content_type.app_label, obj.content_type.model)
    if not obj.created_by.has_perm(permission):
        obj.metadata = {'message': _('Vous n\'avez pas la permission d\'ajouter des données')}
        obj.status = ImporterStatus.ERROR
        obj.notify_me()
        obj.save()
        return

    # Update status
    obj.status = ImporterStatus.PROCESSING
    obj.save()

    # Get model
    model = obj.content_type.model_class()
    fields = {field.verbose_name:field for field in model._meta.fields}
    
    # Read excel file
    df = pd.read_excel(obj.document)
    df = df.where(pd.notnull(df), None)
    df.columns = [fields[col.lower()].name for col in df.columns]
    fields = {field.name:field.related_model.objects.values('id', 'name') 
            for field in fields.values() if field.is_relation and field.name in df.columns}

    try:
        data = df.to_dict(orient='records')
        [row.update({'created_by': obj.created_by}) for row in data]
        [row.update({f'{field}_id': choices.get(name=row[field]).get('id') 
                    for field, choices in fields.items()}) for row in data]
        
        # remove all foreign key fields
        [row.pop(field) for field in fields.keys() for row in data]
        data = [model(**row) for row in data]
        model.objects.bulk_create(data, ignore_conflicts=True)
    except Exception as e:
        obj.metadata = {'message': str(e)}
        obj.status = ImporterStatus.ERROR
        obj.notify_me()
        obj.save()
        return

    obj.status = ImporterStatus.SUCCESS
    obj.notify_me()
    obj.save()
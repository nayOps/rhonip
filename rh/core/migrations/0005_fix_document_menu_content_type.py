from django.db import migrations


def fix_document_menu(apps, schema_editor):
    Menu = apps.get_model('core', 'Menu')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    employee_document = ContentType.objects.filter(app_label='employee', model='document').first()
    if not employee_document:
        return

    stale = ContentType.objects.filter(app_label='core', model='document').first()
    for menu in Menu.objects.filter(name='Document'):
        children = list(menu.children.all())
        if stale and stale in children:
            menu.children.remove(stale)
        if employee_document not in menu.children.all():
            menu.children.add(employee_document)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_fix_admin_log_user_fk'),
        ('employee', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(fix_document_menu, migrations.RunPython.noop),
    ]

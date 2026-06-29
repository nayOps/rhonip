"""Corrige le mojibake UTF-8 (ex. Employ├⌐ → Employé) dans les champs texte."""
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models


def fix_mojibake(value: str) -> str:
    if not value or not isinstance(value, str):
        return value
    if '├' not in value and 'Ã' not in value and 'â€' not in value:
        return value
    for encoding in ('cp437', 'latin1'):
        try:
            fixed = value.encode(encoding).decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
        if fixed != value:
            return fixed
    return value


class Command(BaseCommand):
    help = 'Répare les caractères accentués corrompus (mojibake) en base.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les corrections sans écrire.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        updated_rows = 0
        updated_fields = 0

        for model in apps.get_models():
            if model._meta.app_label in {'contenttypes', 'sessions', 'admin'}:
                continue
            text_fields = [
                field
                for field in model._meta.get_fields()
                if isinstance(field, (models.CharField, models.TextField))
                and hasattr(field, 'attname')
            ]
            if not text_fields:
                continue

            for obj in model.objects.all().iterator():
                changes = {}
                for field in text_fields:
                    current = getattr(obj, field.attname)
                    if not current:
                        continue
                    fixed = fix_mojibake(current)
                    if fixed != current:
                        changes[field.attname] = fixed
                if not changes:
                    continue
                updated_rows += 1
                updated_fields += len(changes)
                if dry_run:
                    self.stdout.write(f'{model._meta.label} #{obj.pk}: {changes}')
                else:
                    model.objects.filter(pk=obj.pk).update(**changes)

        mode = 'seraient corrigés' if dry_run else 'corrigés'
        self.stdout.write(
            self.style.SUCCESS(
                f'{updated_fields} champ(s) sur {updated_rows} ligne(s) {mode}.'
            )
        )

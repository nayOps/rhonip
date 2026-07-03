"""
Finalise les sessions d'enrôlement avec photo (FAILED, PENDING, …) et synchronise vers le RH.

Usage :
  python manage.py backfill_enrollment_photos
  python manage.py backfill_enrollment_photos --dry-run
  python manage.py backfill_enrollment_photos --resync-completed
"""
from django.core.management.base import BaseCommand

from apps.enrollment.services import EnrollmentOrchestrator


class Command(BaseCommand):
    help = (
        'Finalise les sessions avec photo capturée (sync RH + COMPLETED) '
        'et optionnellement re-synchronise les sessions déjà terminées.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les sessions éligibles sans modifier la base',
        )
        parser.add_argument(
            '--resync-completed',
            action='store_true',
            help='Re-synchronise aussi les sessions COMPLETED vers le RH',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        orchestrator = EnrollmentOrchestrator()
        results = orchestrator.backfill_sessions_with_photos(
            dry_run=dry_run,
            resync_completed=options['resync_completed'],
        )

        ok = [r for r in results if r.get('ok')]
        failed = [r for r in results if not r.get('ok')]

        self.stdout.write(f'Sessions traitées : {len(results)}')
        self.stdout.write(self.style.SUCCESS(f'  OK : {len(ok)}'))
        if failed:
            self.stdout.write(self.style.WARNING(f'  Échecs : {len(failed)}'))

        for row in ok:
            suffix = ' (dry-run)' if row.get('dry_run') else ''
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {row.get('matricule')} — {row.get('session_id')}{suffix}"
                )
            )
        for row in failed:
            self.stdout.write(
                self.style.ERROR(
                    f"  ✗ {row.get('session_id')} — {row.get('error', '?')}"
                )
            )

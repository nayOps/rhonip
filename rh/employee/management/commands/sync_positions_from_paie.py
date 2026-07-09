from django.core.management.base import BaseCommand, CommandError

from employee.services.sync_positions_from_paie import sync_employee_positions_from_paie


class Command(BaseCommand):
    help = (
        "Aligne les positions RH (designation) sur le fichier de paie de référence "
        "(agents/Liste_Paie_ONIP_*.json)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            dest='file',
            default='',
            help='Chemin vers Liste_Paie_ONIP_*.json',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simule sans écrire en base.',
        )

    def handle(self, *args, **options):
        path = options['file'] or None
        try:
            stats = sync_employee_positions_from_paie(path=path, dry_run=options['dry_run'])
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(f"source: {stats['source']}")
        self.stdout.write(f"agents paie: {stats['payroll_agents']}")
        self.stdout.write(f"mis a jour: {stats['updated']}")
        self.stdout.write(f"deja conformes: {stats['already_ok']}")
        self.stdout.write(f"absents du RH: {stats['missing_in_rh']}")
        self.stdout.write(f"fonction vide (paie): {stats['empty_fonction']}")

        for change in stats.get('changes') or []:
            self.stdout.write(
                f"  {change['matricule']} | {change['name']} | "
                f"{change['before']} -> {change['after']}"
            )

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Mode dry-run — aucune modification.'))
        elif stats['updated']:
            self.stdout.write(self.style.SUCCESS('Positions alignees sur le fichier paie.'))
        else:
            self.stdout.write(self.style.SUCCESS('Toutes les positions sont deja conformes au fichier paie.'))

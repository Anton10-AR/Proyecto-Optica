from django.core.management.base import BaseCommand

from core.roles import ROLES, configurar_roles


class Command(BaseCommand):
    help = 'Crea los roles (grupos) y les asigna los permisos definidos en core/roles.py.'

    def handle(self, *args, **options):
        configurar_roles()
        for nombre, permisos in ROLES.items():
            self.stdout.write(f'  {nombre}: {len(permisos)} permisos')
        self.stdout.write(self.style.SUCCESS('Roles configurados.'))

from django.core.management.base import BaseCommand

from core.roles import PERMISOS, ROLES


class Command(BaseCommand):
    help = 'Imprime la matriz de permisos por rol en formato Markdown.'

    def handle(self, *args, **options):
        roles = list(ROLES)
        self.stdout.write('| Módulo | Permiso | Código | ' + ' | '.join(roles) + ' |')
        self.stdout.write('|---|---|---|' + ':---:|' * len(roles))
        for modulo, codigos in PERMISOS.items():
            for codigo, descripcion in codigos.items():
                marcas = ' | '.join('✔' if codigo in ROLES[r] else '' for r in roles)
                self.stdout.write(f'| {modulo} | {descripcion} | `{codigo}` | {marcas} |')

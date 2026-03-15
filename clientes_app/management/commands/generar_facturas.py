from django.core.management.base import BaseCommand
from clientes_app.utils import generar_facturas_del_dia


class Command(BaseCommand):
    help = "Genera las facturas del día según fecha de vencimiento"

    def handle(self, *args, **kwargs):
        generar_facturas_del_dia()
        self.stdout.write(self.style.SUCCESS("Facturas del día procesadas correctamente"))
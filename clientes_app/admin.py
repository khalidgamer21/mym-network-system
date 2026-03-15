from django.contrib import admin
from .models import Cliente, Factura, Antena


class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "telefono",
        "direccion",
        "router",
        "tipo_ip",
        "ip",
        "dia_pago",
        "precio_mensual",
        "estado_pago",
    )

    search_fields = ("nombre", "telefono", "ip")


class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        "cliente",
        "mes",
        "año",
        "pagado",
        "fecha_generacion",
    )

    list_filter = ("pagado", "mes", "año")


admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Factura, FacturaAdmin)
admin.site.register(Antena)

admin.site.site_header = "MYM Internet - Administración"
admin.site.site_title = "MYM Internet"
admin.site.index_title = "Panel administrativo MYM"
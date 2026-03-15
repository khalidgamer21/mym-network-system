
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path
from clientes_app.views import clientes_pendientes, marcar_pagado, dashboard
from django.conf.urls.static import static
from django.conf import settings

from clientes_app.views import (
    dashboard,
    clientes_pendientes,
    marcar_pagado,
    generar_factura_cliente,
    generar_facturas_mes,
    clientes_por_antena,
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('pendientes/', clientes_pendientes, name='pendientes'),
    path('marcar-pagado/<int:cliente_id>/', marcar_pagado, name='marcar_pagado'),
    path('', dashboard, name='dashboard'),
    path('generar-factura/<int:cliente_id>/', generar_factura_cliente, name='generar_factura_cliente'),
    path('generar-facturas-mes/', generar_facturas_mes, name='generar_facturas_mes'),
    path('clientes-por-antena/', clientes_por_antena, name='clientes_por_antena')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
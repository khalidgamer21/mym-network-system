from reportlab.pdfgen import canvas
from django.conf import settings
import os
from datetime import datetime
from .models import Factura, Cliente
from django.shortcuts import render, get_object_or_404, redirect
from .models import Cliente, Factura, Antena
from django.db.models import Count, Sum, Prefetch
from django.contrib import messages
from django.utils import timezone
from .utils import generar_factura_pdf, obtener_fecha_vencimiento
import calendar
from datetime import date

def generar_factura_pdf(factura):

    cliente = factura.cliente

    carpeta_cliente = os.path.join(settings.MEDIA_ROOT, "facturas", cliente.nombre)

    os.makedirs(carpeta_cliente, exist_ok=True)

    nombre_archivo = f"{cliente.nombre}_{factura.mes}_{factura.año}.pdf"

    ruta_pdf = os.path.join(carpeta_cliente, nombre_archivo)

    c = canvas.Canvas(ruta_pdf)

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, "static", "logo_mym.png")
    c.drawImage(logo_path, 50, 750, width=120, height=60)

    # Empresa
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 760, "MYM INTERNET")

    # Datos cliente
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"Cliente: {cliente.nombre}")
    c.drawString(50, 680, f"Dirección: {cliente.direccion}")
    c.drawString(50, 660, f"Teléfono: {cliente.telefono}")

    # Factura
    c.drawString(50, 620, f"Factura correspondiente a: {factura.mes} {factura.año}")
    c.drawString(50, 600, f"Valor del servicio: ${cliente.precio_mensual}")
    c.drawString(50, 580, f"Día de pago: {cliente.dia_pago}")

    # Mensaje
    c.drawString(50, 540, "Estimado cliente, le recordamos realizar el pago de su servicio.")
    c.drawString(50, 520, "Gracias por confiar en MYM Internet.")

    # Firma
    c.drawString(50, 460, "Atentamente:")
    c.drawString(50, 440, "Administración MYM")

    c.save()

    factura.archivo_pdf = f"facturas/{cliente.nombre}/{nombre_archivo}"
    factura.save()
    

def clientes_pendientes(request):

    clientes = Cliente.objects.filter(estado_pago=False)

    return render(request, 'clientes_app/clientes_pendientes.html', {'clientes': clientes})


def marcar_pagado(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.estado_pago = True
    cliente.save()
    return redirect('pendientes')

def dashboard(request):
    total_clientes = Cliente.objects.count()
    clientes_pendientes = Cliente.objects.filter(estado_pago=False).count()
    clientes_pagados = Cliente.objects.filter(estado_pago=True).count()
    total_facturas = Factura.objects.count()
    
    antenas = Antena.objects.annotate(total_clientes=Count("cliente"))
    
    total_esperado = Cliente.objects.aggregate(total=Sum("precio_mensual"))["total"] or 0
    total_pagado = Cliente.objects.filter(estado_pago=True).aggregate(total=Sum("precio_mensual"))["total"] or 0
    total_pendiente = Cliente.objects.filter(estado_pago=False).aggregate(total=Sum("precio_mensual"))["total"] or 0

    contexto = {
        'total_clientes': total_clientes,
        'clientes_pendientes': clientes_pendientes,
        'clientes_pagados': clientes_pagados,
        'total_facturas': total_facturas,
        'antenas': antenas,
        "total_esperado": total_esperado,
        "total_pagado": total_pagado,
        "total_pendiente": total_pendiente,
    }

    return render(request, 'clientes_app/dashboard.html', contexto)

from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Cliente, Factura
from .utils import generar_factura_pdf, obtener_fecha_vencimiento


def generar_factura_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    hoy = date.today()
    año = hoy.year
    mes_num = hoy.month

    meses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    nombre_mes = meses[mes_num - 1]

    # Verificar si ya existe factura de este cliente en este mes
    factura_existente = Factura.objects.filter(
        cliente=cliente,
        año=año,
        mes=nombre_mes
    ).first()

    if factura_existente:
        messages.warning(
            request,
            f"La factura de {cliente.nombre} para {nombre_mes} {año} ya existe."
        )
        return redirect('/')

    fecha_vencimiento = obtener_fecha_vencimiento(año, mes_num, cliente.dia_pago)

    factura = Factura.objects.create(
        cliente=cliente,
        mes=nombre_mes,
        año=año,
        fecha_vencimiento=fecha_vencimiento,
        pagado=False
    )

    # ESTA es la función que usa el diseño bonito del PDF
    generar_factura_pdf(factura)

    messages.success(
        request,
        f"Factura generada correctamente para {cliente.nombre}."
    )
    return redirect('/')


def generar_facturas_mes(request):
    hoy = date.today()
    año = hoy.year
    mes_num = hoy.month

    meses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    nombre_mes = meses[mes_num - 1]

    clientes = Cliente.objects.all()
    generadas = 0
    existentes = 0

    for cliente in clientes:
        ya_existe = Factura.objects.filter(
            cliente=cliente,
            año=año,
            mes=nombre_mes
        ).exists()

        if ya_existe:
            existentes += 1
            continue

        fecha_vencimiento = obtener_fecha_vencimiento(año, mes_num, cliente.dia_pago)

        factura = Factura.objects.create(
            cliente=cliente,
            mes=nombre_mes,
            año=año,
            fecha_vencimiento=fecha_vencimiento,
            pagado=False
        )

        # ESTA es la función que usa el diseño bonito del PDF
        generar_factura_pdf(factura)
        generadas += 1

    messages.success(
        request,
        f"Proceso terminado. Facturas generadas: {generadas}. Ya existentes: {existentes}."
    )
    return redirect('/')




def clientes_por_antena(request):
    antenas = Antena.objects.prefetch_related('cliente_set').all()
    return render(request, 'clientes_app/clientes_por_antena.html', {'antenas': antenas})
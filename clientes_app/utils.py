import os
import calendar
from datetime import date, timedelta
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from .models import Factura, Cliente


def obtener_fecha_vencimiento(año, mes, dia_pago):
    ultimo_dia = calendar.monthrange(año, mes)[1]
    dia_real = min(dia_pago, ultimo_dia)
    return date(año, mes, dia_real)


def generar_factura_pdf(factura):
    cliente = factura.cliente

    nombre_cliente = cliente.nombre.replace(" ", "_")
    carpeta_cliente = os.path.join(settings.MEDIA_ROOT, "facturas", nombre_cliente)
    os.makedirs(carpeta_cliente, exist_ok=True)

    nombre_archivo = f"{cliente.nombre}_{factura.mes}_{factura.año}.pdf".replace(" ", "_")
    ruta_pdf = os.path.join(carpeta_cliente, nombre_archivo)

    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    width, height = A4

    # Paleta MYM
    azul_oscuro = colors.HexColor("#03122b")
    azul_medio = colors.HexColor("#0b2f6b")
    azul_brillante = colors.HexColor("#00a8ff")
    celeste = colors.HexColor("#6fd3ff")
    azul_suave = colors.HexColor("#e8f3ff")
    blanco = colors.white
    negro = colors.black
    gris_texto = colors.HexColor("#333333")

    # Fondo general
    c.setFillColor(azul_suave)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Encabezado principal
    c.setFillColor(azul_oscuro)
    c.rect(0, height - 110, width, 110, fill=1, stroke=0)

    # Franja brillante
    c.setFillColor(azul_brillante)
    c.rect(0, height - 115, width, 5, fill=1, stroke=0)

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, "static", "logo_mym.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 40, height - 92, width=95, height=55, mask='auto')

    # Empresa
    c.setFillColor(blanco)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(155, height - 58, "MYM INTERNET")

    c.setFont("Helvetica", 10)
    c.setFillColor(celeste)
    c.drawString(155, height - 78, "Internet de alta velocidad")

    # Número de factura y fecha
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(blanco)
    c.drawRightString(width - 40, height - 50, f"Factura")
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 40, height - 70, f"Emisión: {factura.fecha_generacion.strftime('%d/%m/%Y')}")

    # Caja datos cliente
    c.setFillColor(blanco)
    c.roundRect(35, height - 275, width - 70, 115, 14, fill=1, stroke=0)

    c.setStrokeColor(celeste)
    c.setLineWidth(1)
    c.roundRect(35, height - 275, width - 70, 115, 14, fill=0, stroke=1)

    c.setFillColor(azul_medio)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 180, "DATOS DEL CLIENTE")

    c.setFillColor(gris_texto)
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 205, f"Cliente: {cliente.nombre}")
    c.drawString(50, height - 225, f"Dirección: {cliente.direccion}")
    c.drawString(50, height - 245, f"Teléfono: {cliente.telefono}")

    antena_nombre = cliente.antena.nombre if cliente.antena else "Sin asignar"
    c.drawString(300, height - 205, f"Antena: {antena_nombre}")
    c.drawString(300, height - 225, f"IP: {cliente.ip}")
    c.drawString(300, height - 245, f"Router: {cliente.router}")

    # Caja detalle factura
    c.setFillColor(blanco)
    c.roundRect(35, height - 430, width - 70, 135, 14, fill=1, stroke=0)

    c.setStrokeColor(celeste)
    c.roundRect(35, height - 430, width - 70, 135, 14, fill=0, stroke=1)

    c.setFillColor(azul_medio)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 315, "DETALLE DE LA FACTURA")

    c.setFillColor(gris_texto)
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 340, f"Periodo facturado: {factura.mes} {factura.año}")
    c.drawString(50, height - 360, f"Fecha de vencimiento: {factura.fecha_vencimiento.strftime('%d/%m/%Y')}")

    # Estado
    c.setFillColor(azul_brillante)
    c.roundRect(50, height - 400, 110, 25, 8, fill=1, stroke=0)
    c.setFillColor(blanco)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(105, height - 392, "PENDIENTE")

    # Caja total a pagar
    c.setFillColor(azul_oscuro)
    c.roundRect(350, height - 400, 190, 70, 12, fill=1, stroke=0)

    c.setFillColor(celeste)
    c.setFont("Helvetica", 11)
    c.drawString(365, height - 355, "TOTAL A PAGAR")

    c.setFillColor(blanco)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(365, height - 380, f"${cliente.precio_mensual}")

    # Mensaje final
    c.setFillColor(azul_oscuro)
    c.roundRect(35, height - 520, width - 70, 60, 12, fill=1, stroke=0)

    c.setFillColor(blanco)
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 490, "Estimado cliente, le recordamos realizar el pago de su servicio.")
    c.drawString(50, height - 508, "Gracias por confiar en MYM Internet.")

    # Pie
    c.setFillColor(negro)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 110, "Atentamente:")

    c.setFont("Helvetica", 11)
    c.drawString(50, 90, "Administración MYM")

    # Línea final decorativa
    c.setFillColor(azul_brillante)
    c.rect(35, 60, width - 70, 4, fill=1, stroke=0)

    c.save()

    factura.archivo_pdf = f"facturas/{nombre_cliente}/{nombre_archivo}"
    factura.save()


def generar_facturas_del_dia(fecha_hoy=None):
    if fecha_hoy is None:
        fecha_hoy = date.today()

    año = fecha_hoy.year
    mes = fecha_hoy.month
    meses = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

    nombre_mes = meses[mes - 1]

    clientes = Cliente.objects.all()

    for cliente in clientes:
        fecha_vencimiento = obtener_fecha_vencimiento(año, mes, cliente.dia_pago)
        fecha_generacion = fecha_vencimiento - timedelta(days=1)

        if fecha_hoy == fecha_generacion:
            existe = Factura.objects.filter(
                cliente=cliente,
                año=año,
                mes=nombre_mes
            ).exists()

            if not existe:
                factura = Factura.objects.create(
                    cliente=cliente,
                    mes=nombre_mes,
                    año=año,
                    fecha_vencimiento=fecha_vencimiento,
                    pagado=False
                )
                generar_factura_pdf(factura)
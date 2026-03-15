from django.db import models


class Antena(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} - {self.ubicacion}"


class Cliente(models.Model):
    TIPO_IP = [
        ('Estatica', 'Estatica'),
        ('Dinamica', 'Dinamica'),
    ]

    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    ubicacion_maps = models.URLField(blank=True, null=True)

    router = models.CharField(max_length=100)
    tipo_ip = models.CharField(max_length=10, choices=TIPO_IP)
    ip = models.GenericIPAddressField()

    fecha_inicio = models.DateField()
    dia_pago = models.IntegerField()
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)

    estado_pago = models.BooleanField(default=False)

    antena = models.ForeignKey(
        Antena,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    mes = models.CharField(max_length=20)
    año = models.IntegerField()

    fecha_generacion = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    pagado = models.BooleanField(default=False)

    archivo_pdf = models.FileField(upload_to='facturas/', blank=True, null=True)

    def __str__(self):
        return f"Factura {self.cliente.nombre} {self.mes}-{self.año}"
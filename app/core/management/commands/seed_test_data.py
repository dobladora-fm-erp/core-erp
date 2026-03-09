from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from core.models import Departamento, Municipio
from terceros.models import Tercero
from inventario.models import Bodega, Item, CategoriaItem, UnidadMedida, InventarioBodega
from compras.models import FacturaCompra, DetalleCompra
from ventas.models import FacturaVenta, DetalleVenta
from tesoreria.models import CuentaBancaria, CuentaPorCobrar, PagoRecibido
from django.utils import timezone

class Command(BaseCommand):
    help = 'Inyecta docenas de registros de prueba (Compras, Ventas, Cartera) para dinamizar el Dashboard'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # 1. Asegurar Cuenta Bancaria
            banco, _ = CuentaBancaria.objects.get_or_create(nombre='Banco Industrial', tipo='Banco', defaults={'numero_cuenta':'123456789'})

            # 2. Geo y Terceros
            dep = Departamento.objects.filter(codigo_dane='11').first() or Departamento.objects.create(codigo_dane='11', nombre='Bogota DC')
            mun = Municipio.objects.filter(codigo_dane='11001').first() or Municipio.objects.create(codigo_dane='11001', departamento=dep, nombre='Bogota')

            prov1 = Tercero.objects.filter(numero_identificacion='900999111').first() or Tercero.objects.create(tipo_documento='NIT', numero_identificacion='900999111', tipo_persona='Juridica', razon_social='Siderurgica Nacional', es_proveedor=True, municipio=mun)
            cli1 = Tercero.objects.filter(numero_identificacion='10203040').first() or Tercero.objects.create(tipo_documento='CC', numero_identificacion='10203040', tipo_persona='Natural', nombres='Constructora', apellidos='Andina', es_cliente=True, municipio=mun)
            
            # 3. Bodega e Items Extras
            bodega = Bodega.objects.filter(nombre='Bodega Principal').first() or Bodega.objects.create(nombre='Bodega Principal')
            unidad = UnidadMedida.objects.filter(nombre='Unidad').first() or UnidadMedida.objects.create(nombre='Unidad', abreviatura='Un')
            cat = CategoriaItem.objects.filter(nombre='Producto Terminado').first() or CategoriaItem.objects.create(nombre='Producto Terminado')
            
            item1 = Item.objects.filter(codigo_sku='PERF-01').first() or Item.objects.create(codigo_sku='PERF-01', nombre='Perfil Estructural C', tipo_item='Almacenable', unidad_medida_base=unidad, categoria=cat, precio_base=15000)
            item2 = Item.objects.filter(codigo_sku='MALL-01').first() or Item.objects.create(codigo_sku='MALL-01', nombre='Malla Electrosoldada', tipo_item='Almacenable', unidad_medida_base=unidad, categoria=cat, precio_base=25000)

            hoy = date.today()

            # 4. Inyectar Compras (Genera CxP vía señales automáticamente)
            for i in range(1, 4):
                fc = FacturaCompra.objects.create(
                    proveedor=prov1,
                    numero_factura_proveedor=f'F-SID-{1000+i}',
                    fecha_emision=hoy - timedelta(days=i*5),
                    fecha_vencimiento=hoy + timedelta(days=30),
                )
                DetalleCompra.objects.create(factura=fc, item=item1, bodega_destino=bodega, cantidad=100*i, costo_unitario=10000)
                fc.estado = 'Confirmada'
                fc.save()

            # 5. Inyectar Ventas (Genera CxC vía señales automáticamente)
            for i in range(1, 6):
                fv = FacturaVenta.objects.create(
                    cliente=cli1,
                    numero_factura=f'VEN-{2000+i}',
                    fecha_emision=hoy - timedelta(days=i*2),
                    fecha_vencimiento=hoy + timedelta(days=15),
                )
                DetalleVenta.objects.create(factura=fv, item=item1, bodega_origen=bodega, cantidad=10*i, precio_unitario=15000)
                fv.estado = 'Confirmada'
                fv.save()

            # 6. Realizar un par de pagos a CxC para demostrar interacción en tesorería
            cxc = CuentaPorCobrar.objects.filter(estado='Pendiente').first()
            if cxc:
                PagoRecibido.objects.create(
                    cuenta_por_cobrar=cxc,
                    cuenta_destino=banco,
                    monto=cxc.saldo_pendiente / 2, # Pago del 50%
                    referencia='TRX-99999'
                )

        self.stdout.write(self.style.SUCCESS('¡REGISTROS DE PRUEBA INYECTADOS SATISFACTORIAMENTE! (Compras, Ventas, Pagos parciales e Inventario)'))

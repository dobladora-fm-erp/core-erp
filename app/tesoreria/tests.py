from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from core.models import Departamento, Municipio
from terceros.models import Tercero
from ventas.models import FacturaVenta
from .models import CuentaBancaria, CuentaPorCobrar, PagoRecibido

class TesoreriaSignalAndValidationTests(TestCase):
    def setUp(self):
        # 1. Crear Departamento y Municipio requeridos por Tercero
        depto = Departamento.objects.create(codigo_dane='05', nombre='Antioquia')
        muni = Municipio.objects.create(departamento=depto, codigo_dane='05001', nombre='Medellín')

        # 2. Crear un tercero cliente
        self.cliente = Tercero.objects.create(
            es_cliente=True,
            tipo_documento='NIT',
            numero_identificacion='123456789',
            tipo_persona='Juridica',
            razon_social='Cliente Prueba S.A.S',
            municipio=muni,
            direccion='Calle Falsa 123',
            telefono='555-1234',
            correo_electronico='cliente@prueba.com',
            regimen_iva='Responsable',
            responsabilidades_fiscales='O-13'
        )

        # 3. Crear una Cuenta Bancaria
        self.banco = CuentaBancaria.objects.create(
            nombre='Cuenta Corriente Principal',
            entidad_bancaria='Bancolombia',
            tipo_cuenta='Corriente',
            numero_cuenta='987654321',
            saldo_actual=Decimal('0.00')
        )

    def test_flujo_cxc_y_pago_completo(self):
        # 1. Crear FacturaVenta
        factura = FacturaVenta.objects.create(
            cliente=self.cliente,
            numero_factura='FV-2026-0001',
            fecha_emision=timezone.now().date(),
            fecha_vencimiento=timezone.now().date(),
            subtotal=Decimal('100000.00'),
            impuestos=Decimal('19000.00'),
            total=Decimal('119000.00'),
            estado='Borrador'
        )

        # Asegurarse que no se crea CxC si está en Borrador
        self.assertFalse(CuentaPorCobrar.objects.filter(factura_origen=factura).exists())

        # Confirmar factura
        factura.estado = 'Confirmada'
        factura.save()

        # Verificar que nace automáticamente la Cuenta por Cobrar vía signal
        cxc_exists = CuentaPorCobrar.objects.filter(factura_origen=factura).exists()
        self.assertTrue(cxc_exists)
        cxc = CuentaPorCobrar.objects.get(factura_origen=factura)
        self.assertEqual(cxc.saldo_pendiente, Decimal('119000.00'))
        self.assertEqual(cxc.estado, 'Pendiente')

        # 2. Registrar un pago parcial
        pago1 = PagoRecibido.objects.create(
            cuenta_por_cobrar=cxc,
            cuenta_destino=self.banco,
            monto=Decimal('50000.00'),
            referencia='Transferencia Bancaria #001'
        )

        # Recargar objetos de la base de datos
        cxc.refresh_from_db()
        self.banco.refresh_from_db()

        # Verificar decremento de saldo de deuda e incremento de saldo en banco
        self.assertEqual(cxc.saldo_pendiente, Decimal('69000.00'))
        self.assertEqual(cxc.estado, 'Pendiente')
        self.assertEqual(self.banco.saldo_actual, Decimal('50000.00'))

        # 3. Intentar registrar un pago que supera el saldo pendiente (Debe fallar validación de modelo)
        pago_invalido = PagoRecibido(
            cuenta_por_cobrar=cxc,
            cuenta_destino=self.banco,
            monto=Decimal('70000.00'),
            referencia='Excedente'
        )
        with self.assertRaises(ValidationError):
            pago_invalido.save()

        # 4. Intentar registrar un pago con monto negativo o cero (Debe fallar validación)
        pago_negativo = PagoRecibido(
            cuenta_por_cobrar=cxc,
            cuenta_destino=self.banco,
            monto=Decimal('-1000.00'),
            referencia='Negativo'
        )
        with self.assertRaises(ValidationError):
            pago_negativo.save()

        # 5. Registrar el pago restante para saldar la deuda
        pago2 = PagoRecibido.objects.create(
            cuenta_por_cobrar=cxc,
            cuenta_destino=self.banco,
            monto=Decimal('69000.00'),
            referencia='Transferencia Bancaria #002'
        )

        # Recargar de la base de datos
        cxc.refresh_from_db()
        self.banco.refresh_from_db()

        # Verificar que la deuda quede saldada y marcada como 'Pagada'
        self.assertEqual(cxc.saldo_pendiente, Decimal('0.00'))
        self.assertEqual(cxc.estado, 'Pagada')
        self.assertEqual(self.banco.saldo_actual, Decimal('119000.00'))

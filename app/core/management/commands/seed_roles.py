from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Crea los roles de seguridad base (Grupos) y asigna permisos NIIF'

    def handle(self, *args, **kwargs):
        # 1. Crear los Grupos
        grupo_gerencia, _ = Group.objects.get_or_create(name='Gerencia')
        grupo_contabilidad, _ = Group.objects.get_or_create(name='Contabilidad_y_Finanzas')
        grupo_ventas, _ = Group.objects.get_or_create(name='Ventas_y_Planta')

        # 2. Diccionario de permisos a buscar (codenames de Django)
        # Contabilidad: Administra compras, ventas, tesorería, inventario (casi todo menos borrar historial o config)
        perms_contabilidad = [
            'add_facturacompra', 'change_facturacompra', 'view_facturacompra',
            'add_facturaventa', 'change_facturaventa', 'view_facturaventa',
            'add_cuentabancaria', 'change_cuentabancaria', 'view_cuentabancaria',
            'view_cuentaporcobrar', 'view_cuentaporpagar',
            'add_pagorecibido', 'view_pagorecibido',
            'add_pagoemitido', 'view_pagoemitido',
            'add_item', 'change_item', 'view_item',
            'add_tercero', 'change_tercero', 'view_tercero',
            'view_inventariobodega', 'view_movimientoinventario',
            'add_ordenproduccion', 'change_ordenproduccion', 'view_ordenproduccion'
        ]

        # Ventas: Solo ve inventario, crea clientes y crea ventas
        perms_ventas = [
            'add_facturaventa', 'change_facturaventa', 'view_facturaventa',
            'view_item', 'view_inventariobodega',
            'add_tercero', 'change_tercero', 'view_tercero'
        ]

        # 3. Asignar permisos a Contabilidad
        for codename in perms_contabilidad:
            try:
                permiso = Permission.objects.get(codename=codename)
                grupo_contabilidad.permissions.add(permiso)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Permiso no encontrado: {codename}'))

        # 4. Asignar permisos a Ventas
        for codename in perms_ventas:
            try:
                permiso = Permission.objects.get(codename=codename)
                grupo_ventas.permissions.add(permiso)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Permiso no encontrado: {codename}'))

        # Nota: El grupo Gerencia usualmente se maneja haciendo al usuario is_superuser, 
        # pero tener el grupo creado ayuda para filtros a futuro.

        self.stdout.write(self.style.SUCCESS('¡ROLES DE SEGURIDAD Y PERMISOS INYECTADOS CON ÉXITO!'))

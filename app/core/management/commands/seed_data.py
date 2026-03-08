from django.core.management.base import BaseCommand
from core.models import Departamento, Municipio
from inventario.models import UnidadMedida, CategoriaItem

class Command(BaseCommand):
    help = 'Inyecta datos predefinidos de geografía y unidades de medida al ERP'

    def handle(self, *args, **kwargs):
        # 1. Sembrado de Categorías de Inventario
        categorias = [
            'Materia Prima', 'Producto Terminado', 'Retal y Sobrantes', 
            'Insumos Menores', 'Servicios de Maquila', 'Herramientas'
        ]
        for cat in categorias:
            CategoriaItem.objects.get_or_create(nombre=cat)
            self.stdout.write(f'Categoría verificada: {cat}')

        # 2. Sembrado de Unidades de Medida (Metalmecánica y General)
        unidades = [
            ('Kilogramo', 'kg'), ('Tonelada', 't'), ('Gramo', 'g'),
            ('Metro', 'm'), ('Centímetro', 'cm'), ('Milímetro', 'mm'),
            ('Unidad', 'und'), ('Rollo', 'rl'), ('Paquete', 'pq'),
            ('Galón', 'gal'), ('Servicio', 'srv')
        ]
        for nombre, abrev in unidades:
            UnidadMedida.objects.get_or_create(nombre=nombre, abreviatura=abrev)
            self.stdout.write(f'Unidad verificada: {nombre} ({abrev})')

        # 3. Sembrado Geográfico (Departamentos y Municipios clave)
        geo_data = {
            'Caquetá': ['Florencia', 'Morelia', 'El Doncello', 'Puerto Rico', 'San Vicente del Caguán', 'Cartagena del Chairá'],
            'Huila': ['Neiva', 'Pitalito', 'Garzón', 'Gigante', 'La Plata'],
            'Cundinamarca': ['Bogotá D.C.', 'Soacha', 'Chía', 'Zipaquirá'],
            'Antioquia': ['Medellín', 'Bello', 'Itagüí', 'Envigado'],
            'Valle del Cauca': ['Cali', 'Palmira', 'Buenaventura', 'Buga']
        }
        
        # Como los modelos Departamento y Municipio requieren un codigo_dane (unique=True), 
        # le asignaremos un código temporal si es que se están creando por primera vez.
        import random
        for i, (dep_name, muns) in enumerate(geo_data.items(), start=1):
            codigo_dep = f"{i:02d}"
            dep, created = Departamento.objects.get_or_create(
                nombre=dep_name,
                defaults={'codigo_dane': codigo_dep}
            )
            for j, mun_name in enumerate(muns, start=1):
                codigo_mun = f"{codigo_dep}{j:03d}"
                Municipio.objects.get_or_create(
                    nombre=mun_name, 
                    departamento=dep,
                    defaults={'codigo_dane': codigo_mun}
                )
            self.stdout.write(f'Geografía verificada: {dep_name} con {len(muns)} municipios.')

        self.stdout.write(self.style.SUCCESS('¡DATA SEMILLA INYECTADA AL ERP CON ÉXITO!'))

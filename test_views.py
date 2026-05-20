import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def run_tests():
    print("Iniciando pruebas simuladas en el navegador (Django Test Client)...")
    client = Client()
    
    # Crear o recuperar un usuario para pasar el @login_required
    user, created = User.objects.get_or_create(username='test_admin', defaults={'is_superuser': True, 'is_staff': True})
    if created:
        user.set_password('test_password')
        user.save()
        
    client.force_login(user)
    
    urls_to_test = [
        ('Dashboard Core', '/'),
        ('Centro de Reportes', '/reportes/'),
        ('Reporte de Cartera (HTML)', '/reportes/cartera/'),
        ('Exportar Cartera (CSV)', '/reportes/cartera/exportar/'),
        ('Inventario Valorizado (HTML)', '/reportes/inventario/'),
        ('Exportar Inventario (CSV)', '/reportes/inventario/exportar/'),
        ('Flujo de Caja (HTML)', '/reportes/flujo-caja/'),
        ('Exportar Flujo de Caja (CSV)', '/reportes/flujo-caja/exportar/'),
    ]
    
    all_passed = True
    
    for name, url in urls_to_test:
        response = client.get(url)
        print(f"[{name}] GET {url} -> Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"  ERROR: Esperaba 200 pero recibí {response.status_code}")
            all_passed = False
            
        if 'exportar' in url:
            if response.status_code == 200:
                print(f"  Headers: Content-Type={response.get('Content-Type')}, Content-Disposition={response.get('Content-Disposition')}")
                
    if all_passed:
        print("\n¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\nAlgunas pruebas fallaron. Revisa los logs arriba.")

if __name__ == '__main__':
    run_tests()

from django.test import TestCase, Client
from django.contrib.auth.models import User

class ReportesExportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('test_admin', 'admin@example.com', 'testpassword')
        self.client.force_login(self.user)

    def test_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_centro_reportes(self):
        response = self.client.get('/reportes/')
        self.assertEqual(response.status_code, 200)

    def test_reporte_cartera(self):
        response = self.client.get('/reportes/cartera/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Exportar CSV')
        
    def test_exportar_cartera(self):
        response = self.client.get('/reportes/cartera/exportar/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        self.assertIn('attachment; filename="Reporte_Cartera_', response.get('Content-Disposition'))

    def test_inventario_valorizado(self):
        response = self.client.get('/reportes/inventario/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Exportar CSV')

    def test_exportar_inventario(self):
        response = self.client.get('/reportes/inventario/exportar/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        self.assertIn('attachment; filename="Inventario_Valorizado_', response.get('Content-Disposition'))

    def test_flujo_caja(self):
        response = self.client.get('/reportes/flujo-caja/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Exportar CSV')

    def test_exportar_flujo_caja(self):
        response = self.client.get('/reportes/flujo-caja/exportar/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        self.assertIn('attachment; filename="Flujo_Caja_', response.get('Content-Disposition'))

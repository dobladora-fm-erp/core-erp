# Arquitectura y Decisiones Técnicas - Dobladora FM ERP

## 1. Visión Tecnológica
El objetivo de este proyecto no es construir una página web administrativa, sino un **ERP (Enterprise Resource Planning) de grado industrial**. 
Al analizar la naturaleza de la empresa (transformación metalmecánica, fluctuación de costos de materia prima y alto volumen transaccional), se ha descartado el uso de soluciones genéricas o arquitecturas frágiles. Cada tecnología seleccionada responde a una necesidad crítica del negocio, garantizando estabilidad, auditoría y cumplimiento normativo (DIAN/NIIF).

## 2. Stack Tecnológico Definitivo y Justificación

### A. Lenguaje y Framework: Python 3.12 + Django 5 (LTS)
El cerebro del sistema. Django es un framework diseñado para aplicaciones empresariales de alta demanda (utilizado por plataformas como Instagram y Pinterest).
* **El Porqué (Pros):** Su sistema ORM garantiza que la lógica de negocio y las reglas contables se respeten a nivel de código antes de tocar la base de datos. 
* **El Reto (Contras):** Requiere un diseño de arquitectura más estricto desde el inicio.

### B. Motor de Base de Datos: PostgreSQL 16
El estándar de oro en bases de datos relacionales y cumplimiento ACID.
* **El Porqué (Pros):** En un sistema contable, un error de guardado no puede existir. Soporte JSONB vital para DIAN.

### C. Infraestructura de Despliegue: Docker y Contenedores
El ERP no se instala, se despliega en "Contenedores" aislados.
* **El Porqué (Pros):** Entornos de desarrollo idénticos a producción.

## 3. Estado Actual de la Arquitectura (Avances)

El ERP ya cuenta con su **Cimiento Estructural** y **Motor de Operaciones** construidos y validados:

1. **Módulos Core y Terceros:** Parametrización empresarial y catálogo único de clientes/proveedores con blindaje DIAN. Se implementó un comando de inyección de datos semilla (`seed_data`) para autocompletar geografía y catálogos.
2. **Módulo de Inventario (Kardex Inmutable):** Arquitectura avanzada de Bodegas, Ítems y Conversiones. Se implementó un Kardex (*MovimientoInventario*) de **Sólo Lectura**, protegido por Signals nativas y bloqueos administrativos para prevenir manipulación manual de saldos.
3. **Módulo de Compras (Abastecimiento):** Creación de facturación a proveedores conectada en tiempo real al Kardex gracias a transacciones atómicas de Postgres. Implementa autocálculo matemático (Subtotal, IVA 19%, Total) e inmutabilidad tras confirmación.
4. **Módulo de Ventas (Validación NIIF):** Cierre de ciclo. Configurado con lógica anti-negativos; el sistema ejecuta bloqueos (`ValidationError`) en microsegundos si se intenta facturar material sin saldo en bodegas. Descarga automática del Kardex al confirmar.
5. **Módulo de Producción (Transformación):** Órdenes de producción para transformar materia prima en producto terminado o retales, moviendo saldos automáticamente en el Kardex al finalizar bajo el formato entrada/salida unificado.
6. **Módulo de Tesorería (Finanzas):** Cuentas bancarias centralizadas, Cuentas por Cobrar (CxC) integradas directamente con Ventas y Cuentas por Pagar (CxP) conectadas con Compras. Control de flujo de caja y emisión de pagos/recibos auditable.
7. **Autonomía Frontend (UX/UI Operativa):** Desarrollo de interfaces operativas (Bootstrap 5) desacopladas del panel administrativo. Integra tecnología inteligente de búsqueda predictiva (*Select2*) en todas las llaves transaccionales para automatizar y proteger la selección de items, clientes, cuentas y facturas, asegurando velocidad en los puntos de venta o captura.

## 4. Documentación Detallada (Diagramas de Flujo)

Para entender cómo operan y se comunican los módulos a nivel de datos, consulte la carpeta `/docs` en la raíz del proyecto:

- [01. Core y Terceros](docs/01_core_terceros.md)
- [02. Inventario y Kardex](docs/02_inventario_kardex.md)
- [03. Gestión de Compras](docs/03_compras_abastecimiento.md)
- [04. Facturación y Ventas](docs/04_ventas_facturacion.md)
- [05. Producción y Transformación](docs/05_produccion_transformacion.md)
- [06. Tesorería y Finanzas](docs/06_tesoreria_finanzas.md)

## 5. Próxima Fase Estratégica
La siguiente etapa consiste en la preparación para la conexión por API de la Facturación Electrónica DIAN y reportes NIIF avanzados, consolidando así el ecosistema fiscal.

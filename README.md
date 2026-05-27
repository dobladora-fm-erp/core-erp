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
2. **Módulo de Inventario (Kardex Inmutable):** Arquitectura avanzada de Bodegas, Ítems y Conversiones. Se implementó un Kardex (*MovimientoInventario*) protegido por Signals y soporte de "Bienes Intangibles" (servicios) que omiten la afectación de stock.
3. **Módulo de Compras (Abastecimiento):** Creación de facturación conectada al Kardex mediante transacciones atómicas. Implementa inmutabilidad, soporte de compras intangibles sin error de stock, y "Botón de Pánico" transaccional para anular y reversar saldos e historial de CxP.
4. **Módulo de Ventas (Validación NIIF y DIAN):** Configurado con lógica anti-negativos para bloquear ventas sin saldo físico. Su arquitectura ha sido expandida recientemente (Fase 5) para soportar metadata DIAN post-emisión (CUFE, XML, Fechas y Estados).
5. **Módulo de Producción (Transformación):** Órdenes de producción para transformar materia prima. Incorpora tecnología de reversión ("Botón de Pánico") capaz de devolver las materias primas consumidas y desaparecer los productos terminados generados en caso de error.
6. **Módulo de Tesorería (Finanzas):** Cuentas bancarias centralizadas, Cuentas por Cobrar (CxC) integradas directamente con Ventas y Cuentas por Pagar (CxP) conectadas con Compras. Control de flujo de caja y emisión de pagos/recibos auditable.
7. **Autonomía Frontend (UX/UI Operativa):** Desarrollo de interfaces operativas (Bootstrap 5) desacopladas del panel administrativo. Integra tecnología inteligente de búsqueda predictiva (*Select2*) en todas las llaves transaccionales.

## 4. Documentación Detallada (Diagramas de Flujo)

Para entender cómo operan y se comunican los módulos a nivel de datos, consulte la carpeta `/docs` en la raíz del proyecto:

- [01. Core y Terceros](docs/01_core_terceros.md)
- [02. Inventario y Kardex](docs/02_inventario_kardex.md)
- [03. Gestión de Compras](docs/03_compras_abastecimiento.md)
- [04. Facturación y Ventas](docs/04_ventas_facturacion.md)
- [05. Producción y Transformación](docs/05_produccion_transformacion.md)
- [06. Tesorería y Finanzas](docs/06_tesoreria_finanzas.md)

## 5. Próxima Fase Estratégica
Actualmente el núcleo transaccional, contable e inventarial se encuentra **certificado y estabilizado**. La arquitectura de bases de datos ya cuenta con los cimientos (Fase 5) para conectarse con la pasarela oficial de la **Facturación Electrónica DIAN**. El próximo hito será la implementación del cliente API REST para consumo del web service de la entidad tributaria.

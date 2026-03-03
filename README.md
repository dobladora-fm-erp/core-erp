# Arquitectura y Decisiones Técnicas - Dobladora FM ERP

## 1. Visión Tecnológica
El objetivo de este proyecto no es construir una página web administrativa, sino un **ERP (Enterprise Resource Planning) de grado industrial**. 
Al analizar la naturaleza de la empresa (transformación metalmecánica, fluctuación de costos de materia prima y alto volumen transaccional), se ha descartado el uso de soluciones genéricas o arquitecturas frágiles. Cada tecnología seleccionada responde a una necesidad crítica del negocio, garantizando estabilidad, auditoría y cumplimiento normativo (DIAN/NIIF).

## 2. Stack Tecnológico Definitivo y Justificación

### A. Lenguaje y Framework: Python 3.12 + Django 5 (LTS)
El cerebro del sistema. Django es un framework diseñado para aplicaciones empresariales de alta demanda (utilizado por plataformas como Instagram y Pinterest).
* **El Porqué (Pros):** Su sistema ORM (Mapeo Objeto-Relacional) garantiza que la lógica de negocio y las reglas contables se respeten a nivel de código antes de tocar la base de datos. La versión LTS (Long Term Support) asegura parches de seguridad por años, protegiendo la información de la empresa.
* **El Reto (Contras):** Requiere un diseño de arquitectura más estricto desde el inicio comparado con lenguajes más informales, lo cual exige mayor tiempo de planeación en las fases tempranas.

### B. Motor de Base de Datos: PostgreSQL 16
El estándar de oro en bases de datos relacionales y cumplimiento ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad).
* **El Porqué (Pros):** En un sistema contable, un error de guardado no puede existir. Si se factura, el inventario debe bajar y la cuenta por cobrar debe subir simultáneamente. Si hay un micro-corte de energía, PostgreSQL revierte la transacción completa, garantizando que la contabilidad **nunca se descuadre**. Además, su soporte para datos estructurados (JSONB) es vital para almacenar y procesar los archivos XML de la Facturación Electrónica DIAN.
* **El Reto (Contras):** Requiere un entorno de servidores más robusto que bases de datos simples (como MySQL o SQLite).

### C. Infraestructura de Despliegue: Docker y Contenedores
El ERP no se instala de forma tradicional, se despliega en "Contenedores" aislados.
* **El Porqué (Pros):** Elimina el problema de "funciona en mi computadora pero no en el servidor". Docker empaqueta el sistema con sus dependencias exactas. Esto asegura que el entorno de desarrollo sea un clon perfecto del servidor de producción. Facilita las copias de seguridad y permite restaurar todo el sistema en un servidor nuevo en cuestión de minutos ante cualquier catástrofe.

## 3. Estado Actual de la Arquitectura (Avances)

Hasta la fecha, se ha consolidado el **Cimiento Estructural** del sistema:
1. **Contenedores Activos:** Orquestación local finalizada (Base de datos y Servidor Web comunicándose de forma segura).
2. **Módulo Core (Configuración):** Creación de las tablas maestras de parametrización empresarial, incluyendo la carga de catálogos oficiales (Municipios DANE, Códigos CIIU).
3. **Módulo de Terceros (Blindado):** Se diseñó un modelo de datos unificado para Clientes, Proveedores y Empleados. 
   * *Innovación Implementada:* Se adaptó la base de datos para soportar la validación y autocompletado del RUT mediante Proveedores Tecnológicos (API REST), garantizando que el sistema recolecte los datos obligatorios exigidos por la DIAN (Resolución 000042) y alertando al departamento contable si un tercero tiene información faltante que pueda generar bloqueos fiscales.

## 4. Próxima Fase Estratégica
La siguiente etapa de ingeniería comprende el **Motor de Inventario y Transformación**. Se está realizando un levantamiento de requerimientos físicos en planta para mapear correctamente las mermas (retales), las conversiones de unidades (Toneladas a Kilos/Metros) y las políticas de bloqueo estricto contra facturación en negativo para proteger la integridad del Kardex.

# Módulo 06: Tesorería y Finanzas

## Propósito del Módulo
Llevar un rastro exacto del flujo de dinero del ERP. Este módulo centraliza las deudas de clientes (Cuentas por Cobrar), las deudas a proveedores (Cuentas por Pagar) y los movimientos bancarios o de efectivo reales en caja.

## Arquitectura del Módulo

### 1. Cuentas Bancarias
El catálogo centralizado de dinero.
- **Tipos de Cuenta:** Bancos (Bancolombia, Davivienda, etc.) y Efectivo (Caja General, Caja Menor).
- **Saldo Actual:** Propiedad auto-calculada mediante transacciones, estrictamente auditable.

### 2. Cuentas por Cobrar (CxC)
Se disparan automáticamente en estado `Pendiente` cuando Ventas genera una `FacturaVenta`.
- Atada mediante una relación `OneToOneField` a la factura origen, previniendo duplicidades.
- Registra el `monto_total` original, la `fecha_vencimiento` y va descontando el `saldo_pendiente`.
- Cambia a estado `Pagada` únicamente cuando el balance matemático frente a sus abonos llega a cero.

### 3. Cuentas por Pagar (CxP)
Operativa idéntica a la CxC, pero en espejo, recibiendo el empuje contable de Compras vía `FacturaCompra`.
- Control y alertas sobre vencimientos a Proveedores.

### 4. Pagos y Recibos
Son los comprobantes físicos del movimiento de dinero.

* **Pago Recibido:** Cruza una "Cuenta por Cobrar" (la deuda de un cliente) con una "Cuenta Destino" (tu cuenta de ahorros empresarial donde entró el dinero real).
* **Pago Emitido (Egreso):** Cruza una "Cuenta por Pagar" (la deuda a tu proveedor) indicando de qué "Cuenta Origen" (ej. Caja Fuerte) salió la plata.

## Validación NIIF
Este diseño asegura el principio contable de partida doble:
Si una cuenta disminuye, el dinero debe ir justificado hacia un pasivo (pagos a terceros) o un ingreso justificado. Los módulos de compraventa nunca tocan cuentas de bancos directamente; esa responsabilidad ha sido exitosamente separada hacia Tesorería para cumplir con lineamientos de auditoría financiera.

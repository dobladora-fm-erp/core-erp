# Módulo 05: Producción y Transformación

## Propósito del Módulo
Controlar la conversión de materia prima (ej. láminas, rollos de acero) en productos terminados (cortes, perfiles) o subproductos (retales), registrando los costos asociados y enlazando este proceso matemáticamente con el Kardex.

## Flujo Operativo y Modelos
Este módulo se compone de una cabecera centralizada (`OrdenProduccion`) y dos ramas detalladas que interactúan con el inventario.

### 1. Orden de Producción
Es la "receta" y la instrucción de planta. Agrupa bajo un número de orden o lote todo lo que se va a fabricar en un turno o bajo una solicitud.
- Entra en estado `Borrador` donde se planifican los insumos.
- Pasa a estado `Finalizada`, siendo este un momento irreversible que detona los movimientos físicos de las bodegas correspondientes.

### 2. Insumo Consumido (Variables de Entrada)
La materia prima exacta que se retira del inventario.
- Se selecciona el **Ítem** (lámina, pintura, soldadura) y la **Bodega de Origen**.
- Cantidades exactas que entrarán a la maquinaria.

### 3. Producto Generado (Variables de Salida)
El resultado del proceso de transformación.
- Se selecciona el nuevo **Ítem** fabricado (perfil, ángulo, pieza medida).
- Se define el **Costo Unitario Asignado** que se hereda del material consumido más la mano de obra/maquila teórica.
- Se define la **Bodega de Destino** donde ingresa la nueva mercancía terminada.

## Inmutabilidad y Auditoría
Cuando la `OrdenProduccion` se marca como `Finalizada`, el sistema emite automáticamente dos transacciones cruzadas hacia el sistema de inventarios:
1. Una transacción de **SALIDA** por cada `InsumoConsumido`.
2. Una transacción de **ENTRADA** por cada `ProductoGenerado`.

Una vez ejecutada, la orden entra en un bloqueo duro y el campo `procesada` se establece en `True`. Ningún operario puede modificar estas variables posteriormente para garantizar integridad industrial.

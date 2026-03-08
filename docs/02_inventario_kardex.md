# Documentación Técnica: Inventario y Kardex Inmutable

## 1. Descripción
El módulo `inventario` es el motor lógico del ERP. Garantiza que todas las transacciones físicas de materia prima y producto terminado (Entradas, Salidas, Traslados y Ajustes) se registren impecablemente para asegurar un cumplimiento estricto bajo NIIF. 

## 2. Modelos y Filosofía Funcional
* **Item:** El núcleo. Puede ser 'Almacenable', 'Consumible', 'Servicio' o 'Retal'. Obligatoriamente está atado a una Categoría y a una UnidadBase.
* **ConversionUnidad:** Permite transformar métricas de compra (Toneladas de acero a Kilogramos). Su factor dinámico previene la creación de códigos duplicados.
* **Bodega:** Entidad espacial.
* **InventarioBodega:** Relación de cruce (Stock consolidado real). Es manipulado de forma atómica.
* **MovimientoInventario (Kardex):** Tabla **inmutable** en Django Admin (`readonly`). Es la auditoría pura. Nadie puede alterar la historia manualmente.

## 3. Disparadores Automáticos (Signals)
Mediante `signals.py`, interceptamos cada transacción de `MovimientoInventario`. Si se registra:
* Una **Entrada**: Busca la `Bodega` destino y *SUMA* al `InventarioBodega`.
* Una **Salida**: Busca la `Bodega` origen y *RESTA*.
* Un **Traslado**: Dispara ambas operaciones simultáneamente dentro de un bloque `transaction.atomic()` de Postgres. Si hay un micro-error eléctrico o de red, **TODA LA TRANSACCIÓN SE REVIERTE** para evitar descuadres.

## 4. Diagrama del Data Flow: Signals y Kardex

```mermaid
sequenceDiagram
    participant M as Módulo externo (Compras/Ventas)
    participant K as MovimientoInventario
    participant S as Signal (post_save)
    participant B as InventarioBodega
    
    M->>K: Factura confirmada (Inyecta Entrada/Salida)
    activate K
    K-->>S: Notifica creación de registro
    activate S
    S->>S: Abre `transaction.atomic()`
    S->>B: get_or_create (Item + Bodega)
    
    alt Es Entrada
        S->>B: cantidad_actual += cantidad
    else Es Salida
        S->>B: cantidad_actual -= cantidad
    end
    
    B-->>S: Save() OK
    S-->>K: Commit Transaction
    deactivate S
    K-->>M: Historial Sellado en DB
    deactivate K
```

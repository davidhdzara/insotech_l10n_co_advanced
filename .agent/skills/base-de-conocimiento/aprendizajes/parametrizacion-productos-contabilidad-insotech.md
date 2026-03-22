# Parametrización de Productos y Contabilidad – InSoTech

**Fecha de Registro:** 2026-03-18
**Contexto del Problema:**
Documentación del catálogo de productos de InSoTech, su parametrización contable en Odoo V19, y las reglas de negocio para la creación de nuevos productos. Este documento sirve como fuente de verdad para toda decisión contable y de pricing del portafolio InSoTech.

---

## 🏢 Modelo Operativo de InSoTech

InSoTech opera como empresa de servicios tecnológicos B2B con tres líneas de negocio:

| Línea de Negocio | Tipo | Modelo de Facturación | Tercerizado |
|---|---|---|---|
| Servicios de Implementación Odoo | Servicio propio | Precio fijo / Prepago (por horas) | No |
| Servicios de Desarrollo de Software | Servicio propio | Por hojas de horas (timesheet) | No |
| Soporte Técnico de Equipos de Cómputo | Servicio tercerizado | Por unidad de servicio | Sí, vía Partner |

---

## 📦 Catálogo de Productos Actual

### 1. Servicios de Implementación

| Campo | Valor |
|---|---|
| **Nombre** | Servicios de Implementación |
| **Referencia interna** | `SRV-IMP-01` |
| **Tipo de producto** | Servicio |
| **Puede ser vendido** | ✅ Sí |
| **Puede ser comprado** | ❌ No |
| **Puede ser gasto** | ❌ No |
| **Crear en la orden** | Tarea |
| **Proyecto** | Definida en la cotización |
| **Política de facturación** | Precio fijo o de prepago |
| **Precio de venta** | $98.400 COP/hora |
| **Impuestos de venta** | 19% IVA |
| **Precio con IVA** | $117.096 COP/hora |
| **Costo** | $0 (servicio propio) |
| **Categoría** | *(sin categoría asignada)* |
| **Marca** | InSoTech |
| **Código partida arancelaria** | *(vacío)* |

> **Nota de facturación:** Factura cantidades ordenadas en cuanto se venda el servicio. Alerta de sobrecosto al superar el 100% de horas vendidas.

---

### 2. Servicios de Desarrollo de Software

| Campo | Valor |
|---|---|
| **Nombre** | Servicios de Desarrollo de Software |
| **Referencia interna** | `DEV-CUS-HRS` |
| **Tipo de producto** | Servicio |
| **Puede ser vendido** | ✅ Sí |
| **Puede ser comprado** | ❌ No |
| **Puede ser gasto** | ❌ No |
| **Crear en la orden** | Tarea |
| **Proyecto** | Definida en la cotización |
| **Política de facturación** | Según el registro de horas (timesheet) |
| **Precio de venta** | $209.100 COP/hora |
| **Impuestos de venta** | 19% IVA |
| **Precio con IVA** | $248.829 COP/hora |
| **Costo** | $0 (servicio propio) |
| **Categoría** | Desarrollo a Medida |
| **Marca** | InSoTech |
| **Referencia** | `DEV-CUS-HRS` |

> **Nota de facturación:** Factura por hojas de horas (cantidad entregada). Requiere crear tarea en proyecto para seguimiento del tiempo.

---

### 3. Soporte Técnico de Equipos de Cómputo *(NUEVO)*

| Campo | Valor |
|---|---|
| **Nombre** | Soporte Técnico de Equipos de Cómputo |
| **Referencia interna** | `SOP-EQU-01` |
| **Tipo de producto** | Servicio |
| **Puede ser vendido** | ✅ Sí |
| **Puede ser comprado** | ✅ Sí |
| **Puede ser gasto** | ❌ No |
| **Crear en la orden** | Nada (servicio tercerizado, no genera tarea interna) |
| **Política de facturación** | Cantidades ordenadas |
| **Precio de venta** | $69.600 COP/unidad *(sin IVA)* |
| **Impuestos de venta** | 19% IVA |
| **Precio con IVA** | $82.824 COP/unidad |
| **Costo (precio de compra)** | $58.000 COP/unidad *(sin IVA)* |
| **Impuestos de compra** | 19% IVA |
| **Categoría** | Soporte Técnico *(crear si no existe)* |
| **Marca** | InSoTech |
| **Unidad de medida** | Unidades (o "Servicios") |

#### Cálculo del Pricing

```
Costo del partner (sin IVA):       $58.000 COP
Margen deseado:                    20%
Precio de venta (sin IVA):         $58.000 × 1.20 = $69.600 COP
IVA 19%:                           $69.600 × 0.19 = $13.224 COP
Precio final al cliente (con IVA): $69.600 + $13.224 = $82.824 COP
Margen bruto por servicio:         $69.600 - $58.000 = $11.600 COP
```

---

## 📐 Convenciones de Nomenclatura de Productos

Basándose en los productos existentes, la convención de referencia interna sigue este patrón:

| Prefijo | Significado | Ejemplo |
|---|---|---|
| `SRV-` | Servicio propio | `SRV-IMP-01` |
| `DEV-` | Desarrollo | `DEV-CUS-HRS` |
| `SOP-` | Soporte técnico | `SOP-EQU-01` |

---

## 💡 Buenas Prácticas / Reglas para Nuevos Productos

1. **Servicios propios** (implementación, desarrollo): Solo marcar "Ventas". Costo = $0 porque el recurso es interno.
2. **Servicios tercerizados** (soporte equipos): Marcar "Ventas" **Y** "Compras". El costo refleja el precio del partner.
3. **IVA**: Todos los servicios de InSoTech llevan **19% IVA** tanto en venta como en compra.
4. **Marca**: Siempre asignar **InSoTech** como marca, independientemente de si el servicio es propio o tercerizado.
5. **Categorías de producto**: Crear categorías con cuentas contables de ingreso y gasto preconfiguradas para que cada producto herede su contabilidad automáticamente.
6. **Margen mínimo**: Para servicios tercerizados, mantener un **mínimo de 20%** de margen sobre el costo del partner.

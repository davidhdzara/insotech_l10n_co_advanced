# Insotech — Localización Colombiana Avanzada

## Descripción

Módulo para Odoo 19 Enterprise que extiende la localización nativa colombiana (`l10n_co_dian`) para proteger los consecutivos de resolución DIAN contra rechazos técnicos y errores de datos.

- **Nombre técnico**: `insotech_l10n_co_advanced`
- **Versión**: 19.0.1.0.0
- **Licencia**: OPL-1
- **Dependencias**: `account`, `l10n_co_edi`, `l10n_co_dian`, `insotech_core`

---

## Problema que Resuelve

Cuando Odoo confirma una factura, asigna inmediatamente el siguiente consecutivo de la resolución DIAN (ej. `FE-845`). Si la DIAN rechaza el XML, ese número **se pierde**, creando huecos en la numeración legal.

Este módulo implementa un **patrón de secuencia temporal**: asigna un nombre temporal `PRE-INV/YYYY/NNNNN` al confirmar, y solo muta al número legal definitivo cuando la DIAN acepta.

---

## Flujo de Secuencias

```
           Borrador
              │
              ▼
    Confirmar (_post)
              │
              ▼
    ┌─────────────────────┐
    │ PRE-INV/2026/00001  │  ← Nombre temporal, contabilidad OK
    └──────────┬──────────┘
               │
      Enviar a DIAN (Print & Send)
               │
        ┌──────┴──────┐
        │             │
   Aceptada      Rechazada
        │             │
        ▼             ▼
  ┌──────────┐  ┌──────────────────┐
  │ FE-845   │  │ PRE-INV/2026/... │
  │ ✅ Legal │  │ ❌ Corregir      │
  └──────────┘  │    y reintentar  │
                └──────────────────┘
```

---

## Campos Añadidos a `account.move`

| Campo | Tipo | Descripción |
|---|---|---|
| `insotech_dian_status` | Selection | `not_applicable`, `pending`, `accepted`, `rejected` |
| `insotech_pre_inv_name` | Char | Nombre temporal PRE-INV asignado |
| `insotech_is_co_edi` | Boolean (computed) | Si la factura es EDI colombiana |

---

## Validación de Licencia SaaS

Antes de enviar el XML a la DIAN, valida la licencia usando `insotech_core._validate_and_report_license()`. Si la licencia no es válida, bloquea el envío (no la confirmación).

---

## Elementos de Vista

- **Banner amarillo**: "Pendiente de validación DIAN" (facturas con PRE-INV)
- **Banner rojo**: "Rechazada por DIAN" (con instrucciones de corrección)
- **Botón "Reintentar Envío DIAN"**: visible solo en facturas rechazadas
- **Botón "Forzar Aceptación DIAN"**: solo administradores contables
- **Badge de estado**: en la pestaña "Otra Información"

# Contingencia DIAN Tipo 04 en Odoo 19: Protocolo Normativo + Implementación Técnica

> **Autor:** David Hernández Ara — InSoTech
> **Fecha:** 2026-03-24
> **Tags:** Odoo 19, DIAN, Contingencia, Facturación Electrónica, Colombia, l10n_co_dian
> **Rating:** ⭐⭐⭐⭐⭐

---

## ¿Qué es la Contingencia Tipo 04?

Cuando el servicio de validación de la DIAN (Dirección de Impuestos y Aduanas Nacionales de Colombia) no está disponible, las empresas no pueden detenerse. La **Contingencia Tipo 04** es el protocolo que permite seguir facturando cuando la DIAN no responde.

### Marco Normativo

La Resolución 000165 de 2023 de la DIAN establece 4 tipos de contingencia:

| Tipo | Causa | Quién lo activa | ¿Requiere resolución previa? |
|------|-------|-----------------|------------------------------|
| 01 | Problemas tecnológicos del emisor | Empresa | Sí |
| 02 | Problemas con el proveedor tecnológico | Empresa | Sí |
| **03** | **Caída del proveedor tecnológico** | **Automático** | **Sí (talonario)** |
| **04** | **Caída del servicio DIAN** | **Automático** | **No** |

El Tipo 04 es el más relevante para automatización porque:
- **No requiere resolución previa** (a diferencia del Tipo 03)
- La factura ya tiene CUFE y firma digital — **es válida**
- Solo falta la validación de DIAN
- Se puede entregar al cliente con una nota de contingencia
- Plazo para retransmitir: **48 horas**

### Protocolo de Detección (DIAN)

```
Intento 1 (Odoo nativo) → falla
    ↓ esperar 20 segundos
Intento 2 → falla
    ↓ esperar 20 segundos
Intento 3 → falla
    ↓ esperar 20 segundos
Intento 4 → falla
    ↓
CONTINGENCIA TIPO 04 ACTIVADA
```

**4 intentos × 20 segundos** antes de declarar contingencia.

---

## ¿Por qué Odoo nativo no lo maneja?

Verificamos el modelo `l10n_co_dian.document` (Odoo 19 Enterprise) directamente en un servidor de staging usando `odoo-bin shell`:

```python
# Campos nativos del modelo
Model = env['l10n_co_dian.document']
for name, field in sorted(Model._fields.items()):
    print(name, field.type)
```

**Hallazgos:**
- El campo `state` tiene `'invoice_sending_failed'` para fallos de envío ✅
- **No tiene** lógica de retry automático ❌
- **No tiene** campos de contingencia ❌
- **No tiene** retransmisión post-contingencia ❌
- `l10n_co_edi_operation_type` **no incluye** códigos de contingencia (03/04) ❌

También verificamos el código fuente del método de envío:

```python
import inspect
print(inspect.getsource(Model._send_to_dian))
print(inspect.getsource(Model._send_bill_sync))
```

**Descubrimiento crítico:** `_send_bill_sync` es **stateless** — se puede re-invocar sin efectos secundarios ni duplicación de CUFEs. Además, tiene detección de "documento ya procesado" (`_document_already_processed`), lo que lo hace idempotente.

---

## Nuestra Implementación: Retry Híbrido

### El problema del bloqueo

4 intentos × 20 segundos = **80 segundos bloqueando al usuario**. Inaceptable.

### La solución: Retry asíncrono vía CRON

| Componente | Función |
|-----------|---------|
| Odoo nativo | Intento #1 (síncrono, al confirmar factura) |
| CRON retry (cada 5 min) | Intentos #2-4 con `sleep(20)` entre cada uno |
| CRON recovery (cada 30 min) | Retransmisión cuando DIAN se recupera |

**El usuario nunca es bloqueado.** El CRON absorbe los 60 segundos de espera restantes.

### Extensión del modelo nativo

```python
class L10nCoDianDocument(models.Model):
    _inherit = 'l10n_co_dian.document'

    insotech_contingency_mode = fields.Boolean(default=False)
    insotech_contingency_evidence = fields.Text()       # JSON con intentos
    insotech_contingency_activated_at = fields.Datetime()
    insotech_contingency_resolved_at = fields.Datetime()
    insotech_retry_count = fields.Integer(default=0)
```

### Extensión del operation_type

```python
# En account.move — CLAVE: usar selection_add
l10n_co_edi_operation_type = fields.Selection(
    selection_add=[
        ('03', 'Contingencia Proveedor Tecnológico'),
        ('04', 'Contingencia DIAN'),
    ],
)
```

> **Aprendizaje:** `selection_add` agrega valores al final del Selection nativo sin tocar los existentes. Es el ÚNICO patrón seguro para extender Selections Enterprise.

---

## Lecciones Aprendidas (Técnicas)

### 1. CRON `model_id`: `search=` vs `ref=`

Al referenciar modelos Enterprise en XML de CRONs:
```xml
<!-- ❌ El XML ID puede no existir -->
<field name="model_id" ref="l10n_co_dian.model_l10n_co_dian_document"/>

<!-- ✅ Busca por nombre técnico — siempre funciona -->
<field name="model_id" search="[('model', '=', 'l10n_co_dian.document')]"/>
```

### 2. Campos de ir.cron en V19

En Odoo 19, estos campos fueron **eliminados**:
- `numbercall` ❌
- `state` ❌
- `priority` ❌

Solo usar: `name`, `model_id`, `code`, `interval_number`, `interval_type`, `active`.

### 3. Inspeccionar antes de extender

Antes de tocar un modelo Enterprise, **siempre usar `odoo-bin shell`** para verificar campos y métodos reales. Nunca asumir.

---

## Lecciones Aprendidas (Normativas)

### 1. Los códigos de Odoo ≠ códigos DIAN

Odoo define `commercial_state` con `'accepted_by_issuer'` = `'034'`. Pero según la Resolución 000165/2023:
- **034 = Reclamo de la Factura Electrónica** (NO "accepted by issuer")
- **035 = Aceptación Tácita** (NO existe en el modelo nativo)

### 2. El reloj de aceptación tácita empieza en el 032, no en el 030

| Evento | Código | ¿Inicia el reloj? |
|--------|--------|--------------------|
| Acuse de Recibo | 030 | ❌ |
| Rechazo | 031 | ❌ |
| **Recibo del Bien/Servicio** | **032** | **✅ Inicia los 3 días** |
| Aceptación Expresa | 033 | ❌ (resuelve) |
| Reclamo | 034 | ❌ (resuelve) |
| Aceptación Tácita | 035 | ❌ (automática tras 3 días) |

### 3. El plazo de retransmisión post-contingencia es de 48 horas

No es configurable por la empresa — es un mandato DIAN. Nuestro sistema alerta cuando se acerca el deadline y envía una alerta crítica cuando se excede.

### 4. La factura SÍ se puede entregar al cliente durante contingencia

Protocolo DIAN Tipo 04: la factura es válida (tiene CUFE + firma). Solo falta la validación. El negocio no se detiene.

### 5. Contingencia Tipo 03 requiere resolución de talonario previa

No se puede automatizar sin que el cliente tenga autorización previa de la DIAN para emitir facturas en papel/talonario.

---

## Resultado

| Métrica | Valor |
|---------|-------|
| Archivos nuevos | 2 (modelo + CRONs) |
| Archivos modificados | 5 |
| Pruebas pasadas en staging | 6/6 |
| Tiempo de bloqueo al usuario | **0 segundos** |
| Compliance DIAN | ✅ 4 intentos × 20s |
| Multi-tenant | ✅ Configurable por empresa |

---

## ¿Quieres implementar esto en tu proyecto Odoo?

Este módulo forma parte de **InSoTech — Localización Colombiana Avanzada**, disponible para Odoo 19. Contáctanos para una demostración.

🌐 [www.insotech.it](https://www.insotech.it)

# Plan de Implementación — RADIAN InSoTech

> **Proyecto:** InSoTech Localización Colombiana Avanzada
> **Fase:** 7 — Eventos RADIAN
> **Fecha:** 2026-03-24
> **Estimación total:** 80-115 horas (4 fases)

---

## Fase 7.1 — Investigación ✅ COMPLETADA

Documentación exhaustiva de eventos RADIAN, normativa DIAN, análisis de competencia y gaps identificados.

**Entregables:** `INVESTIGACION_RADIAN.md`, `GAPS_RADIAN_ODOO19.md`, este documento.

---

## Sprint 0 — Infraestructura Base ✅ COMPLETADO (2026-03-24)

> **Commits:** `cc5234a` (dev), `1093dbd` (staging)
> **Módulo afectado:** `insotech_dian_wizard`

### QW2: Alerta de Vencimiento de Certificado Digital
**Archivos:**
- `models/res_company.py` — 3 campos computados + método CRON
- `data/cron_certificate_expiry.xml` — CRON diario V19

**Cómo funciona:**
1. Campo `insotech_dian_cert_expiry_date` (Date, stored, computed) parsea el `.p12` con `cryptography.hazmat.primitives.serialization.pkcs12`
2. Campo `insotech_dian_cert_days_remaining` (Integer, computed) calcula `(expiry - today).days`
3. CRON diario `_cron_check_certificate_expiry()` busca empresas con certificado y alerta en 3 niveles:
   - 🟢 ≤90 días → aviso
   - 🟡 ≤30 días → advertencia
   - 🔴 ≤7 días → urgente
4. Publica en el **chatter de `res.company`** vía `message_post()`

**Compatibilidad:** Usa `getattr(cert, 'not_valid_after_utc', cert.not_valid_after)` para soportar `cryptography < 42.0`.

### QW3: Selector Vocación de Circulación
**Archivos:**
- `models/res_company.py` — campo `insotech_radian_mode` (Selection)
- `models/res_config_settings.py` — campo related para UI
- `views/res_config_settings_views.xml` — bloques UI en Ajustes → InSoTech

**Opciones:** `disabled` | `manual` (default) | `all_credit`

**UI visible en:** Ajustes → InSoTech → Configuración RADIAN

---

## Sprint 1 — Aceptación Tácita + Bloqueo NC/ND ✅ COMPLETADO (2026-03-24)

> **Commits:** `729be07` (dev), `44a0e4c` (staging)
> **Módulo afectado:** `insotech_l10n_co_advanced` (v19.0.1.4.0)

### Componente 1: Calculadora de Días Hábiles Colombianos
**Archivo:** `services/colombian_calendar.py`

Módulo Python puro (sin dependencia de Odoo). Implementa:

```python
get_colombian_holidays(year)  # → set[date] (18 festivos)
is_business_day(dt, extra_holidays=None)  # → bool
add_business_days(start, n, extra_holidays=None)  # → date
```

**Algoritmo de festivos:**
- **6 fijos:** 1 ene, 1 may, 20 jul, 7 ago, 8 dic, 25 dic
- **7 Ley Emiliani** (se mueven al lunes): Reyes, San José, San Pedro, Asunción, Raza, Santos, Cartagena
- **5 dependientes de Pascua:** Jueves/Viernes Santo, Ascensión, Corpus Christi, Sagrado Corazón
- Pascua calculada con **algoritmo anónimo gregoriano** (Gauss)
- **Cero mantenimiento** — funciona para cualquier año pasado o futuro

**Base legal:** Art. 62, Ley 4 de 1913 (días hábiles); Ley 51 de 1983 (festivos colombianos)

### Componente 2: Modelo `insotech.radian.event`
**Archivo:** `models/radian_event.py`

Modelo propio (NO modifica `account.move`). Hereda `mail.thread`.

| Campo | Tipo | Uso |
|-------|------|-----|
| `move_id` | Many2one → account.move | Factura referenciada |
| `event_code` | Selection | 030/031/032/033/034 |
| `state` | Selection | draft/done/sent/accepted/error |
| `source` | Selection | manual/cron/portal |
| `claim_code` | Selection | Solo para 031 (códigos 01-04) |
| `xml_content` | Text | XML generado (dry run) |
| `notes` | Text | Motivo/detalle del evento |

**CRON `_cron_tacit_acceptance()`** (diario):
1. Busca eventos 030 en estado done/sent/accepted
2. Para cada uno, verifica que NO exista 033/034/031 en la misma factura
3. Calcula `add_business_days(fecha_030, 3)` usando festivos + custom holidays
4. Si `hoy > deadline` → crea evento 034 (dry run) + post en chatter

### Componente 3: Modelo `insotech.custom.holiday`
**Archivo:** `models/insotech_custom_holiday.py`

Modelo simple: `name` (Char) + `date` (Date) + `company_id` (Many2one).
El CRON consulta estos festivos y los une con `set | set` al resultado del algoritmo → duplicados se ignoran automáticamente.

### Componente 4: Bloqueo NC/ND por Irrevocabilidad
**Archivo:** `models/account_move.py` — método `_insotech_check_radian_irrevocability()`

Se ejecuta **antes** de `super()._post()` en el override existente. Lógica:
1. Solo aplica a `move_type == 'out_refund'`
2. Busca la factura original vía `reversed_entry_id`
3. Consulta si existe `insotech.radian.event` con código 033/034 y estado ≠ error
4. Si existe:
   - **Sin grupo override** → `raise UserError` con mensaje explicativo
   - **Con grupo override** → permite pero SIEMPRE publica alerta en chatter

### Componente 5: Grupo de Seguridad
**Archivo:** `security/security.xml`

Grupo `insotech_l10n_co_advanced.group_radian_override`:
- Nombre: "RADIAN: Permitir NC/ND sobre facturas aceptadas"
- Sin `privilege_id` (grupo interno, no visible en categorías)
- Se asigna manualmente a contadores/gerentes autorizados

### Permisos (ACL)
**Archivo:** `security/ir.model.access.csv`

| Modelo | Invoicers | Managers |
|--------|-----------|----------|
| `insotech.radian.event` | read/write/create | full (+ unlink) |
| `insotech.custom.holiday` | read-only | full |

---

## Fase 7.2 — Portal Receptor para Personas Naturales (DIFERENCIADOR #1)

> **Prioridad:** 🔴 Alta — Inversión: 40-60 horas
> **Regla:** NO crear campos en modelos nativos. NO modificar UI nativa de Odoo.

### Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────┐
│  Emisor (InSoTech / Cliente Odoo)                       │
│                                                         │
│  Emite FE → DIAN acepta → Envía correo al receptor     │
│                         con link:                       │
│  https://empresa.odoo.com/radian/view/<token>           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Portal Público RADIAN (Controller HTTP)                │
│                                                         │
│  GET /radian/view/<token>                               │
│  → Página web con datos de la FE (sin login)            │
│  → Botones: Acusar Recibo | Aceptar | Rechazar | Reclamar│
│                                                         │
│  POST /radian/action/<token>                            │
│  → Genera ApplicationResponse XML                       │
│  → Firma con certificado del emisor                     │
│  → Envía a DIAN vía SOAP                                │
│  → Registra en account.move (chatter)                   │
└─────────────────────────────────────────────────────────┘
```

### Nuevo Módulo: `insotech_radian`

```
insotech_radian/
├── __manifest__.py          # Dependencias: insotech_l10n_co_advanced
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── radian_token.py      # Modelo propio: token UUID, factura ref, estado
│   └── radian_event.py      # Modelo propio: registro de eventos enviados
├── controllers/
│   ├── __init__.py
│   └── radian_portal.py     # Routes: /radian/view, /radian/action
├── services/
│   ├── xml_builder.py       # Genera ApplicationResponse XML (UBL 2.1)
│   ├── xml_signer.py        # Firma XAdES-EPES
│   └── soap_client.py       # Envía a DIAN
├── views/
│   └── radian_portal_templates.xml  # Templates QWeb para la página pública
├── data/
│   ├── mail_template.xml    # Template de correo con link de acción
│   └── cron_tacit_acceptance.xml  # CRON: detectar aceptación tácita
├── security/
│   └── ir.model.access.csv
└── static/
    └── src/
        ├── css/               # Estilos del portal público
        └── js/                # Timeline widget OWL (Fase 7.5)
```

### Modelos Propios (NO toca modelos nativos)

#### `insotech.radian.token`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | Char | Token UUID4 único |
| `move_id` | Many2one → account.move | Factura referenciada |
| `partner_id` | Many2one → res.partner | Receptor |
| `state` | Selection | pending / acknowledged / accepted / rejected / claimed |
| `cufe` | Char | CUFE de la factura |
| `expiry_date` | Datetime | Fecha de expiración del token |
| `created_by` | Many2one → res.users | Usuario que generó el token |

#### `insotech.radian.event`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | Char | Consecutivo del evento |
| `move_id` | Many2one → account.move | Factura |
| `token_id` | Many2one → insotech.radian.token | Token usado |
| `event_code` | Selection | 030/031/032/033/034/035 |
| `cude` | Char | CUDE del ApplicationResponse |
| `xml_sent` | Binary | XML enviado |
| `xml_response` | Binary | Respuesta DIAN |
| `dian_status` | Selection | pending / accepted / rejected |
| `sent_date` | Datetime | Fecha de envío |
| `source` | Selection | portal / email / internal | De dónde se generó |

### Seguridad del Token
- UUID4 (128-bit, criptográficamente seguro)
- Expiración: 30 días desde emisión (configurable)
- Rate limiting: máximo 5 acciones por token por hora
- Validación IP: registrar IP de cada acción
- HTTPS obligatorio

### Dependencia: Reutilizar código existente
- **Firma XAdES-EPES:** Reutilizar de `insotech_dian_wizard/services/`
- **Cliente SOAP:** Adaptar de `insotech_dian_wizard/services/soap_client.py`
- **Modelo de licencia:** Validar contra `insotech_core`

---

## Fase 7.3 — Acciones desde Correo Electrónico (DIFERENCIADOR #2)

> **Prioridad:** 🔴 Alta — Inversión: 15-20 horas (sobre el portal base)

### Diseño

- Template de correo con botones de acción directa
- Cada botón es un link GET a `/radian/action/<token>?event=030`
- La página intermediaria confirma la acción antes de ejecutar
- Soporte para correos con estilos inline (compatibilidad Gmail, Outlook)

### Flujo

```
1. Emisor confirma factura → Odoo envía correo al receptor
2. Correo incluye:
   - PDF de la factura adjunta
   - Resumen de la factura (monto, concepto, fecha)
   - Botones de acción:
     [✅ Acusar Recibo]  [📦 Confirmar Recepción]  [❌ Rechazar]
3. Receptor hace clic → se abre /radian/action/<token>?event=030
4. Página de confirmación (sin login) → clic en "Confirmar"
5. InSoTech genera XML → firma → envía a DIAN → registra
```

---

## Fase 7.4 — CRON Aceptación Tácita Automática

> **Prioridad:** 🔴 Alta — Inversión: 5 horas

### Lógica del CRON

```python
# Ejecutar diariamente
# REGLA 2026: plazo empieza desde RECEPCIÓN de la FE (evento 030),
# NO desde recibo del bien (032).
# Buscar facturas con:
#   - Evento 030 (Acuse de recibo) registrado
#   - Fecha del 030 + 3 días hábiles < hoy
#   - Sin evento 033 (aceptación expresa)
#   - Sin evento 031 (rechazo)
#   - Sin evento 034 (reclamo)
# Para cada una:
#   - Generar evento 035 (Aceptación tácita)
#   - Enviar a DIAN
#   - Notificar al emisor
#   - Marcar factura como irrevocable (bloquear NC/ND)
```

---

## Fase 7.5 — Timeline Visual de Eventos (DIFERENCIADOR #3)

> **Prioridad:** 🟢 Alta — Inversión: 15-20 horas

### Diseño UX

Widget OWL que se renderiza en el chatter o en una pestaña nueva de la factura, mostrando:

```
 ┌─────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │   FE    │────▶│  030 Acuse   │────▶│  032 Recibo  │────▶│ 033 Aceptada │
 │ Emitida │     │  12/03/2026  │     │  13/03/2026  │     │  14/03/2026  │
 │   ✅    │     │     ✅       │     │     ✅       │     │     ✅       │
 └─────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

Con estados dinámicos:
- 🟢 Verde = Completado
- 🟡 Amarillo = Pendiente (esperando acción)
- 🔴 Rojo = Rechazado/Reclamado
- ⏳ Gris = Futuro (no aplica aún)
- 🔒 Candado = Irrevocable (tras aceptación)

---

## Fase 7.6 — Cumplimiento Normativo Anexo 1.9

> **Prioridad:** 🔴 Crítica — Inversión: 15-20 horas
> **Fuente:** Informe técnico PO + Resolución 000008/2024

### Items de Cumplimiento

| ID | Item | Esfuerzo | Módulo | Estado |
|---|---|---|---|---|
| 7.6a | Verificar/migrar a SHA-384 para CUFE/CUDE | 2-3h | `insotech_dian_wizard` | ✅ Confirmado (ya en producción) |
| 7.6b | Bloqueo NC/ND tras aceptación título valor (irrevocabilidad) | 3-5h | `insotech_radian` | ⏳ Sprint 1 |
| 7.6c | Selector "vocación de circulación" en FE | 3-5h | `insotech_dian_wizard` | ✅ Sprint 0 completado |
| 7.6d | Contingencia Tipo 4: Código de Operación 04 en XML | 5-8h | `insotech_l10n_co_advanced` | ⏳ Sprint 2 |
| 7.6e | Alerta proactiva vencimiento certificado digital (90 días) | 3-5h | `insotech_dian_wizard` | ✅ Sprint 0 completado |

---

## Cronograma Propuesto

| Fase | Descripción | Horas | Sprint | Estado |
|------|-------------|-------|--------|--------|
| 7.1 | Investigación | — | Sprint 0 | ✅ Completado |
| 7.6a | SHA-384 CUFE/CUDE | — | Sprint 0 | ✅ Ya en producción |
| 7.6c | Selector vocación de circulación | — | Sprint 0 | ✅ Completado 2026-03-24 |
| 7.6e | Alerta vencimiento certificado | — | Sprint 0 | ✅ Completado 2026-03-24 |
| 7.4 | CRON aceptación tácita | 5h | Sprint 1 | ⏳ Siguiente |
| 7.6b | Bloqueo NC/ND irrevocabilidad | 3-5h | Sprint 1 | ⏳ |
| 7.6d | Contingencia Tipo 4 (Código 04) | 5-8h | Sprint 2 | ⏳ |
| 7.2 | Portal receptor personas naturales | 40-60h | Sprint 2-3 | ⏳ |
| 7.3 | Acciones desde correo | 15-20h | Sprint 3 | ⏳ Depende de 7.2 |
| 7.5 | Timeline visual OWL | 15-20h | Sprint 4 | ⏳ Depende de 7.2 |

**Completado: Sprint 0 (3 items) · Restante: 85-120 horas → ~4-6 semanas**

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Cambios en API DIAN | Alto | Abstraer endpoints en config, documentar WSDL |
| Firma XAdES falla para eventos | Alto | Reutilizar código probado del wizard |
| Token de portal comprometido | Medio | UUID4 + expiración + rate limiting + HTTPS |
| Receptor no recibe correo | Medio | Fallback: portal DIAN directo |
| Odoo actualiza l10n_co_dian | Medio | Módulo independiente, no toca nativos |
| SHA-384 no implementado en producción | ~~🔴 Alto~~ | ✅ MITIGADO — Confirmado en producción |
| Certificado vence sin alerta | ~~Medio~~ | ✅ MITIGADO — CRON + 3 niveles de alerta implementado |
| NC/ND emitida contra FE aceptada (irrevocabilidad) | Alto | Bloqueo programático en `_post()` (7.6b) |

---

## Métricas de Éxito

| Métrica | Objetivo |
|---------|----------|
| Eventos 030-034 generados desde portal | >0 en primer mes |
| Aceptaciones tácitas automáticas | >0 en primer mes |
| Tiempo de adopción por receptor | <5 minutos sin capacitación |
| Receptores sin Odoo que interactúan | >1 en primer trimestre |
| Cumplimiento Anexo 1.9 | 100% |
| Alertas certificado emitidas antes de vencimiento | ≥1 |


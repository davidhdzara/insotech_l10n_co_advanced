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

| ID | Item | Esfuerzo | Módulo |
|---|---|---|---|
| 7.6a | Verificar/migrar a SHA-384 para CUFE/CUDE | 2-3h | `insotech_dian_wizard` |
| 7.6b | Bloqueo NC/ND tras aceptación título valor (irrevocabilidad) | 3-5h | `insotech_radian` |
| 7.6c | Selector "vocación de circulación" en FE (acción explícita del emisor) | 3-5h | `insotech_radian` |
| 7.6d | Contingencia Tipo 4: Código de Operación 04 en XML | 5-8h | `insotech_l10n_co_advanced` |
| 7.6e | Alerta proactiva vencimiento certificado digital (90 días) | 3-5h | `insotech_core` |

---

## Cronograma Propuesto

| Fase | Descripción | Horas | Sprint | Dependencia |
|------|-------------|-------|--------|-------------|
| 7.1 | Investigación | ✅ | ✅ Completado | — |
| 7.6a | SHA-384 CUFE/CUDE | 2-3h | Sprint 0 (URGENTE) | — |
| 7.4 | CRON aceptación tácita | 5h | Sprint 1 (Q2 W1) | — |
| 7.6b-e | Cumplimiento normativo | 15-20h | Sprint 1-2 (Q2 W1-2) | — |
| 7.2 | Portal receptor personas naturales | 40-60h | Sprint 2-3 (Q2 W2-5) | — |
| 7.3 | Acciones desde correo | 15-20h | Sprint 3 (Q2 W4-5) | 7.2 |
| 7.5 | Timeline visual OWL | 15-20h | Sprint 4 (Q2 W6-7) | 7.2 |

**Total: 95-140 horas → ~5-7 semanas de desarrollo**

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Cambios en API DIAN | Alto | Abstraer endpoints en config, documentar WSDL |
| Firma XAdES falla para eventos | Alto | Reutilizar código probado del wizard |
| Token de portal comprometido | Medio | UUID4 + expiración + rate limiting + HTTPS |
| Receptor no recibe correo | Medio | Fallback: portal DIAN directo |
| Odoo actualiza l10n_co_dian | Medio | Módulo independiente, no toca nativos |
| SHA-384 no implementado en producción | 🔴 Alto | Verificar INMEDIATAMENTE en `insotech_dian_wizard` |
| Certificado vence sin alerta | Medio | Implementar alerta 90 días (7.6e) |
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


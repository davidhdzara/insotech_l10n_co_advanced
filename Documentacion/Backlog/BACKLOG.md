# Product Backlog — InSoTech Localización Colombiana

> **Producto:** Suite de Facturación Electrónica DIAN para Odoo 19/18
> **Product Owner:** David Hernández Ara
> **Última actualización:** 2026-03-23

---

## 🟢 Completado

### FASE 0 — Planeación Estratégica
| ID | Item | Estado |
|---|---|---|
| 0.1 | Definición de arquitectura modular (core + advanced + wizard) | ✅ |
| 0.2 | Revisión de viabilidad SaaS y contingencia de red | ✅ |
| 0.3 | Trazabilidad normativa DIAN 2026 (Anexo 1.9) | ✅ |

### FASE 1 — Motor SaaS (`insotech_core`)
| ID | Item | Estado |
|---|---|---|
| 1.1 | Base estructural del módulo | ✅ |
| 1.2 | Modelo de configuración y caching de pings | ✅ |
| 1.3 | Cliente API RPC anti-fallas (grace period 72h) | ✅ |
| 1.4 | Documentación técnica | ✅ |
| 1.5 | README raíz corregido | ✅ |
| 1.6 | `security/ir.model.access.csv` agregado | ✅ |

### FASE 2 — Facturación Segura DIAN (`insotech_l10n_co_advanced`)
| ID | Item | Estado |
|---|---|---|
| 2.1 | Investigación Odoo 19 nativo: campos verificados en staging | ✅ |
| 2.2 | Estructura del módulo: manifest, init, security, data | ✅ |
| 2.3 | Secuencia provisional PRE-INV: override `_post()` + `_get_last_sequence_domain()` | ✅ |
| 2.4 | Mutación PRE-INV → FE: restaura `insotech_reserved_dian_name` | ✅ |
| 2.5 | Bloqueo por licencia: 3 hooks de validación | ✅ |
| 2.6 | Vistas XML: banners + botones (retry / force-accept / verify CUFE) | ✅ |
| 2.7 | Documentación técnica | ✅ |
| 2.8 | Hook automático `account.edi.document` (detecta aceptación/rechazo) | ✅ |
| 2.9 | Botón "Forzar Aceptación DIAN" (admin only) | ✅ |
| 2.10 | Contador visual de resolución DIAN | ✅ |
| 2.11 | Validación formato secuencia DIAN (FAD05a) | ✅ |
| 2.12 | Fix NIT en GetNumberingRange (sanitización DV) | ✅ |
| 2.13 | Mensajes amigables error 302/401 DIAN | ✅ |

### FASE 3 — Servidor API SaaS (`insotech_saas_server`)
| ID | Item | Estado |
|---|---|---|
| 3.1 | Modo Dev: bypass para pruebas sin API | ✅ |
| 3.2 | Modelo `insotech.license`: token UUID4, plan, estado, consumo | ✅ |
| 3.2b | Modelo `insotech.license.log`: auditoría + `is_suspicious` | ✅ |
| 3.4 | Controller `/verify`: JSON plano, SQL atómico, IP Cloudflare | ✅ |
| 3.4b | Endpoint `/health`: GET → `{"status": "ok"}` | ✅ |
| 3.5 | Lógica pay-per-use: re-check post-incremento, auto-exhaust | ✅ |
| 3.6 | Datos demo: 3 licencias (internal, partner, payperuse) | ✅ |
| 3.7 | CRONs: 3 (vencimientos, reset mensual, purge semanal) | ✅ |

### FASE 3.5 — Habilitación DIAN (`insotech_dian_wizard`)
| ID | Item | Estado |
|---|---|---|
| 3.5.1 | Wizard + credenciales DIAN (Software ID, PIN, Test Set, .p12) | ✅ |
| 3.5.2 | Motor UBL 2.1: genera FE, NC, ND con datos emulados | ✅ |
| 3.5.3 | Firma XAdES-EPES: RSA-SHA256 con política DIAN v2 | ✅ |
| 3.5.4 | Cliente SOAP: SendBillSync + SendTestSetAsync + GetStatusZip | ✅ |
| 3.5.5 | Desacoplamiento: habilitación independiente de datos reales | ✅ |
| 3.5.6 | Documentación: 2 docs técnicos + 15 reglas de oro | ✅ |
| 3.5.7 | Sección "Habilitación DIAN" en `res.config.settings` | ✅ |
| 3.5.8 | Estado y bloqueo: `insotech_dian_config_state` + readonly | ✅ |

---

## 🟡 En Progreso

### FASE 4 — Configuración Producción + Cobertura Funcional

| ID | Item | Prioridad | Estado | Responsable |
|---|---|---|---|---|
| 4.0 | Fix configuración DIAN en diario para producción | 🔴 Crítica | ✅ Resuelto por config | David |
| 4.1 | Notas Débito: verificar PRE-INV en `out_invoice` + `debit_note=True` | 🟡 Media | Pendiente | — |
| 4.2 | Documento Soporte (DSNO): extender PRE-INV a compras electrónicas | 🟡 Media | Pendiente | — |
| 4.3 | DV Automático: `_compute_dv()` en `res.partner` — quick win | 🟢 Alta | Pendiente | — |
| 4.4 | Diagnóstico Inteligente de Errores DIAN | 🟢 Alta | Pendiente | — |
| 4.5 | Pre-validación de Contactos (reduce rechazos 70%) | 🟢 Alta | Pendiente | — |

### FASE 5 — QA y Validación

| ID | Item | Prioridad | Estado | Responsable |
|---|---|---|---|---|
| 5.1 | Habilitación DIAN real | — | ✅ Completada (22/03/2026) | David |
| 5.2 | Facturación en producción: primera FE real | — | ✅ FE1 aceptada (23/03/2026) | David |
| 5.3 | Tests automatizados: unit tests PRE-INV → aceptación → mutación | 🟡 Media | Pendiente | — |
| 5.4 | Pruebas E2E API: `insotech_core` → `insotech_saas_server` → respuesta | 🟡 Media | Pendiente | — |
| 5.5 | Desactivar DEV MODE en producción (`insotech.dev_mode`) | 🔴 Crítica | Pendiente | David |

---

## 🔴 Pendiente

### FASE 6 — Port a Odoo 18

| ID | Item | Prioridad | Estado |
|---|---|---|---|
| 6.1 | Migración de código Python/XML (ver `GUIA_MIGRACION_V18.md`) | 🟡 Media | Pendiente |
| 6.2 | Wizard self-service: datos del emisor dinámicos (no hardcodeados) | 🟡 Media | Pendiente |

### Configuración Manual (Admin)

| ID | Item | Prioridad | Responsable |
|---|---|---|---|
| 3.3 | Producto suscripción en Odoo Subscriptions nativo | 🟡 Media | David |
| 3.8 | Cloudflare Rate Limiting: máx 30 req/min por IP | 🟡 Media | David |

---

## ⚪ Backlog Futuro (No priorizado)

| ID | Item | Tipo |
|---|---|---|
| F.1 | Multi-empresa: secuencia PRE-INV por compañía | Feature |
| F.2 | HMAC signature: firmar payload API `/verify` | Security |
| F.3 | Dashboard DIAN: gráfico FE enviadas/aceptadas/rechazadas + semáforo | Feature |
| F.4 | Cron reintentos DIAN: consultar `GetStatusZip` para facturas pendientes | Feature |
| F.5 | Wizard self-service vendible: datos del emisor ingresados por usuario | Feature |
| F.6 | Notificación agrupada: cron diario con resumen de intentos sospechosos | Feature |
| F.7 | Portal de Partners: sub-clientes y consumo en portal web | Feature |
| F.8 | Pruebas E2E con cliente real diferente a InSoTech | QA |
| F.9 | Cron alerta de agotamiento resolución (90% consumido) | Feature |
| F.10 | Contingencia Tipo 4: proceso de 48h para documentos offline | Compliance |

---

## Métricas del Proyecto

| Métrica | Valor |
|---|---|
| Módulos desarrollados | 4 (`insotech_core`, `insotech_l10n_co_advanced`, `insotech_dian_wizard`, `insotech_saas_server`) |
| Errores DIAN descubiertos y resueltos | 15+ |
| Reglas de oro documentadas | 18 |
| Aprendizajes documentados | 7+ archivos |
| Primera factura real aceptada | 23/03/2026 — FE1 con CUFE |
| Versión del módulo principal | v19.0.1.3.0 |

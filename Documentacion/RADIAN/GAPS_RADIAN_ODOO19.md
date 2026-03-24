# Análisis de Gaps — RADIAN en Odoo 19

> **Proyecto:** InSoTech Localización Colombiana Avanzada
> **Fecha:** 2026-03-24

---

## Tabla de Gaps Principal

| Funcionalidad | Odoo 19 Nativo | Siigo | Loggro | Alegra | Lo que InSoTech debería ofrecer |
|---|---|---|---|---|---|
| **EVENTOS BÁSICOS** | | | | | |
| Acuse de recibo (030) | ✅ Manual | ✅ | ✅ | ✅ | ✅ Mantener nativo |
| Recibo del bien (032) | ✅ Manual | ✅ | ✅ | ✅ | ✅ Mantener nativo |
| Aceptación expresa (033) | ✅ Manual | ✅ | ✅ | ✅ | ✅ Mantener nativo |
| Rechazo (031) | ✅ Manual | ✅ | ✅ | ✅ | ✅ Mantener nativo |
| Reclamo (034) | ✅ Manual | ✅ | ✅ | ✅ | ✅ Mantener nativo |
| Aceptación tácita (035) | ⚠️ Manual | ✅ Vendedor emite | ❌ | ❌ | ✅ **CRON automático** |
| **PORTAL Y ACCESO EXTERNO** | | | | | |
| Portal personas naturales | ❌ | ❌ | ❌ | ❌ | ✅ **DIFERENCIADOR #1** |
| Acciones desde correo | ❌ | ❌ | ❌ | ❌ | ✅ **DIFERENCIADOR #2** |
| Vista pública FE (sin login) | ❌ | ❌ | ❌ | ❌ | ✅ **DIFERENCIADOR #3** |
| **TÍTULO VALOR** | | | | | |
| Inscripción título valor (036) | ❌ | ❌ | ⚠️ Parcial | ⚠️ Parcial | 🟡 Evaluar demanda |
| Endoso en propiedad (037) | ❌ | ❌ | ❌ | ❌ | 🟡 Factoring futuro |
| Endoso en garantía (038) | ❌ | ❌ | ❌ | ❌ | 🟡 Factoring futuro |
| Otros endosos (039-047) | ❌ | ❌ | ❌ | ❌ | ❌ Baja prioridad |
| **UX Y VISIBILIDAD** | | | | | |
| Timeline visual de eventos | ❌ | ❌ | ❌ | ❌ | ✅ **DIFERENCIADOR #4** |
| Notificaciones de estado | ❌ | ❌ | ❌ | ❌ | ✅ Chatter + email |
| Dashboard RADIAN | ❌ | ❌ | ❌ | ❌ | 🟡 Backlog futuro |

---

## Gaps Críticos (Debemos Cerrar para Competir)

> [!CAUTION]
> Estos gaps nos dejan **desventaja competitiva directa** frente a Siigo, Loggro y Alegra.

| # | Gap | Impacto | Esfuerzo | Prioridad |
|---|-----|---------|----------|-----------|
| G1 | No generamos eventos 030-034 desde InSoTech | Odoo nativo los hace, pero si queremos extenderlo debemos entenderlo | Bajo | 🟡 Media |
| G2 | Sin CRON automático para aceptación tácita (035) | Riesgo legal — facturas sin aceptación | Bajo (5h) | 🔴 Alta |

---

## Oportunidades de Diferenciación (Nadie lo Ofrece)

> [!IMPORTANT]
> Estas oportunidades representan el **mayor valor comercial** para InSoTech. NINGÚN competidor las ofrece.

| # | Oportunidad | Impacto Comercial | Esfuerzo | Prioridad |
|---|-------------|-------------------|----------|-----------|
| O1 | **Portal receptor para personas naturales** — Página web con token único donde el receptor puede ver la FE y aceptar/rechazar sin cuenta Odoo | 🔴 Muy Alto — abre mercado B2C | Alto (40-60h) | 🔴 Alta |
| O2 | **Acciones desde correo electrónico** — Links de acción directa en el correo de la FE | 🔴 Alto — reduce fricción | Medio (15-20h) | 🔴 Alta |
| O3 | **Timeline visual de eventos** — Widget OWL que muestra el flujo 030→032→033/031 con estados y fechas | 🟡 Medio — UX premium | Medio (15-20h) | 🟢 Alta |
| O4 | **Vista pública de FE** — URL accesible sin login con datos de la factura + PDF + verificación CUFE | 🟡 Medio — transparencia | Bajo (10-15h) | 🟢 Alta |

---

## Gaps Adicionales (del Informe Técnico 24/03/2026)

> [!WARNING]
> Estos gaps son de **cumplimiento normativo** (Anexo 1.9, vigente desde 01/05/2024).

| # | Gap | Impacto | Esfuerzo | Prioridad |
|---|-----|---------|----------|-----------|
| G3 | SHA-384 en CUFE/CUDE (Anexo 1.9 exige SHA-384, no SHA-256) | 🔴 Rechazo DIAN si no cumple | Bajo (2-3h) | 🔴 Crítica |
| G4 | Sin manejo Contingencia Tipo 3 (falla DIAN) ni Tipo 4 (falla propia) | 🔴 Bloqueo operativo | Medio (10-15h) | 🟡 Media |
| G5 | Sin bloqueo NC/ND tras aceptación título valor (irrevocabilidad) | 🔴 Riesgo legal | Bajo (3-5h) | 🔴 Alta |
| G6 | Sin selector "vocación de circulación" para FE | 🟡 Se generarían eventos innecesarios | Bajo (3-5h) | 🟢 Alta |
| G7 | Sin alerta proactiva vencimiento certificado digital (90 días) | 🟡 Bloqueo operativo inesperado | Bajo (3-5h) | 🟢 Alta |

---

## Funcionalidades Futuras (Evaluar Según Demanda)

| # | Funcionalidad | Cuándo | Condición |
|---|---------------|--------|-----------|
| F1 | Eventos título valor (036-047) | Q4 2026+ | Solo si hay demanda de factoring |
| F2 | Dashboard RADIAN completo | Q3 2026 | Después de implementar eventos básicos |
| F3 | Integración con plataformas de factoring | 2027+ | Requiere F1 + mercado validado |
| F4 | RADIAN 2.0 — APIs para fintech | 2027+ | Según evolución normativa |
| F5 | Tokenización de facturas | 2027+ | Pendiente regulación |
| F6 | Documento Equivalente POS Electrónico (Res. 165) | Q3 2026 | Cliente POS |

---

## Resumen Estratégico

```
CUMPLIMIENTO NORMATIVO (cerrar YA):
├── G3: SHA-384 en CUFE/CUDE → 2-3 horas ← URGENTE
├── G5: Bloqueo NC/ND tras aceptación → 3-5 horas
├── G6: Selector vocación de circulación → 3-5 horas
└── G7: Alerta vencimiento certificado → 3-5 horas

PARIDAD (cerrar gaps para competir):
├── G2: CRON aceptación tácita automática → 5 horas
└── G1: Entender/extender eventos nativos → investigación lista ✅

DIFERENCIACIÓN (ganar mercado):
├── O1: Portal personas naturales → 40-60 horas ← MÁXIMA PRIORIDAD
├── O2: Acciones desde correo → 15-20 horas
├── O3: Timeline visual → 15-20 horas
└── O4: Vista pública FE → 10-15 horas

RESILIENCIA (protección operativa):
└── G4: Contingencias Tipo 3 + 4 → 10-15 horas

FUTURO (evaluar demanda):
├── F1: Eventos título valor (036-047)
├── F2: Dashboard RADIAN
├── F3: Integración factoring
├── F4: RADIAN 2.0 APIs fintech
└── F5: Tokenización
```

> **Inversión total para cumplimiento + diferenciación: ~95-140 horas**
> **Resultado: 4 funcionalidades únicas + cumplimiento normativo completo Anexo 1.9**


# Estrategia Comercial — InSoTech

> **Empresa:** INFINITY SOLUTIONS TECHNOLOGY S.A.S (InSoTech)
> **NIT:** 901797249-5
> **Última actualización:** 2026-03-23

---

## 1. Propuesta de Valor

InSoTech ofrece una **suite de facturación electrónica DIAN** para Odoo 19 (y próximamente 18) que resuelve los 3 problemas críticos de la facturación electrónica en Colombia:

| Problema | Cómo lo resuelve InSoTech |
|---|---|
| **Pérdida de consecutivos DIAN** — Odoo nativo consume el consecutivo al confirmar, antes de saber si la DIAN acepta. Si rechaza, el número se pierde | Motor **PRE-INV**: nombre temporal hasta que DIAN acepta. Cero pérdida de consecutivos. |
| **Habilitación compleja** — El proceso de habilitación como software propio requiere 50+ documentos XML firmados, SOAP, UBL 2.1 | **Wizard automatizado**: genera, firma y envía los 50 documentos en minutos. |
| **Errores DIAN crípticos** — La DIAN devuelve códigos sin contexto | **Diagnóstico inteligente** (roadmap): traduce errores DIAN a mensajes accionables en español. |

### Diferenciadores vs Competencia

| Característica | InSoTech | Odoo Nativo | Competidores locales |
|---|---|---|---|
| Protección de consecutivos (PRE-INV) | ✅ | ❌ | ❌ |
| Habilitación como software propio | ✅ Automatizado | ❌ Manual | Parcial |
| Soporte Odoo 19 Enterprise | ✅ | ✅ | ❌ (mayoría en 16/17) |
| Modelo SaaS con licencia | ✅ Grace period 72h | N/A | ❌ |
| Validación de licencia offline-resiliente | ✅ | N/A | ❌ |
| Documentación y reglas de oro DIAN | ✅ 18 reglas | ❌ | ❌ |
| Contador visual de resolución | ✅ | ❌ | ❌ |
| Verificación CUFE en portal DIAN | ✅ 1 clic | ❌ Manual | ❌ |

---

## 2. Modelo de Negocio

### Arquitectura de Módulos (4 productos)

```
┌─────────────────────────────────────────────────┐
│              Cliente Odoo (empresa)              │
│                                                   │
│  ┌──────────────────┐  ┌────────────────────────┐ │
│  │  insotech_core   │  │ insotech_l10n_co_      │ │
│  │  (Motor SaaS)    │──│ advanced (FE DIAN)     │ │
│  │  Licencia + API  │  │ PRE-INV + Mutación     │ │
│  └────────┬─────────┘  └────────────────────────┘ │
│           │                                        │
│  ┌────────┴─────────┐                             │
│  │ insotech_dian_   │  (one-time, independiente) │
│  │ wizard           │                             │
│  │ Habilitación DIAN│                             │
│  └──────────────────┘                             │
└──────────────────────────┬──────────────────────────┘
                           │ API /verify
                      ┌────┴──────────────┐
                      │ insotech_saas_    │
                      │ server            │
                      │ (insotech.it)     │
                      │ Licencias + Logs  │
                      └───────────────────┘
```

### Planes de Licenciamiento

| Plan | Descripción | Validación |
|---|---|---|
| **Suscripción** | Licencia anual/mensual ilimitada | Token + fecha de vencimiento |
| **Pay-per-use** | Pago por factura enviada a DIAN | Token + contador de consumo |
| **Partner** | Para integradores Odoo que revenden | Token + sub-licencias |

### Flujo de Ingresos

```
1. SETUP (one-time)
   ├── Habilitación DIAN (insotech_dian_wizard)
   ├── Configuración Odoo (diarios, resolución, certificado)
   └── Capacitación al usuario

2. RECURRENTE (mensual/anual)
   ├── Licencia SaaS (insotech_core valida contra insotech_saas_server)
   ├── Soporte técnico
   └── Actualizaciones (nuevos errores DIAN, cambios normativos)

3. PAY-PER-USE (opcional)
   └── Cada factura enviada a DIAN consume 1 crédito
```

---

## 3. Mercado Objetivo

### Segmento Primario
- **Empresas colombianas** obligadas a facturar electrónicamente (todas con NIT)
- **Usuarios de Odoo 19/18 Enterprise** en Odoo.sh o on-premise
- **Volumen:** 1 - 50,000 facturas/mes

### Segmento Secundario
- **Integradores Odoo** en Colombia que necesitan ofrecer facturación DIAN a sus clientes
- **Modelo:** Partner con sub-licencias

### Tamaño del Mercado (Colombia)
- +1.5M de empresas obligadas a facturar electrónicamente
- ~5,000 empresas usan Odoo en Colombia (estimado)
- Mercado potencial: empresas Odoo que necesitan FE DIAN robusta

---

## 4. Pricing (Referencia)

> ⚠️ **Estos valores son referenciales** — ajustar según investigación de mercado.

| Concepto | Precio Sugerido (COP) | Precio Sugerido (USD) |
|---|---|---|
| Setup + Habilitación DIAN | $2,000,000 - $5,000,000 | $500 - $1,200 |
| Licencia mensual (suscripción) | $200,000 - $500,000 | $50 - $120 |
| Licencia anual (descuento) | $2,000,000 - $5,000,000 | $500 - $1,200 |
| Pay-per-use (por factura) | $500 - $2,000 | $0.12 - $0.50 |
| Soporte técnico mensual | $300,000 - $800,000 | $75 - $200 |

### Costo de Desarrollo (Referencia Interna)

| Item | Horas estimadas | Costo mercado (COP) |
|---|---|---|
| Motor PRE-INV (Fase 2) | 80+ horas | $16,000,000+ |
| Habilitación DIAN (Fase 3.5) | 60+ horas | $12,000,000+ |
| Servidor API SaaS (Fase 3) | 40+ horas | $8,000,000+ |
| Motor SaaS Core (Fase 1) | 30+ horas | $6,000,000+ |
| **Total inversión en desarrollo** | **200+ horas** | **$42,000,000+** |

---

## 5. Roadmap Comercial

### Q1 2026 (Actual) — Validación
- [x] Primer cliente en producción (InSoTech = dogfooding)
- [x] Primera factura real aceptada por DIAN (FE1 — 23/03/2026)
- [ ] Desactivar DEV MODE y validar licencia real
- [ ] Emitir primeras 10 facturas reales

### Q2 2026 — Estabilización
- [ ] Port a Odoo 18 (ampliar mercado)
- [ ] Tests automatizados (E2E)
- [ ] Cloudflare Rate Limiting activo
- [ ] Diagnóstico Inteligente de Errores DIAN
- [ ] Pre-validación de Contactos
- [ ] Primer cliente externo (piloto)

### Q3 2026 — Crecimiento
- [ ] Portal de Partners
- [ ] Dashboard DIAN
- [ ] Programa de Partners (integradores)
- [ ] 5 clientes activos

### Q4 2026 — Escala
- [ ] Wizard self-service vendible (setup sin intervención InSoTech)
- [ ] Documento Soporte (DSNO)
- [ ] Multi-empresa
- [ ] 15+ clientes activos

---

## 6. Canales de Distribución

| Canal | Descripción | Estado |
|---|---|---|
| **Directo** | Venta directa a empresas colombianas con Odoo | Activo |
| **Odoo.sh Submodule** | Instalación como submódulo git en Odoo.sh | ✅ Validado |
| **Partners Odoo** | Integradores que revenden con licencia partner | Roadmap Q3 |
| **Odoo App Store** | Publicación en apps.odoo.com | Roadmap Q4 |
| **Website InSoTech** | Landing page con demo y signup | En desarrollo |

---

## 7. Activos Técnicos (IP)

| Activo | Descripción | Valoración |
|---|---|---|
| Motor PRE-INV | Único en el mercado — protección de consecutivos DIAN | 🔴 Alta |
| Wizard de habilitación | Automatiza proceso de 2-3 días en minutos | 🔴 Alta |
| 18 reglas de oro DIAN | Know-how documentado de 15+ errores reales | 🟡 Media |
| Servidor API SaaS | Infraestructura de licenciamiento con grace period | 🟡 Media |
| Base de conocimiento | 7+ documentos de aprendizajes técnicos | 🟡 Media |

# Prompt para Agente de Investigación RADIAN

> **Objetivo:** Investigar los eventos RADIAN en Odoo 19, documentar cómo funcionan, identificar oportunidades de mejora, y diseñar soluciones que hagan de InSoTech el mejor motor RADIAN del mercado colombiano.

---

## Contexto del Proyecto

Somos **InSoTech** — desarrollamos un módulo de facturación electrónica avanzado para Odoo Colombia (`insotech_l10n_co_advanced`). Ya tenemos en producción:

- Facturación electrónica (FE) con protección de consecutivos (PRE-INV)
- Notas Crédito (NC)
- Licenciamiento SaaS con API propia
- Habilitación DIAN automatizada

### Repositorios

- **Código V19:** `/home/david/odoo-projects/insotech_l10n_co_advanced` (rama `19.0`)
- **Producción Odoo.sh:** `/home/david/odoo-projects/insotech` (rama `produccion`)
- **Documentación:** `Documentacion/Backlog/BACKLOG.md` (fuente de verdad de prioridades)

### Reglas estrictas

1. **NO crear campos nuevos** en modelos nativos de Odoo
2. **NO modificar la interfaz nativa** de Odoo (no agregar botones, vistas ni campos visibles)
3. **NO hacer push a la rama `produccion`** sin autorización explícita del usuario
4. Pushear siempre a `staging_produccion` para pruebas

---

## Tu Misión: Fase 7 — Eventos RADIAN

### 7.1 — Investigación (PRIMERA PRIORIDAD)

Debes investigar y documentar exhaustivamente:

#### A. ¿Qué es RADIAN?

RADIAN es el sistema de Registro y Anotación de las Facturas Electrónicas de Venta como Título Valor, definido por la DIAN en Colombia (Resolución 000085 de 2022). Los eventos RADIAN son:

| Código | Evento | Quién lo emite |
|---|---|---|
| 030 | Acuse de recibo de FE | Receptor (adquiriente) |
| 032 | Recibo del bien/prestación del servicio | Receptor |
| 033 | Aceptación expresa | Receptor |
| 031 | Rechazo de la FE | Receptor |
| 034 | Reclamo (con código de reclamo) | Receptor |
| 035 | Aceptación Tácita | Automático (DIAN, tras 3 días) |
| 036 | Inscripción del Título Valor | Poseedor legítimo |
| 037 | Endoso en propiedad | Poseedor legítimo |
| 038 | Endoso en garantía | Poseedor legítimo |
| 039 | Endoso en procuración | Poseedor legítimo |
| 040 | Cancelación del endoso | Poseedor legítimo |
| 041 | Limitación de circulación | Poseedor legítimo |
| 042 | Terminación de limitaciones | Poseedor legítimo |
| 043 | Mandato | Poseedor legítimo |
| 044 | Pago | Poseedor legítimo |
| 045 | Informe para el pago | Factor/Comprador |
| 046 | Protesto | Poseedor legítimo |
| 047 | Transferencia de derechos | Poseedor legítimo |

#### B. Investigar en el código fuente de Odoo 19

1. **Buscar en el código Enterprise** (`/home/odoo/src/enterprise/`) el módulo `l10n_co_dian` o cualquier archivoque haga referencia a RADIAN, `ApplicationResponse`, eventos 030-047
2. **Documentar:**
   - ¿Qué modelos usa? (`account.edi.document`? modelo propio?)
   - ¿Qué eventos implementa? (¿solo 030-034 o también los de título valor 036-047?)
   - ¿Cómo se envían los eventos? (¿SOAP? ¿REST?)
   - ¿Dónde se registran en la UI? (¿en la factura? ¿en un menú propio?)
   - ¿Funciona para personas naturales que no tienen cuenta Odoo?
   - ¿Se puede aceptar/rechazar desde correo electrónico?

#### C. Investigar la competencia

Investigar en la web cómo los siguientes competidores manejan RADIAN:

1. **Siigo:** ¿Tiene portal para que el receptor acepte/rechace sin entrar al ERP? ¿Envío por correo?
2. **Loggro:** ¿Tiene eventos RADIAN completos? ¿Hasta qué número?
3. **Alegra:** ¿Tiene timeline visual de eventos? ¿Permite acción desde correo?
4. **Jorels (Odoo):** ¿Tiene módulo RADIAN para Odoo? ¿Gratuito o pago?

#### D. Investigar normativa DIAN

1. Resolución 000085 de 2022 (RADIAN)
2. Anexo técnico del ApplicationResponse para eventos
3. WSDLs y endpoints DIAN para envío de eventos
4. ¿Qué cambia entre habilitación y producción para eventos?

### 7.2 — Oportunidades de Mejora Identificadas

Basándote en la investigación, documentar un análisis de gaps:

| Funcionalidad | Odoo 19 nativo | Siigo | Lo que InSoTech debería ofrecer |
|---|---|---|---|
| Eventos 030-034 | ¿? | ✅ | ✅ |
| Portal para personas naturales | ❌ (hipótesis) | ¿? | ✅ → DIFERENCIADOR |
| Aceptar/rechazar desde correo | ❌ (hipótesis) | ¿? | ✅ → DIFERENCIADOR |
| Eventos título valor (036-047) | ❌ (hipótesis) | ¿? | Evaluar demanda |
| Timeline visual de eventos | ❌ (hipótesis) | ¿? | ✅ bonito para UX |

### 7.3 — Entregables esperados

Al finalizar tu investigación, debes producir:

1. **`Documentacion/RADIAN/INVESTIGACION_RADIAN.md`** — Documento exhaustivo con todo lo investigado
2. **`Documentacion/RADIAN/GAPS_RADIAN_ODOO19.md`** — Tabla de gaps y oportunidades
3. **`Documentacion/RADIAN/PLAN_RADIAN_INSOTECH.md`** — Plan de implementación propuesto con fases
4. Actualización del `BACKLOG.md` con items concretos derivados de la investigación

---

## Preguntas que debes responder

1. ¿Odoo 19 ya implementa todos los eventos RADIAN (030-047) o solo algunos?
2. ¿Un receptor que NO tiene Odoo puede aceptar/rechazar una factura? ¿Cómo?
3. ¿Qué pasa con personas naturales que reciben facturas? ¿Pueden usar el portal?
4. ¿Hay algún módulo comunitario (OCA, Jorels) que complete lo que Odoo nativo no hace?
5. ¿Cuánto esfuerzo llevaría crear un portal web ligero donde el receptor apruebe/rechace sin tener cuenta Odoo?
6. ¿Es técnicamente viable enviar links de acción por correo?
7. ¿Qué necesitamos para que una factura electrónica sea legalmente un título valor negociable?

---

## Skills y documentación a consultar

Antes de escribir código, lee estas skills:
- `/home/david/odoo-projects/insotech_l10n_co_advanced/.agent/skills/metodologia-de-trabajo-insotech/SKILL.md`
- `/home/david/odoo-projects/insotech_l10n_co_advanced/.agent/skills/odoo-v19-buenas-practicas/SKILL.md`
- `/home/david/odoo-projects/insotech_l10n_co_advanced/.agent/skills/base-de-conocimiento/SKILL.md`

Documentación existente:
- `Documentacion/Backlog/BACKLOG.md` — Backlog actualizado
- `Documentacion/Backlog/ANALISIS_COMPETITIVO.md` — Tabla comparativa vs Siigo/Loggro/Alegra
- `Documentacion/Backlog/ESTRATEGIA_COMERCIAL.md` — Estrategia de producto

# Investigación: Contingencia Tipo 4 — DIAN, Odoo V19, Competencia

> **Fecha:** 2026-03-24
> **Investigador:** Agente InSoTech
> **Objetivo:** Determinar si implementar Contingencia Tipo 4 y cómo

---

## 1. ¿Qué dice la DIAN?

### Dos tipos de contingencia (no solo uno):

| Tipo | Código | Causa | Quién falla |
|------|--------|-------|-------------|
| **03** | `OperationType=03` | Falla del facturador o proveedor tecnológico (tu software, tu internet) | **Tú** |
| **04** | `OperationType=04` | Falla del sistema de validación de la DIAN (servidores DIAN caídos) | **DIAN** |

### Tipo 03 — Falla del facturador
1. Emitir factura en **papel/talonario** (requiere resolución de contingencia previa de la DIAN)
2. Cuando se recupere el sistema, transcribir a formato electrónico
3. Enviar a DIAN marcado como `OperationType=03` dentro de **48 horas**

### Tipo 04 — Falla de la DIAN (el que nos interesa)
1. Verificar caída: **4 intentos** con intervalos de **20 segundos**
2. Almacenar evidencia del error (HTTP 500/503/507)
3. Emitir factura al cliente **sin validación previa**
4. Cuando DIAN vuelva (reintentar 30 min después), enviar marcada como `OperationType=04`
5. Plazo máximo: **48 horas** desde que DIAN se recupera
6. La factura DEBE ir **firmada con certificado digital**

---

## 2. ¿Qué tiene Odoo V19 nativo?

### Campo existente
```python
# En account.move (l10n_co_dian):
l10n_co_edi_operation_type  # Selection — Tipo de operación
```

### Lo que NO tiene (verificado):
- ❌ NO hay lógica de retry automático (4 intentos × 20s)
- ❌ NO hay detección automática de caída DIAN
- ❌ NO hay campo para almacenar evidencia de error
- ❌ NO hay modo contingencia activable
- ❌ NO hay CRON de re-transmisión a 48h

**Conclusión:** Odoo V19 tiene el campo `operation_type` pero **cero automatización de contingencia**.

---

## 3. ¿Cómo lo hace la competencia?

### Siigo
- Soporta **Tipo 03** (talonario): el usuario configura un "comprobante de contingencia" marcado como "Usar como documento electrónico" → selecciona "Contingencia / instrumento electrónico de transmisión – tipo 03"
- **No hay evidencia de Tipo 04 automatizado** — parece ser manual

### Alegra
- Soporta **Tipo 03**: el usuario crea la factura de contingencia manualmente → Alegra la marca como "Contingencia 03" al enviarla
- Documentación pública sobre solicitud de resolución de contingencia a la DIAN
- **No hay mención de detección automática de caída DIAN**

### Conclusión competencia
- Ambos soportan **Tipo 03** (manual, con resolución de talonario)
- **Ninguno parece tener Tipo 04 automatizado** (detección + retry + re-envío)
- Esto significa que **Tipo 04 automatizado es un DIFERENCIADOR** si lo implementamos

---

## 4. Análisis: ¿Lo implementamos?

### Argumentos a favor ✅
- Es **requisito del Anexo 1.9** (cumplimiento normativo)
- La competencia **no lo automatiza** → diferenciador
- Nuestro sistema PRE-INV ya "aguanta" facturas sin enviar → base ideal para contingencia
- Odoo tiene el campo `operation_type` listo → solo falta la lógica

### Argumentos en contra ❌
- La DIAN **rara vez cae** (quizá 2-3 veces al año, por horas)
- Requiere una **resolución de contingencia separada** de la DIAN (¿el cliente la tiene?)
- Son 5-8 horas de desarrollo por algo que se usaría 2-3 veces al año
- El portal receptor (7.2) tiene **mucho más valor comercial**

### Recomendación

| Prioridad | Acción |
|-----------|--------|
| **Ahora** | Sprint 2 → Portal Receptor (7.2) — **alto valor comercial** |
| **Después** | Sprint 3 → Contingencia Tipo 4 — cumplimiento normativo, diferenciador |
| **Opcional** | Contingencia Tipo 03 — talonario (la mayoría de clientes NO tiene resolución de contingencia) |

---

## 5. Diseño técnico preliminar (si se decide implementar)

```python
# Flujo propuesto para Tipo 04:
# 1. _post() envía a DIAN → timeout/500/503
# 2. Retry automático: 4 intentos × 20s (totales: ~80s)
# 3. Si 4 intentos fallan:
#    a) Marcar factura como insotech_contingency_mode = True
#    b) Almacenar error evidence (JSON: timestamps + HTTP codes)
#    c) l10n_co_edi_operation_type = '04'
#    d) Factura se emite con nombre DIAN (NO PRE-INV)
#    e) Post en chatter: "⚠️ Contingencia Tipo 4 activada"
# 4. CRON cada 30 min:
#    a) Buscar facturas en contingencia
#    b) Intentar re-enviar a DIAN
#    c) Si DIAN responde → marcar como enviada
#    d) Si >48h sin éxito → alerta crítica
```

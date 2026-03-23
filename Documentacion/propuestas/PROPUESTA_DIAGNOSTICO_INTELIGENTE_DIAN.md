# Propuesta de Producto: Diagnóstico Inteligente de Errores DIAN

**Autor:** Equipo Técnico InSoTech
**Fecha:** 2026-03-22
**Módulo destino:** `insotech_l10n_co_advanced`
**Prioridad sugerida:** Alta — diferenciador competitivo directo

---

## Resumen Ejecutivo

Proponemos agregar un sistema de **diagnóstico inteligente** que traduzca los errores técnicos de la DIAN en mensajes accionables para el usuario final, y que **pre-valide los datos del contacto antes de enviar** la factura electrónica.

Hoy, cuando la DIAN rechaza una factura, el usuario ve un código críptico como `FAJ28`. No sabe qué corregir, dónde ir en Odoo, ni qué campo tiene el problema. Esto genera tickets de soporte, frustración, y retraso en la facturación.

**Resultado esperado:** El usuario corrige el problema solo, en segundos, sin escalar a soporte.

---

## Problema Actual

### Lo que ve el usuario hoy

```
❌ Error DIAN: "Documento con errores en campos mandatorios"
   Regla: FAJ28
```

### Lo que debería ver

```
⚠️ La factura FV-001234 no pudo enviarse a la DIAN.

📋 Problema detectado:
   El contacto "Distribuidora ABC S.A.S" no tiene dirección
   completa para facturación electrónica.

   Campos faltantes:
   • Ciudad (código DANE)
   • Código Postal
   • Departamento

   🔗 [Abrir contacto para corregir]
```

---

## Solución Propuesta

### Nivel 1 — Traductor de errores DIAN (MVP — 1 sprint)

Un mapa de **regla DIAN → mensaje amigable → campo de Odoo afectado**.

Cuando la DIAN rechaza un documento, el sistema:
1. Parsea el `ApplicationResponse` (ya lo hacemos en el habilitador)
2. Identifica las reglas que fallaron
3. Traduce cada regla a un mensaje en español con la acción exacta
4. Muestra un link directo al registro de Odoo que hay que corregir

**Ejemplo del mapa (ya validado contra la DIAN real):**

| Regla DIAN | Mensaje para el usuario | Campo Odoo |
|------------|------------------------|------------|
| FAJ28 | "Dirección del contacto incompleta" | `partner.city_id`, `state_id`, `zip`, `street` |
| FAK24 | "Dígito de verificación incorrecto" | `partner.l10n_co_verification_digit` |
| FAK41 | "Código tributario del contacto no es válido" | `partner.l10n_co_tax_level_code_id` |
| FAK61 | "Persona natural sin nombre/apellido separado" | `partner.firstname`, `partner.lastname` |
| FAB35 | "Tipo de documento de identidad no configurado" | `partner.l10n_latam_identification_type_id` |
| FAK26 | "Responsabilidad fiscal no configurada" | Obligaciones en el contacto |
| FAN02 | "Método de pago no válido en el diario" | `journal.l10n_co_payment_method` |
| FAD06 | "Error en cálculo de CUFE — contactar soporte" | Varios (técnico) |

**Esfuerzo estimado:** 2-3 días. Ya tenemos el parser de respuesta SOAP que decodifica `ApplicationResponse`.

---

### Nivel 2 — Pre-validación antes del envío (recomendado — 1 sprint)

Validar los datos del contacto **ANTES** de llamar a la DIAN.

```python
def _pre_validate_partner_for_dian(partner):
    """
    Ejecutar ANTES de firmar/enviar.
    Retorna lista de problemas o vacío si todo OK.
    """
    issues = []

    if not partner.vat:
        issues.append({
            'field': 'NIT / Cédula',
            'action': 'Complete el número de identificación',
        })

    if partner.l10n_latam_identification_type_id.l10n_co_document_code == '31':
        # NIT → necesita DV
        if not partner.l10n_co_verification_digit:
            issues.append({
                'field': 'Dígito de verificación',
                'action': 'Calcular DV automáticamente o ingresar manualmente',
            })

    if not partner.city_id or not partner.city_id.l10n_co_code:
        issues.append({
            'field': 'Ciudad',
            'action': 'Seleccione una ciudad con código DANE válido',
        })

    if not partner.zip:
        issues.append({
            'field': 'Código postal',
            'action': 'Ingrese el código postal (6 dígitos)',
        })

    return issues
```

**Beneficio clave:** El usuario ve los errores ANTES de gastar un consecutivo. Combinado con PRE-INV, el flujo sería:

```
Confirmar factura
  → PRE-INV intercepta (sin consecutivo)
    → Pre-validar contacto
      → Si falla: mostrar errores + link al contacto (PARA aquí)
      → Si pasa: asignar consecutivo → firmar → enviar DIAN
        → DIAN acepta: confirmar consecutivo ✅
        → DIAN rechaza: liberar consecutivo + mostrar error traducido
```

**Esfuerzo estimado:** 3-5 días (incluye integración con PRE-INV).

---

### Nivel 3 — Cálculo automático de DV (quick win — 2 horas)

Agregar `_compute_dv()` como campo computado en `res.partner`. Si el tipo de documento es NIT (31), calcular el DV automáticamente al guardar el contacto.

Esto elimina el error FAK24 (DV incorrecto) de raíz.

**Esfuerzo estimado:** 2 horas. Ya tenemos la función validada contra la DIAN.

---

## Análisis Competitivo

| Capacidad | Odoo nativo | Otras localizaciones CO | InSoTech (propuesto) |
|-----------|-------------|------------------------|---------------------|
| Envío a DIAN | ✅ | ✅ | ✅ |
| Mostrar error raw | ✅ | ✅ | ✅ |
| Traducir error a español | ❌ | ❌ | ✅ |
| Indicar campo exacto a corregir | ❌ | ❌ | ✅ |
| Link directo al registro | ❌ | ❌ | ✅ |
| Pre-validar antes de enviar | ❌ | ❌ | ✅ |
| No perder consecutivo en error | ❌ (PRE-INV) | ❌ | ✅ |
| DV automático | ❌ | Parcial | ✅ |

---

## Impacto en el Negocio

### Para clientes SaaS
- **Reducción de tickets de soporte** relacionados con facturación electrónica (estimado: 60-70%)
- **Autoservicio:** El usuario corrige solo sin necesitar asistencia técnica
- **Menos facturas perdidas** por consecutivos gastados en errores

### Para InSoTech
- **Diferenciador comercial** frente a implementadores Odoo genéricos
- **Material de marketing:** "La única localización colombiana que te dice qué corregir"
- **Base para blog técnico** (15 errores DIAN documentados con soluciones)

### Por qué ahora
- Tenemos los **15 errores DIAN validados contra el servicio real**, no contra documentación teórica
- El parser de `ApplicationResponse` ya existe y funciona
- PRE-INV ya intercepta consecutivos — solo falta conectar las piezas
- La competencia no tiene esto

---

## Ruta de Implementación Sugerida

| Fase | Entregable | Esfuerzo | Impacto |
|------|-----------|----------|---------|
| **Quick Win** | DV automático (`_compute_dv`) | 2 horas | Elimina FAK24 |
| **MVP** | Traductor de errores DIAN | 2-3 días | Reduce tickets 50% |
| **Completo** | Pre-validación + integración PRE-INV | 3-5 días | Experiencia diferenciadora |

**Total estimado:** ~1.5 sprints para la solución completa.

---

## Origen de los Datos

Todos los errores documentados fueron encontrados y validados durante la habilitación real de InSoTech ante la DIAN (2026-03-22). No son teóricos — cada regla fue probada contra el servicio `SendBillSync` del ambiente de habilitación.

La base de conocimiento completa está en:
`aprendizajes/dian-habilitacion-facturacion-electronica.md`

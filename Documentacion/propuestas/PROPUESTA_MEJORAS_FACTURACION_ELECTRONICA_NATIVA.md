# Propuesta: Mejoras a la Facturación Electrónica Nativa de Odoo

**Fecha:** 22 de marzo de 2026  
**Autor:** Equipo Técnico InSoTech  
**Módulo base:** `insotech_l10n_co_advanced`  
**Basado en:** Aprendizajes del proceso de habilitación DIAN (15 errores de validación resueltos)

---

## Contexto

Durante el proceso de habilitación de InSoTech ante la DIAN, resolvimos **15 errores de validación** que revelan brechas significativas entre lo que Odoo genera nativamente y lo que la DIAN realmente valida. Estos aprendizajes nos posicionan para **mejorar la facturación electrónica nativa** y ofrecer un producto diferenciado en el mercado colombiano.

> **Hallazgo clave:** Un solo carácter errado en la Clave Técnica (`8` en vez de `6`) causó horas de rechazo. No hay herramientas en el ecosistema Odoo Colombia que diagnostiquen esto.

---

## Propuestas de Mejora

### 🟢 Fase 1 — Impacto Inmediato (1-2 semanas)

#### 1. Diagnóstico Inteligente de Errores DIAN

**Problema:** Cuando la DIAN rechaza una factura, Odoo muestra un mensaje genérico. El usuario no sabe qué está mal ni cómo corregirlo.

**Solución:** Interceptar el `ApplicationResponse` de la DIAN, parsear los códigos de regla (FAD06, FAJ28, FAB10a, etc.) y mostrar al usuario un mensaje claro en español con la acción correctiva.

**Ejemplos reales:**

| Error DIAN | Mensaje actual en Odoo | Mensaje propuesto |
|-----------|----------------------|-------------------|
| FAJ28 | "Error de validación" | "⚠️ El contacto **ACME SAS** no tiene dirección completa. Vaya a Contactos > ACME > pestaña Dirección y complete: calle, ciudad y código DANE." |
| FAD06 | "CUFE incorrecto" | "⚠️ El hash del documento no coincide. Verifique que los montos de impuestos coincidan con las líneas de factura. [Ver debug CUFE]" |
| FAM06 | "Nombre inválido" | "⚠️ La razón social de **ACME SAS** no coincide con el RUT de la DIAN. Verifique en www.dian.gov.co y actualice el nombre del contacto." |
| Regla 90 | "Documento duplicado" | "⚠️ La factura FV-001 ya fue enviada a la DIAN. No se puede reenviar. Si necesita corregirla, emita una Nota Crédito." |

**Esfuerzo estimado:** 3-4 días  
**Reducción de soporte estimada:** 60-70% de tickets relacionados con DIAN

---

#### 2. Validación Previa de Contactos

**Problema:** El 40% de los rechazos DIAN que vimos son por datos incompletos del contacto (receptor). El usuario no sabe que faltan datos hasta que la DIAN rechaza.

**Solución:** Validar antes de generar el XML:

```
Al confirmar una factura → Verificar datos DIAN del contacto:
  ✅ ¿Tiene NIT o cédula con DV?
  ✅ ¿Tiene dirección con código DANE?
  ✅ ¿Tiene responsabilidad fiscal configurada?
  ✅ ¿Tiene TaxScheme correcto?
  ❌ Si falta algo → Bloquear envío + mostrar qué falta
```

**Esfuerzo estimado:** 2-3 días  
**Impacto:** Elimina rechazos DIAN por datos de contacto incompletos

---

#### 3. CUFE Debug en Logs

**Problema:** FAD06 (CUFE incorrecto) es el error más difícil de diagnosticar. Un carácter errado cambia completamente el hash SHA-384.

**Solución:** Cuando hay error FAD06, logear la cadena raw del CUFE y mostrarla en el chatter de la factura para diagnóstico.

**Esfuerzo estimado:** 1 día  
**Impacto:** Reduce tiempo de resolución de FAD06 de horas a minutos

---

### 🟡 Fase 2 — Valor Diferenciador (2-4 semanas)

#### 4. Retención de Consecutivo hasta Aceptación DIAN

**Problema:** Si la DIAN rechaza una factura, el consecutivo ya fue "gastado". Esto genera huecos en la numeración que pueden activar alertas de la DIAN en auditorías.

**Solución:**
1. Al confirmar factura → asignar consecutivo temporal
2. Enviar a DIAN
3. Si DIAN acepta (StatusCode 00) → confirmar consecutivo definitivo
4. Si DIAN rechaza → liberar consecutivo para reusar

**Esfuerzo estimado:** 5-7 días  
**Impacto:** Cero huecos en numeración, cumplimiento total con resolución de facturación

---

#### 5. Dashboard de Estado DIAN

**Problema:** No hay visibilidad centralizada del estado de la facturación electrónica.

**Solución:** Vista tipo dashboard con:
- 📊 Facturas enviadas / aceptadas / rechazadas (gráfico temporal)
- ⚠️ Top 5 errores más frecuentes del mes
- 📅 Vigencia del certificado digital (alerta a 30 días)
- 🔢 Consecutivos usados vs. disponibles (resolución)
- 🏥 Salud general del sistema (semáforo)

**Esfuerzo estimado:** 5-7 días  
**Impacto:** Visibilidad total para el gerente financiero / contador

---

#### 6. Reintentos Automáticos (Cron DIAN)

**Problema:** La DIAN a veces responde con timeout (Error 500/503). Odoo deja la factura en estado "pendiente" y nadie se da cuenta.

**Solución:** Cron que cada 15 minutos:
1. Busca facturas con estado "Enviado, pendiente de respuesta"
2. Consulta `GetStatusZip` con el Track ID
3. Actualiza estado automáticamente
4. Si hay error → notifica al usuario por mail/chatter

**Esfuerzo estimado:** 3-4 días  
**Impacto:** Cero facturas "perdidas" en el limbo

---

### 🔵 Fase 3 — Producto Premium (1-2 meses)

#### 7. Wizard Self-Service de Habilitación

**Problema actual:** El wizard actual tiene datos hardcodeados de InSoTech. No es vendible directamente.

**Solución:** Refactorizar para que el cliente llene todos los datos:
- Paso 1: Datos de la empresa (NIT, razón social, dirección)
- Paso 2: Certificado digital
- Paso 3: Datos del portal DIAN (Software ID, PIN, Test Set ID)
- Paso 4: Click → Habilitado

**Esfuerzo estimado:** 5-7 días  
**Impacto:** Producto vendible como servicio autónomo

---

#### 8. Soporte Multi-versión (V18 + V19)

**Problema:** El mercado colombiano tiene empresas en V18 y V19.

**Solución:** El core de servicios (`ubl_generator`, `xml_signer`, `soap_client`) es Python puro y **ya es portable**. Solo hay que adaptar la capa Odoo (wizard, vistas, ORM).

**Esfuerzo estimado:** 3-5 días de adaptación  
**Impacto:** Duplica el mercado objetivo

---

## Priorización Sugerida

| Prioridad | Mejora | Esfuerzo | Impacto en ventas |
|-----------|--------|----------|-------------------|
| 🥇 | Diagnóstico inteligente de errores | 3-4 días | Alto — diferenciador único |
| 🥇 | Validación previa de contactos | 2-3 días | Alto — reduce soporte 70% |
| 🥈 | Wizard self-service | 5-7 días | Alto — producto vendible |
| 🥈 | Dashboard DIAN | 5-7 días | Medio — valor visual para PO |
| 🥉 | Retención de consecutivo | 5-7 días | Medio — cumplimiento fiscal |
| 🥉 | Cron reintentos | 3-4 días | Medio — operación robusta |
| 🏅 | CUFE debug | 1 día | Bajo en ventas, alto en soporte |
| 🏅 | Multi-versión V18 | 3-5 días | Alto si hay demanda |

---

## Métricas de Éxito

| Métrica | Baseline (actual) | Target (6 meses) |
|---------|-------------------|-------------------|
| Tickets soporte DIAN / mes | ~15-20 | < 5 |
| Tiempo resolución error DIAN | 2-4 horas | < 15 minutos |
| Clientes habilitados sin soporte | 0% | 80%+ |
| Facturas rechazadas por datos incompletos | ~40% | < 5% |

---

## Conclusión

Estos aprendizajes son resultado directo de resolver **15 errores reales de producción** contra el validador de la DIAN. No son teóricos — cada mejora propuesta resuelve un dolor que experimentamos esta noche. **Ningún otro proveedor Odoo en Colombia tiene esta base de conocimiento.**

La inversión total estimada para Fase 1 + Fase 2 es de **~4 semanas de desarrollo**, con un retorno inmediato en reducción de soporte y diferenciación de producto.

# Investigación Exhaustiva — Eventos RADIAN

> **Proyecto:** InSoTech Localización Colombiana Avanzada
> **Fase:** 7.1 — Investigación RADIAN
> **Fecha:** 2026-03-24
> **Autor:** Agente IA (InSoTech)

---

## 1. ¿Qué es RADIAN?

**RADIAN** (Registro de la factura electrónica de venta como Título Valor) es una plataforma administrada por la **DIAN** (Dirección de Impuestos y Aduanas Nacionales de Colombia), establecida por la **Resolución 000085 del 8 de abril de 2022**.

### Propósito
- Registrar, consultar y dar trazabilidad a las facturas electrónicas de venta que tienen calidad de **título valor**.
- Habilitar la **negociación** de facturas electrónicas (factoring electrónico).
- Garantizar la **unicidad** del tenedor legítimo y la disponibilidad del título para negociación.

### ¿Por qué importa?
- Sin los eventos RADIAN registrados, una factura electrónica **NO** puede usarse como soporte de costos, deducciones ni impuestos descontables.
- Es **obligatorio** para que una factura adquiera la calidad de título valor.
- Habilita el ecosistema de **factoring digital** en Colombia.

---

## 2. Catálogo Completo de Eventos RADIAN

### 2.1 Eventos del Adquiriente (Receptor) — Obligatorios

| Código | Evento | Quién lo emite | Descripción |
|--------|--------|----------------|-------------|
| **030** | Acuse de recibo de FE | Receptor | Confirma que la factura electrónica fue recibida. La FE aún NO es título valor. |
| **032** | Recibo del bien/servicio | Receptor | Confirma que la mercancía o servicio fue recibido. **Activa el plazo de 3 días** para aceptación tácita. |
| **033** | Aceptación expresa | Receptor | El receptor acepta formalmente la factura. La FE se convierte en título valor. |
| **031** | Rechazo de la FE | Receptor | Rechaza la factura. Debe incluir motivo. |
| **034** | Reclamo de la FE | Receptor | Objeción formal por inconsistencias o incumplimiento. |

### 2.2 Evento Automático

| Código | Evento | Quién lo emite | Descripción |
|--------|--------|----------------|-------------|
| **035** | Aceptación tácita | DIAN / Emisor | Si no hay rechazo ni aceptación expresa en **3 días hábiles** después del evento 032, la factura se acepta tácitamente. |

### 2.3 Eventos de Título Valor (Circulación) — Avanzados

| Código | Evento | Quién lo emite | Descripción |
|--------|--------|----------------|-------------|
| **036** | Inscripción del título valor | Poseedor legítimo | Registra la FE como título valor negociable en RADIAN. |
| **037** | Endoso en propiedad | Poseedor legítimo | Transfiere la propiedad del título valor a un tercero. |
| **038** | Endoso en garantía | Poseedor legítimo | Usa el título valor como garantía de una obligación. |
| **039** | Endoso en procuración | Poseedor legítimo | Autoriza a un tercero a cobrar el título valor. |
| **040** | Cancelación del endoso | Poseedor legítimo | Anula un endoso previo. |
| **041** | Limitación de circulación | Poseedor legítimo | Restringe la negociación del título. |
| **042** | Terminación de limitaciones | Poseedor legítimo | Levanta restricciones de circulación. |
| **043** | Mandato | Poseedor legítimo | Delega administrativamente el título. |
| **044** | Pago | Poseedor legítimo | Registra el pago de la obligación. |
| **045** | Informe para el pago | Factor/Comprador | Notifica al deudor sobre el pago pendiente. |
| **046** | Protesto | Poseedor legítimo | Acción legal por impago. |
| **047** | Transferencia de derechos | Poseedor legítimo | Cede los derechos económicos del título. |

### 2.4 Flujo Temporal de Eventos (Timeline)

```
Día 0: Emisor envía FE → DIAN acepta → FE enviada al receptor
  │
  ├─► Evento 030: Acuse de recibo (receptor confirma que recibió la FE)
  │
  ├─► Evento 032: Recibo del bien/servicio (receptor confirma entrega)
  │     │
  │     └─── Comienzan 3 DÍAS HÁBILES ──┐
  │                                       │
  │     ┌───── Opciones del receptor ─────┤
  │     │                                 │
  │     ├─► Evento 033: Aceptación expresa (FE = Título Valor ✅)
  │     ├─► Evento 031: Rechazo (con motivo)
  │     ├─► Evento 034: Reclamo (con código de reclamo)
  │     │                                 │
  │     └─► Evento 035: Aceptación tácita (automática si no hay acción)
  │
  └─►  Eventos 036-047: Circulación del título valor (factoring, endoso, etc.)
```

---

## 3. Investigación del Código Fuente Odoo 19

### 3.1 ¿Qué módulo implementa RADIAN?

El módulo **`l10n_co_dian`** (Enterprise) es el responsable de toda la facturación electrónica colombiana en Odoo 19, incluyendo los eventos RADIAN.

### 3.2 ¿Qué eventos implementa Odoo 19?

**Solo los eventos del adquiriente (030-034) + aceptación tácita manual (035):**

| Evento | Soportado | Tipo | Detalle |
|--------|-----------|------|---------|
| 030 — Acuse de recibo | ✅ | Manual | Botón en factura de proveedor confirmada |
| 032 — Recibo del bien | ✅ | Manual | Botón en factura de proveedor |
| 033 — Aceptación expresa | ✅ | Manual | Botón después de 032 |
| 031 — Rechazo/Reclamo | ✅ | Manual | Botón con motivo requerido |
| 034 — Aceptación tácita | ✅ | Manual* | Se puede generar manualmente si pasaron 3 días sin respuesta tras 032 |
| 036-047 — Título valor | ❌ | — | **No implementado** |

> **\* Nota:** Aunque la aceptación tácita debería ser automática, Odoo la implementa como acción manual. NO hay CRON automático para detección de aceptación tácita.

### 3.3 ¿Cómo se envían los eventos?

- **Protocolo:** SOAP (mismo WS que facturación electrónica)
- **Formato:** ApplicationResponse XML (UBL 2.1)
- **Endpoints:**
  - **Habilitación:** `https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc`
  - **Producción:** `https://vpfe.dian.gov.co/WcfDianCustomerServices.svc`
- **Servicio:** `SendEventUpdateStatus` (para eventos RADIAN)
- **Firma:** XAdES-EPES con certificado digital del emisor del evento

### 3.4 ¿Dónde se registran en la UI?

- **Facturas de proveedor (Vendor Bills):** Pestaña "DIAN" con botones para cada evento
- **Facturas de cliente (Customer Invoices):** Pestaña "DIAN" que muestra eventos recibidos
- **CRON:** Odoo tiene un CRON diario que consulta el estado comercial de las FE
- **No hay menú propio** — todo se gestiona desde la factura

### 3.5 Modelos utilizados

| Modelo | Propósito |
|--------|-----------|
| `account.move` | Factura — contiene la pestaña DIAN con estado de eventos |
| `account.edi.document` | Documento EDI — gestiona el envío/recepción de XMLs |
| `l10n_co_dian.event` (probable) | Modelo propio para eventos RADIAN |

### 3.6 Limitaciones Críticas de Odoo 19 Nativo

1. **❌ Sin portal para personas naturales:** Un receptor que NO tiene cuenta Odoo **no puede** aceptar, rechazar ni ver la factura desde un portal web.
2. **❌ Sin acciones desde correo electrónico:** No se pueden enviar links de acción por email para que el receptor responda sin entrar a Odoo.
3. **❌ Sin eventos de título valor (036-047):** No soporta endosos, inscripción de título valor, ni operaciones de factoring.
4. **❌ Sin aceptación tácita automática:** Es manual, no hay CRON que la detecte.
5. **❌ Sin timeline visual:** No hay representación visual del flujo de eventos.
6. **⚠️ Requiere usuario Odoo:** El receptor debe ser un usuario del sistema Odoo para interactuar con los eventos.

---

## 4. Investigación de la Competencia

### 4.1 Siigo

| Aspecto | Detalle |
|---------|---------|
| **Eventos soportados** | 030, 032, 033, 031, 034, 035 (aceptación tácita emitida por el vendedor) |
| **Portal receptor** | ❌ No tiene portal externo. Todo se gestiona desde la plataforma Siigo del receptor. |
| **Acceso** | Sección "Compras y gastos → Registro de eventos" |
| **Acciones desde correo** | ❌ No. Solo notificaciones por correo, acciones en el portal Siigo. |
| **Título valor (036-047)** | ❌ No implementado en Siigo. |
| **Timeline visual** | ❌ No tiene. Lista plana de eventos con estados. |
| **Personas naturales** | ⚠️ Requieren tener cuenta Siigo activa. No hay portal público. |
| **Habilitación** | Requiere activar módulo, definir perfil de organización, certificado digital. |
| **Fortalezas** | Base de usuarios grande, documentación extensa, soporte en español. |
| **Debilidades** | Sin portal externo, sin acciones por correo, sin título valor. |

### 4.2 Loggro

| Aspecto | Detalle |
|---------|---------|
| **Eventos soportados** | 030, 032, 033, 031, 034 (básicos) |
| **Portal receptor** | ❌ No tiene portal externo para personas naturales. |
| **Acciones desde correo** | ❌ No. |
| **Título valor** | ✅ Parcial — permite "convertir FE en título valor" (inscripción), requiere registro en RADIAN. |
| **Timeline visual** | ❌ No documentado. |
| **Fortalezas** | Interfaz sencilla, precio competitivo. |
| **Debilidades** | Funcionalidad RADIAN limitada a eventos básicos. |

### 4.3 Alegra

| Aspecto | Detalle |
|---------|---------|
| **Eventos soportados** | 030, 032, 033, 031, 034 (acuse de recibo, aceptación) |
| **Portal receptor** | ❌ No tiene portal externo específico para RADIAN. |
| **Acciones desde correo** | ❌ No documentado. |
| **Título valor** | ✅ Parcial — genera facturas compatibles con título valor. |
| **Timeline visual** | ❌ No documentado. |
| **Habilitación** | Rápida — software autorizado por DIAN, proceso simplificado. |
| **Fortalezas** | Usabilidad excelente, habilitación rápida, marca reconocida. |
| **Debilidades** | Sin portal externo RADIAN, sin acciones por correo. |

### 4.4 Jorels (Odoo Community)

| Aspecto | Detalle |
|---------|---------|
| **Eventos soportados** | 030, 032, 033, 031, 034, 035 (RADIAN completo básico) |
| **Portal receptor** | ❌ No documentado. |
| **Acciones desde correo** | ❌ No. |
| **Título valor (036-047)** | ❌ No implementa eventos de título valor avanzados. |
| **Integración** | Módulo para Odoo (Community Edition principalmente). |
| **Precio** | **Pago** — licencia por suscripción. |
| **Versiones** | Odoo 14-17 confirmado. V18/V19 no verificado. |
| **Fortalezas** | Nativo en Odoo, gestión de eventos desde la factura. |
| **Debilidades** | No tiene portal externo, community focus, versiones atrasadas. |

### 4.5 Resumen Competitivo RADIAN

```
                          Siigo  Loggro  Alegra  Odoo19  Jorels  InSoTech
Eventos 030-034            ✅     ✅      ✅      ✅      ✅      🟡
Aceptación tácita (035)    ✅     ❌      ❌      ⚠️*     ✅      🟡
Portal personas naturales  ❌     ❌      ❌      ❌      ❌      🟡 → OPORTUNIDAD
Acciones desde correo      ❌     ❌      ❌      ❌      ❌      🟡 → OPORTUNIDAD
Título valor (036-047)     ❌     ❌ P    ❌ P    ❌      ❌      🟡 → EVALUAR
Timeline visual            ❌     ❌      ❌      ❌      ❌      🟡 → OPORTUNIDAD

P = Parcial  * = Manual
```

> **🎯 CONCLUSIÓN CLAVE:** NINGÚN competidor ofrece portal para personas naturales ni acciones desde correo. Esto es un **DIFERENCIADOR MASIVO** si InSoTech lo implementa.

---

## 5. Normativa DIAN — Detalle Técnico

### 5.1 Resolución 000085 de 2022

- **Objeto:** Regular el registro de la FE de venta como título valor y los eventos asociados.
- **Alcance:** Todos los facturadores electrónicos y adquirientes en Colombia.
- **Plataforma:** RADIAN (administrada por DIAN).
- **Formato técnico:** ApplicationResponse XML basado en UBL 2.1.

### 5.2 Anexo Técnico RADIAN 1.0

| Elemento | Detalle |
|----------|---------|
| **Estándar XML** | UBL 2.1 — `ApplicationResponse` |
| **Firma digital** | XAdES-EPES, RSA-SHA256, política DIAN v2 |
| **CUFE referencia** | Cada evento debe incluir el CUFE de la factura referenciada |
| **Validaciones** | DIAN valida: firma, CUFE, secuencia de eventos, NIT emisor/receptor |
| **Identificador** | CUDE (Código Único de Documento Electrónico) para el ApplicationResponse |

### 5.3 Endpoints DIAN para Eventos

| Entorno | URL del Web Service |
|---------|---------------------|
| **Habilitación** | `https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc` |
| **Producción** | `https://vpfe.dian.gov.co/WcfDianCustomerServices.svc` |
| **WSDL** | Misma URL + `?wsdl` |

**Servicios relevantes:**
- `SendBillSync` — Envío sincrónico de documentos
- `SendEventUpdateStatus` — Envío de eventos RADIAN
- `GetStatus` — Consulta de estado
- `GetStatusZip` — Consulta de estado por lote

### 5.4 Diferencias Habilitación vs Producción para Eventos

| Aspecto | Habilitación | Producción |
|---------|--------------|------------|
| **URL base** | `vpfe-hab.dian.gov.co` | `vpfe.dian.gov.co` |
| **Certificado** | Se puede usar el de pruebas | Obligatorio el de producción |
| **Software ID** | El de habilitación | El de producción |
| **Validación CUFE** | Contra facturas de test | Contra facturas reales |
| **NIT** | Mismo NIT de la empresa | Mismo NIT |
| **Set de pruebas** | Requiere set de pruebas (TestSetId) | No aplica |

### 5.5 Estructura XML del ApplicationResponse (Eventos)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ApplicationResponse xmlns="urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2"
                     xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                     xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
  <cbc:CustomizationID>1</cbc:CustomizationID>
  <cbc:ProfileID>DIAN 2.1</cbc:ProfileID>
  <cbc:ID>[Consecutivo del evento]</cbc:ID>
  <cbc:IssueDate>[Fecha]</cbc:IssueDate>
  <cbc:IssueTime>[Hora]</cbc:IssueTime>
  <cbc:ResponseCode>[030|031|032|033|034|035|036-047]</cbc:ResponseCode>
  <cbc:Note>[Observaciones]</cbc:Note>

  <!-- Referencia a la factura -->
  <cac:DocumentResponse>
    <cac:Response>
      <cbc:ResponseCode>[Código del evento]</cbc:ResponseCode>
      <cbc:Description>[Descripción]</cbc:Description>
    </cac:Response>
    <cac:DocumentReference>
      <cbc:ID>[CUFE de la factura]</cbc:ID>
      <cbc:UUID>[CUFE]</cbc:UUID>
    </cac:DocumentReference>
  </cac:DocumentResponse>

  <!-- Datos del emisor del evento -->
  <cac:SenderParty>...</cac:SenderParty>

  <!-- Datos del receptor del evento -->
  <cac:ReceiverParty>...</cac:ReceiverParty>

  <!-- Firma digital XAdES-EPES -->
  <ds:Signature>...</ds:Signature>
</ApplicationResponse>
```

---

## 6. Respuestas a las Preguntas Clave

### P1: ¿Odoo 19 ya implementa todos los eventos RADIAN (030-047)?
**NO.** Odoo 19 implementa solo los eventos 030-034 (adquiriente) y permite generar manualmente el 035 (aceptación tácita). **No implementa ningún evento de título valor (036-047).**

### P2: ¿Un receptor sin Odoo puede aceptar/rechazar una factura?
**NO.** Odoo 19 nativo requiere que el receptor sea un usuario del sistema Odoo con acceso a la factura de proveedor. No existe un portal público ni mecanismo de correo electrónico para receptores externos.

### P3: ¿Qué pasa con personas naturales?
**No pueden interactuar.** Personas naturales que reciben facturas electrónicas y no tienen una instancia de Odoo propia no tienen forma de registrar los eventos RADIAN desde Odoo. Deben utilizar la plataforma DIAN directamente o un software de terceros.

### P4: ¿Hay algún módulo comunitario que complete lo que falta?
**Jorels** tiene un módulo RADIAN para Odoo Community con eventos 030-035, pero:
- Es de **pago** (licencia por suscripción)
- No verificado para Odoo 18/19
- **No incluye** portal para personas naturales ni acciones desde correo
- **No incluye** eventos de título valor (036-047)

### P5: ¿Cuánto esfuerzo para un portal web ligero?
**Estimación: 40-60 horas** para un MVP que incluya:
- Controller HTTP con token único por factura
- Página web autenticada por token (sin login Odoo)
- Botones: Acusar recibo → Confirmar recepción → Aceptar/Rechazar
- Generación de ApplicationResponse XML firmado
- Envío a DIAN vía SOAP
- Registro del evento en la factura original

### P6: ¿Es viable enviar links de acción por correo?
**SÍ.** Técnicamente viable usando:
- URLs con token JWT o UUID único por factura
- Controller Odoo que procese la acción
- Página de confirmación simple (no requiere login)
- Complejidad adicional: ~15-20 horas sobre el portal base

### P7: ¿Qué necesitamos para título valor negociable?
Para que una FE sea legalmente un título valor se requiere:
1. ✅ FE aceptada por DIAN y enviada al receptor
2. ✅ Evento 030 (Acuse de recibo) registrado
3. ✅ Evento 032 (Recibo del bien/servicio) registrado
4. ✅ Evento 033 (Aceptación expresa) o 035 (Aceptación tácita)
5. 🟡 Evento 036 (Inscripción del título valor) en RADIAN
6. 🟡 Certificado digital del poseedor legítimo
7. 🟡 Registro como participante en RADIAN con rol "Registro"

---

## 7. Fuentes Consultadas

| Fuente | URL/Referencia |
|--------|----------------|
| DIAN — Resolución 000085 de 2022 | dian.gov.co |
| DIAN — Resolución 000165 de 2023 | dian.gov.co |
| DIAN — Resolución 000008 de 2024 (Anexo 1.9) | dian.gov.co |
| DIAN — Comunicado 026 de 2025 | dian.gov.co |
| DIAN — Anexo Técnico RADIAN 1.0 | dian.gov.co |
| Odoo 19 Documentación Oficial | odoo.com/documentation/19.0 |
| Siigo — Centro de Ayuda RADIAN | siigo.com |
| Loggro — Blog Factura Título Valor | loggro.com |
| Alegra — Blog Facturación Electrónica | alegra.com |
| Jorels — Módulo RADIAN Odoo | jorels.com / apps.odoo.com |
| Novasoft — Guía eventos RADIAN | novasoft.com.co |
| Gerencie — Endoso electrónico | gerencie.com |
| Informe técnico InSoTech (PO) | Documento interno 24/03/2026 |

---

## 8. Actualización Normativa 2024-2025

> **Fuente:** Informe técnico del PO (24/03/2026), Resolución 000165/2023, Resolución 000008/2024.

### 8.1 Marco Normativo Actualizado

| Resolución | Fecha | Impacto |
|------------|-------|---------|
| **000085 de 2022** | 08/04/2022 | Establece RADIAN y eventos de FE como título valor |
| **000165 de 2023** | 2023 | Documento Equivalente Electrónico para POS |
| **000008 de 2024** | 2024 | Entrada en vigor del **Anexo Técnico 1.9** (01/05/2024) |
| **Comunicado 026 de 2025** | 2025 | "Identificación Simplificada" (solo Nombre/NIT/Email) |

### 8.2 Requisitos Técnicos Críticos del Anexo 1.9

| Requisito | Detalle | Impacto InSoTech |
|-----------|---------|------------------|
| **SHA-384** | CUFE y CUDE deben generarse con **SHA-384** (no SHA-256) | 🔴 Verificar que `insotech_dian_wizard` use SHA-384 |
| **Redondeo Global** | Obligatorio activar Método de Redondeo Global en Contabilidad → Configuración | 🔴 Documentar en guía de usuario |
| **Firma XAdES-EPES** | Certificados ECD acreditados por ONAC (Certicámara, Viafirma) | ✅ Ya soportado |
| **Formato teléfono** | +57 + 10 dígitos obligatorio para contactos | 🟡 Pre-validación de contactos |
| **Divisa XML** | Siempre COP en XML, incluso en transacciones multimoneda | 🟡 Verificar en exportación |
| **Identificación Simplificada** | Comunicado 026: solo Nombre/NIT/Email mínimo; no bloquear por falta de dirección | 🟡 Ajustar pre-validación |

### 8.3 Protocolos de Contingencia

#### Contingencia Tipo 3 — Falla de la DIAN
```
1. Sistema detecta código de error de indisponibilidad del servidor DIAN
2. Permite la entrega del documento al cliente (PDF + XML sin validación)
3. Cuando DIAN se restablece → validación posterior automática
4. ⚠️ InSoTech debe poder detectar y manejar este escenario
```

#### Contingencia Tipo 4 — Falla del Facturador
```
1. Caída de infraestructura propia (Odoo.sh down, etc.)
2. Se procede con factura de talonario/papel
3. Al restablecerse → sincronización del XML en máximo 48 horas
4. OBLIGATORIO: usar Código de Operación 04 en el XML
5. ⚠️ InSoTech debe soportar Código de Operación 04
```

### 8.4 Alerta Proactiva de Certificados

| Alerta | Umbral | Acción |
|--------|--------|--------|
| Certificado digital próximo a vencer | **90 días** antes | Notificación en dashboard + email al admin |
| Certificado vencido | Día 0 | **Bloqueo total** de operación de FE |

---

## 9. Tendencias del Mercado RADIAN 2026

> **Fuente:** Informe técnico del PO. Estas tendencias definen la hoja de ruta a mediano plazo.

### 9.1 Vocación de Circulación (Regla de Negocio CLAVE)

> **No todas las facturas deben registrarse en RADIAN.** Solo aplica para facturas con "vocación de circulación" — cuando el emisor tiene intención de endosarlas o negociarlas.

**Implicación para InSoTech:** El sistema no debe generar eventos RADIAN automáticamente para todas las facturas. Debe ser una **acción explícita** del emisor cuando desee que la FE circule como título valor.

### 9.2 Cambio en el Detonante del Plazo de Aceptación

| Antes | Ahora (2026) |
|-------|--------------|
| 3 días hábiles desde **recibo físico de la mercancía** | 3 días hábiles desde **recepción de la factura electrónica** |

**Implicación:** Simplifica la lógica del CRON de aceptación tácita. El contador empieza cuando la FE es recibida (evento 030), no cuando se confirma la entrega física.

### 9.3 Irrevocabilidad del Título Valor

> **Una vez aceptada la factura (033 o 035), NO se permiten Notas Crédito ni Notas Débito asociadas en el RADIAN.**

**Implicación para InSoTech:** Debemos implementar una **validación de bloqueo**: si una factura tiene el evento 033/035 registrado, bloquear la creación de NC/ND contra esa factura con mensaje explicativo.

### 9.4 RADIAN 2.0 — Interoperabilidad con Fintech

El mercado exige:
- Validación en **tiempo real** (no asíncrona)
- Interoperabilidad directa con **entidades financieras, bancos y plataformas fintech**
- Registro de eventos **100% digital, automatizado, sin barreras geográficas**

**Implicación:** Posiciona a InSoTech para construir APIs de integración con plataformas de factoring en el futuro.

### 9.5 Tokenización de Facturas (Futuro)

- Exploración de facturas electrónicas como **activos digitales tokenizados**
- Potencial **fraccionamiento** de facturas para inversión
- Ecosistema descentralizado y seguro

**Implicación:** Backlog futuro (2027+). Monitorear evolución normativa.

---

## 10. Requisitos Técnicos para Implementación InSoTech

### 10.1 Checklist de Pre-Requisitos

| # | Requisito | Estado | Módulo |
|---|-----------|--------|--------|
| R1 | SHA-384 para CUFE/CUDE | ⚠️ Verificar | `insotech_dian_wizard` |
| R2 | Redondeo Global activado | 📋 Documentar | Guía usuario |
| R3 | Firma XAdES-EPES con certificado ONAC | ✅ | `insotech_dian_wizard` |
| R4 | Pre-validación teléfonos (+57 + 10 dígitos) | 🟡 Pendiente | `insotech_l10n_co_advanced` |
| R5 | Identificación Simplificada (Comunicado 026) | 🟡 Ajustar | `insotech_l10n_co_advanced` |
| R6 | Código de Operación 04 (Contingencia Tipo 4) | 🟡 Pendiente | `insotech_l10n_co_advanced` |
| R7 | Alerta vencimiento certificado (90 días) | 🟡 Pendiente | `insotech_core` |
| R8 | Bloqueo NC/ND tras aceptación (irrevocabilidad) | 🟡 Pendiente | `insotech_radian` |
| R9 | Selector "vocación de circulación" en FE | 🟡 Pendiente | `insotech_radian` |

### 10.2 Modelo Comparativo Actualizado — Software Propio vs PT

| Dimensión | Alegra (Mandato) | Siigo/Loggro (PT) | **InSoTech (Software Propio)** |
|-----------|------------------|--------------------|-------------------------------|
| Firma Digital | Delegada (contrato mandato) | Certificado gestionado por usuario | **Certificado de Persona Jurídica directo** |
| Autonomía | Dependencia total del PT | Media; validaciones del PT | **Máxima; control total SOAP con DIAN** |
| Costos por folio | Incluido en plan (limitado) | $500-$2,000/folio | **$0 por folio** (amortización certificado) |
| Habilitación | Rápida bajo infra ajena | Trámites DIAN 3 días | **Automatización nativa en la nube** |
| Contingencia | Limitada | Limitada | **Tipo 3 + Tipo 4 completos** |
| RADIAN 2.0 ready | No | No | **Sí (arquitectura modular)** |


# <img src="https://www.insotech.it/favicon.ico" width="28"/> InSoTech — Facturación Electrónica DIAN para Odoo 19

[![Odoo 19](https://img.shields.io/badge/Odoo-19.0-blueviolet)](https://www.odoo.com)
[![Licencia: OPL-3](https://img.shields.io/badge/Licencia-OPL--3-red)](#licencia)
[![Autor: InSoTech](https://img.shields.io/badge/Autor-InSoTech-orange)](https://www.insotech.it)
[![Producción](https://img.shields.io/badge/Estado-Producción-brightgreen)](#)

**La solución más robusta** para facturación electrónica colombiana en Odoo 19.
Extiende la localización nativa (`l10n_co_dian`) con protecciones críticas que los contadores y gerentes de TI necesitan para operar con tranquilidad.

> *"Cada factura cuenta. Cada consecutivo importa. Cero huecos."*

---

## 🎯 ¿Por qué InSoTech?

La localización nativa de Odoo **no protege los consecutivos DIAN**. Si la DIAN rechaza una factura, el consecutivo se pierde — y con él, la integridad de tu resolución de numeración.

InSoTech resuelve esto y más:

### 🔒 Protección de Consecutivos DIAN
La funcionalidad #1 que ningún otro módulo ofrece:
- Las facturas se confirman con nombre temporal (`PRE-INV`) hasta ser aceptadas por la DIAN
- El consecutivo legal (`FE1`, `FE2`...) **solo se asigna tras validación exitosa**
- Si la DIAN rechaza → el consecutivo **no se consume**
- Resultado: **cero huecos** en tu resolución de numeración

### 🛡️ Tracking Inteligente de Consecutivos
Protección ante restauraciones de base de datos, migraciones y desastres:

| Capa | Protección | Ejemplo |
|:-:|---|---|
| 1 | **Persistencia automática** — Guarda el último consecutivo aceptado por la DIAN | Envías FE5 → se guarda `5`. Si restauras la BD, el sistema sabe que FE5 ya fue usado |
| 2 | **Bloqueo pre-envío** — Impide enviar un número que ya fue aceptado | Odoo intenta enviar FE3 pero FE5 ya fue aceptado → ❌ Bloqueado. Muestra: *"El siguiente disponible es FE6"* |
| 3 | **Detección + override manual** — Botón en el diario para escanear o configurar manualmente | Instalación nueva sin backup → Click "Detectar" → Escanea registros DIAN → Encuentra FE5 como último |

### ✅ Verificación DIAN con un Click
Botón "Verificar en DIAN" directamente en la factura:
- Abre el portal oficial de la DIAN con el CUFE de tu factura
- Confirma en segundos si la factura fue recibida correctamente
- Solo visible en facturas aceptadas — interfaz limpia

### 📊 Contador de Resolución en Tiempo Real
Visibilidad total del consumo de tu resolución:
- Muestra cuántos consecutivos has usado vs. autorizados
- Alertas automáticas cuando se acerca el límite
- Funciona con cualquier diario y prefijo (FE, NC, ND, DS...)

### 🔄 Reintentos Inteligentes
Si la DIAN rechaza tu factura:
- Botón "Reintentar Envío DIAN" — sin crear factura nueva
- Restauración automática del nombre temporal
- El consecutivo original se preserva para el reintento

### 📡 Eventos RADIAN — Control Total del Ciclo de Vida
La factura electrónica no termina cuando la DIAN la acepta. InSoTech gestiona los eventos RADIAN que convierten tu factura en un documento con pleno valor jurídico:

| Evento | Código | Descripción |
|:-:|:-:|---|
| Acuse de Recibo | 030 | Confirma que el receptor recibió la factura |
| Recibo de Bienes | 032 | Certifica que los bienes o servicios fueron entregados |
| Aceptación Expresa | 033 | El receptor acepta formalmente la factura |
| Aceptación Tácita | 034 | Se genera automáticamente cuando el receptor no responde en 3 días |
| Reclamo | 031 | El receptor rechaza la factura (con motivo DIAN) |

**¿Por qué importa?**
- Sin estos eventos, tu factura **no tiene "vocación de circulación"** — no es negociable como título valor
- Sin Aceptación (033/034), la factura **no es soporte válido** para costos, deducciones ni impuestos descontables
- Los competidores (Siigo, Alegra) ya lo ofrecen — RADIAN es el nuevo estándar de competencia

**Modo RADIAN configurable:**
- **Solo facturas marcadas** — Tú decides cuáles tienen vocación de circulación
- **Todas las facturas a crédito** — Generación automática para toda factura con plazo de pago
- **Desactivado** — Si no necesitas título valor

### 🔐 Monitoreo de Certificado Digital
Protección proactiva contra el bloqueo operativo más costoso: un certificado .p12 vencido.

| Nivel | Días restantes | Acción |
|:-:|:-:|---|
| 🟢 Aviso | ≤ 90 días | Notificación en el chatter de la empresa |
| 🟡 Advertencia | ≤ 30 días | "Programe la renovación" |
| 🔴 Crítico | ≤ 7 días | "Renueve URGENTEMENTE" |
| 🔴 Bloqueado | 0 días | "Facturación electrónica BLOQUEADA" |

- Verificación automática diaria (CRON)
- Fecha de vencimiento extraída directamente del .p12 — sin configuración manual
- Visible en **Ajustes → InSoTech** con contador de días en tiempo real

---

## 📦 Módulos Incluidos

| Módulo | Descripción |
|---|---|
| `insotech_l10n_co_advanced` | Motor principal de facturación electrónica DIAN con protección de consecutivos |
| `insotech_dian_wizard` | Habilitación DIAN directa, firma XAdES-BES, generación UBL 2.1 y eventos RADIAN |
| `insotech_core` | Licenciamiento SaaS con validación centralizada y período de gracia 72h |

---

## 🏗️ Compatibilidad

| Plataforma | Soporte |
|---|:-:|
| Odoo.sh (Enterprise) | ✅ |
| Odoo On-Premise (Enterprise) | ✅ |
| Odoo 19.0 | ✅ Desarrollo activo |
| Odoo 18.0 | ⏳ Port planificado |

> **Requisito**: Odoo Enterprise con localización colombiana (`l10n_co_dian`).

---

## 🚀 Instalación

Consulta la guía detallada para todos los entornos:

📄 [`GUIA_DESPLIEGUE.md`](Documentacion/insotech_l10n_co_advanced/GUIA_DESPLIEGUE.md)

---

## 📜 Licencia

**OPL-3** (Odoo Proprietary License v3)

© 2026 **INFINITY SOLUTIONS TECHNOLOGY S.A.S (InSoTech)**. Todos los derechos reservados.

Este software es propiedad exclusiva de InSoTech. No está permitida su redistribución, modificación o uso sin licencia válida. El uso de este software requiere una suscripción activa con InSoTech.

Odoo® es una marca registrada de Odoo S.A. Este módulo **no es desarrollado, mantenido ni respaldado por Odoo S.A.**

---

## 📞 Contacto

🌐 [www.insotech.it](https://www.insotech.it)  
📧 soporte@insotech.it  
🇨🇴 Colombia

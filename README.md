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

### 🧠 Diagnóstico Inteligente de Errores (¡Adiós XML crudos!)
Siigo y Alegra te dicen exactamente qué salió mal. Odoo nativo lanza códigos XML incomprensibles. InSoTech incorpora un **Traductor Inteligente de Errores DIAN**:
- Si el NIT del cliente no existe en el RUT, no verás un "Error 401"; verás un banner rojo que dice: *"El NIT del cliente no existe o fue cancelado."*
- Validación pre-envío de responsabilidades fiscales. Ahorra cientos de horas de soporte financiero y frustración contable.

### 📄 Rediseño B2B: Transformación de PDF a "Título Valor" Legal
Odoo nativo imprime facturas contables europeas, no exigibles legalmente en Colombia. Nosotros re-escribimos el corazón de `report_invoice_document` para que tu empresa expida un **Título Valor 100% Legal y Endosable (Artículos 621 y 774 del Código de Comercio)**:
- **Inyección Automática de Monto en Letras** ("SON: UN MILLON DE PESOS M/CTE"). Obligatorio para evitar nulidades judiciales.
- El PDF expone elegantemente el código QR DIAN, el CUFE, e inyecta la referencia de la Firma Digital Autónoma y la resolución.
- Expone claramente el domicilio de notificación deudor y las referencias bancarias de pago. Todo bajo el marco estético Bootstrap del cliente corporativo premium.

### 🔄 Reintentos Inteligentes
Si la DIAN rechaza tu factura:
- Botón "Reintentar Envío DIAN" — sin crear una factura nueva de cero.
- Restauración automática del nombre temporal (`PRE-INV`) en tiempo real.
- El consecutivo legal original permanece protegido y sellado bajo nuestro test 5-way CI/CD. Cero saltos.

### 🌐 Portal RADIAN 360 Interactívo (Sin Login Friccional)
La factura electrónica no termina cuando la DIAN la acepta, apenas comienza. Hemos emancipado Odoo del pesado y limitante portal nativo ("Tiene que iniciar sesión para...").
- **Portal URL Público Blindado:** Tu cliente entra directamente desde un link en el correo, ve su Título Valor e interactúa.
- **Firma a Ruego Automática:** Un checkbox de Mandato Legal obliga al deudor a aceptar sus términos corporativos. InSoTech captura su IP, emite el Hash Criptográfico, y registra el mandato al instante.
- **Cero Comisiones por Evento:** Aceptación Expresa (033), Acuse de Recibo (030) y Reclamos (031) se envían hacia Bogotá en formato UBL 2.1 vía **SOAP Directo (Bypassing IAP)**. Cero caídas, cero tokens de compra en Odoo.
- **Bloqueo Inteligente Anti-Factoring:** Si tu factura es endosada (Eventos 037/038), InSoTech elimina automáticamente el botón nativo de de "Pre-Pago", previniendo catástrofes de recaudo doble.

### 🔐 Monitoreo de Certificado Digital
Protección proactiva contra el bloqueo operativo más costoso (Un certificado .p12 vencido).
- Notifica 90 días antes, alerta 30 días antes, y **BLOQUEA por seguridad** el día 0.
- Cron automático evalúa diariamente tu bóveda criptográfica.

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

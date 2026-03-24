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
- **Capa 1**: Persistencia automática del último consecutivo aceptado
- **Capa 2**: Bloqueo pre-envío de duplicados — imposible enviar un número ya usado
- **Capa 3**: Botón de detección automática + override manual en el diario

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

---

## 📦 Módulos Incluidos

| Módulo | Descripción |
|---|---|
| `insotech_l10n_co_advanced` | Motor principal de facturación electrónica DIAN con protección de consecutivos |
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

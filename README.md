# <img src="https://www.insotech.it/favicon.ico" width="28"/> InSoTech — Localización Colombiana Avanzada para Odoo

[![Odoo 18](https://img.shields.io/badge/Odoo-18.0-blueviolet)](https://www.odoo.com)
[![Odoo 19](https://img.shields.io/badge/Odoo-19.0-blueviolet)](https://www.odoo.com)
[![Licencia: OPL-3](https://img.shields.io/badge/Licencia-OPL--3-red)](#licencia)
[![Autor: InSoTech](https://img.shields.io/badge/Autor-InSoTech-orange)](https://www.insotech.it)
[![Producción](https://img.shields.io/badge/Estado-Producción-brightgreen)](#)

**La suite más completa** de facturación electrónica colombiana para Odoo.
Extiende la localización nativa (`l10n_co_dian`) con protecciones críticas, un POS profesional y herramientas que los contadores y gerentes de TI necesitan para operar con tranquilidad.

> *"Cada factura cuenta. Cada consecutivo importa. Cero huecos."*

---

## 📦 Módulos Incluidos

| Módulo | Descripción |
|---|---|
| `insotech_l10n_co_advanced` | Motor principal: facturación electrónica DIAN con protección de consecutivos, diagnóstico inteligente y PDF Título Valor |
| `insotech_l10n_co_pos` | **Punto de Venta profesional** con facturación electrónica DIAN integrada |
| `insotech_dian_wizard` | Habilitación DIAN directa, firma XAdES-BES, generación UBL 2.1 y eventos RADIAN |
| `insotech_core` | Licenciamiento SaaS con validación centralizada |

---

## 🛒 Punto de Venta — Facturación Electrónica DIAN

**El único módulo POS para Odoo que integra facturación electrónica colombiana directamente en la tirilla de compra.**

### ¿Cómo funciona?

El cajero decide en cada venta si genera **Factura Electrónica** o un **Comprobante de Venta**. Un solo checkbox: `Recibo/Factura`.

| Recibo/Factura | Resultado |
|:-:|---|
| ✅ Activado | **Factura Electrónica de Venta** — Se envía a la DIAN, incluye CUFE, QR y consecutivo fiscal |
| ❌ Desactivado | **Comprobante de Venta** — Tirilla profesional sin reporte DIAN |

### ✨ Tirilla Profesional

Diseñada para impresoras térmicas con estándar colombiano:

```
        ╔══════════════════════════════╗
        ║    [LOGO DE LA EMPRESA]      ║
        ║      MI EMPRESA S.A.S.       ║
        ║    NIT: 901.234.567-8        ║
        ║  CRA 25 # 3-45, MEDELLÍN    ║
        ║  Tel: 316-468-2413           ║
        ╠══════════════════════════════╣
        ║  Factura Electrónica de Venta║
        ║       No. FE2574            ║
        ║       Orden: 109            ║
        ╠══════════════════════════════╣
        ║  Fecha: 17-06-2026 20:47    ║
        ║  Forma de pago: Contado     ║
        ║  Medio de Pago: Efectivo    ║
        ╠══════════════════════════════╣
        ║  Cliente: AMELIA COFFEE      ║
        ║  NIT: 901639098-3           ║
        ║  Tel: 316-468-2413          ║
        ║  Dir: CRA 25 # 3-45        ║
        ╠══════════════════════════════╣
        ║  Descripción          Valor  ║
        ║                              ║
        ║  Café Latte        $12.000   ║
        ║  Croissant          $8.500   ║
        ║                              ║
        ║  Subtotal          $20.500   ║
        ║  IVA 19%            $3.895   ║
        ║  TOTAL             $24.395   ║
        ║  EFECTIVO          $25.000   ║
        ║  CAMBIO               $605   ║
        ╠══════════════════════════════╣
        ║  No somos Grandes            ║
        ║  Contribuyentes, R-99-PN     ║
        ║  No responsable de IVA       ║
        ║                              ║
        ║  Resolución DIAN:            ║
        ║  18764107493338 del          ║
        ║  2026-03-21 al 2028-03-21   ║
        ║                              ║
        ║  Act. Económica: 5611        ║
        ║                              ║
        ║         [QR DIAN]            ║
        ║                              ║
        ║  CUFE:                       ║
        ║  a1b2c3d4e5f6...             ║
        ╠══════════════════════════════╣
        ║  Implementado por InSoTech   ║
        ╚══════════════════════════════╝
```

### 🎯 Funcionalidades del POS

| Feature | Detalle |
|---|---|
| **Consecutivo fiscal compartido** | Usa el mismo diario de ventas que el módulo Contabilidad — si facturas desde POS o desde Ventas, el consecutivo es uno solo (FE2574, FE2575...) |
| **Orden / Turnero** | Número de orden visible para gestión de turnos en el mostrador |
| **Datos del cliente DIAN** | NIT, tipo de documento, dirección, teléfono, email |
| **Consumidor Final** | Si no se asigna cliente, se usa "Consumidor Final" automáticamente |
| **Forma y medio de pago** | Detecta automáticamente: Efectivo, Transferencia, Nequi, Daviplata, TC |
| **Desglose de impuestos** | IVA (0%, 5%, 19%), INC (8%, 16%), y cualquier otro impuesto configurado |
| **Resolución DIAN** | Lee la resolución directamente del diario de ventas |
| **Responsabilidades fiscales** | Gran Contribuyente, régimen IVA, obligaciones |
| **Actividad económica** | Código CIIU de la empresa |
| **CUFE** | Código Único de Facturación Electrónica (solo en FE) |
| **QR DIAN** | Código QR verificable en el portal DIAN (solo en FE) |
| **Compatible con cualquier Odoo 18** | Enterprise y Community — se adapta automáticamente |

### 🔌 Instalación Independiente

`insotech_l10n_co_pos` funciona de forma **independiente**:

| Escenario | Resultado |
|---|---|
| POS solo (sin advanced) | ✅ Tirilla profesional con datos empresa e impuestos |
| POS + advanced | ✅ Todo + resolución DIAN, CUFE, QR, envío automático |
| Advanced solo (sin POS) | ✅ Facturación electrónica desde Ventas/Contabilidad |

---

## 🔒 Facturación Electrónica — Protección de Consecutivos DIAN

La funcionalidad #1 que ningún otro módulo ofrece:

- Las facturas se confirman con nombre temporal (`PRE-INV`) hasta ser aceptadas por la DIAN
- El consecutivo legal (`FE1`, `FE2`...) **solo se asigna tras validación exitosa**
- Si la DIAN rechaza → el consecutivo **no se consume**
- Resultado: **cero huecos** en tu resolución de numeración

### 🛡️ Tracking Inteligente de Consecutivos

Protección ante restauraciones de base de datos, migraciones y desastres:

| Capa | Protección | Ejemplo |
|:-:|---|---|
| 1 | **Persistencia automática** — Guarda el último consecutivo aceptado | Envías FE5 → se guarda `5`. Si restauras la BD, sabe que FE5 ya fue usado |
| 2 | **Bloqueo pre-envío** — Impide enviar un número ya aceptado | Odoo intenta FE3 pero FE5 ya fue aceptado → ❌ Bloqueado |
| 3 | **Detección + override manual** — Botón en el diario para escanear | Instalación nueva → Click "Detectar" → Escanea DIAN → Encuentra FE5 |

---

## ✅ Verificación DIAN con un Click

Botón "Verificar en DIAN" directamente en la factura:
- Abre el portal oficial de la DIAN con el CUFE de tu factura
- Confirma en segundos si fue recibida correctamente
- Solo visible en facturas aceptadas — interfaz limpia

---

## 📊 Contador de Resolución en Tiempo Real

- Muestra cuántos consecutivos has usado vs. autorizados
- Alertas automáticas cuando se acerca el límite
- Funciona con cualquier diario y prefijo (FE, NC, ND, DS...)

---

## 🧠 Diagnóstico Inteligente de Errores DIAN

Siigo y Alegra te dicen exactamente qué salió mal. Odoo nativo lanza códigos XML incomprensibles. InSoTech traduce:

- NIT inexistente → *"El NIT del cliente no existe o fue cancelado."*
- Responsabilidad fiscal incorrecta → Mensaje claro con la corrección
- Validación pre-envío que ahorra horas de soporte

---

## 📄 PDF Título Valor Legal

Odoo nativo imprime facturas contables europeas. InSoTech genera un **Título Valor 100% Legal y Endosable** (Art. 621 y 774 del Código de Comercio):

- **Monto en letras** automático ("SON: UN MILLÓN DE PESOS M/CTE")
- QR DIAN, CUFE y firma digital
- Domicilio de notificación y referencias bancarias
- Diseño corporativo premium

---

## 🔄 Reintentos Inteligentes

Si la DIAN rechaza tu factura:
- Botón **"Reintentar Envío DIAN"** — sin crear factura nueva
- Restauración automática del nombre temporal (`PRE-INV`)
- El consecutivo original permanece protegido

---

## 🌐 Portal RADIAN 360 Interactivo

La factura electrónica no termina cuando la DIAN la acepta:

- **Portal URL público** — Tu cliente accede sin login
- **Firma a ruego automática** — Captura IP y hash criptográfico
- **Eventos RADIAN** — Aceptación (033), Acuse (030) y Reclamos (031) vía SOAP directo
- **Bloqueo anti-factoring** — Si la factura es endosada, bloquea el pago duplicado

---

## 🔐 Monitoreo de Certificado Digital

- Notifica **90 días antes** del vencimiento
- Alerta **30 días antes**
- **Bloquea** el día 0 por seguridad
- Cron automático diario

---

## 🗺️ Códigos Postales Colombianos

Base de datos completa de **1,123 municipios** colombianos con códigos postales DANE:
- Se cargan automáticamente al instalar el módulo
- Actualizados según la codificación oficial del DANE
- Integrados con `res.city` para formularios de contactos y facturación

---

## 🏗️ Compatibilidad

| Plataforma | Soporte |
|---|:-:|
| Odoo.sh (Enterprise) | ✅ |
| Odoo On-Premise (Enterprise) | ✅ |
| Odoo Community (POS) | ✅ |
| Odoo 18.0 | ✅ Desarrollo activo |
| Odoo 19.0 | ✅ Desarrollo activo |

> **Nota**: La facturación electrónica DIAN requiere Odoo Enterprise con `l10n_co_dian`. El módulo POS funciona también en Community con funcionalidades adaptadas.

---

## 🚀 Instalación

1. Clona este repositorio en tu directorio de addons
2. Actualiza la lista de aplicaciones en Odoo
3. Instala los módulos que necesites:
   - `insotech_l10n_co_advanced` — Facturación electrónica
   - `insotech_l10n_co_pos` — Punto de Venta

> 📄 Consulta la guía detallada: [`GUIA_DESPLIEGUE.md`](Documentacion/insotech_l10n_co_advanced/GUIA_DESPLIEGUE.md)

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

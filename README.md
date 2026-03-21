# Insotech — Localización Colombiana Avanzada para Odoo

[![Odoo 19](https://img.shields.io/badge/Odoo-19.0-blueviolet)](https://www.odoo.com)
[![Licencia: OPL-1](https://img.shields.io/badge/Licencia-OPL--1-red)](https://www.odoo.com/documentation/19.0/legal/licenses.html)
[![Autor: Insotech](https://img.shields.io/badge/Autor-Insotech-orange)](https://www.insotech.it)

Repositorio de **módulos comerciales de Insotech** para la localización colombiana avanzada en Odoo 19 (con port futuro a 18).

Resuelve las limitaciones críticas de la localización nativa (`l10n_co`):

- 🔒 **Protección de consecutivos de resolución DIAN** — Cero huecos por rechazos: la secuencia legal solo se consume tras validación exitosa.
- 🛡️ **Motor de licenciamiento SaaS** — Validación centralizada con período de gracia de 72 horas ante fallos de conectividad.
- 🔍 **Autocompletado de RUT/NIT** — Consulta automática de datos tributarios *(futuro)*.

---

## Módulos

| Módulo | Estado | Descripción |
|---|---|---|
| `insotech_core` | ✅ Disponible | Motor de licenciamiento SaaS |
| `insotech_l10n_co_advanced` | 🚧 En desarrollo | Facturación electrónica DIAN segura |

---

## Versiones Soportadas

| Versión Odoo | Estado |
|---|---|
| 19.0 | ✅ Desarrollo activo |
| 18.0 | ⏳ Port planificado |

---

## Instalación

Consulta la guía detallada de instalación para todos los entornos (Odoo.sh, On-Premise, Docker) en:

📄 [`Documentacion/insotech_core/GUIA_DESPLIEGUE.md`](Documentacion/insotech_core/GUIA_DESPLIEGUE.md)

---

## Licencia

**OPL-1** (Odoo Proprietary License v1.0)

Todos los derechos reservados por **Insotech**.

---

## Contacto

🌐 [www.insotech.it](https://www.insotech.it)

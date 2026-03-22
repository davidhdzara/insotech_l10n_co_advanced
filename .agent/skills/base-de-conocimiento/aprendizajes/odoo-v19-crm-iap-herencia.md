---
title: "Secuestro de Vistas (Hijacking) en Odoo V19: CRM IAP Lead Mining"
date: "2026-03-06"
description: "Lecciones documentadas sobre herencia de vistas, nombres de módulos cambiantes y validaciones estandarizadas de campos en Odoo V19."
---

# Aprendizajes: Herencia B2B del Wizard CRM Generador de Leads (Odoo V19)

Al intentar interceptar ("Hijacking") el wizard nativo de generación de prospectos de Odoo (`crm_iap_lead_mining_request`) para inyectar nuestra propia fuente B2B de Datos Abiertos (SECOP), se descubrieron diferencias arquitectónicas clave en **Odoo V19** respecto a versiones anteriores.

## 1. El Módulo Real de IAP B2B en V19 cambió de Nombre

**El Error:**
Asumimos por inercia que el módulo base que controla el recuadro de *Generate Leads* en el CRM se llamaba `crm_iap_lead`. Por consiguiente, nuestro XML tenía:
```xml
<field name="inherit_id" ref="crm_iap_lead.crm_iap_lead_mining_request_view_form"/>
```
Esto causó que Odoo **ignorara silenciosamente** nuestro XML, porque el ID base no existía, saltando cualquier Traceback pero sin mostrar nuestros cambios B2B.

**La Solución Estricta (Odoo V19):**
El módulo encargado del *lead mining* en Odoo V19 es `crm_iap_mine`. Por lo tanto, tanto en el `__manifest__.py` (dependencias) como en el identificador de herencia (XML), se debe apuntar al ID Externo exacto verificado desde *Ajustes > Técnico > Vistas*.

```xml
<!-- LO CORRECTO -->
<field name="inherit_id" ref="crm_iap_mine.crm_iap_lead_mining_request_view_form"/>
```

## 2. El Peligro de Ocultar Campos Obligatorios Nativos (`Missing required fields`)

**El Error:**
Para limpiar la ventana visualmente y transformarla en una interfaz exclusiva de SECOP, usamos atributos `invisible="1"` para ocultar los grupos nativos (ej. "How many leads would you like?" o los campos de Países e Industrias). Todo pintó bien hasta que el usuario hizo click en *Submit*.

Odoo arrojó el error **"Missing required fields"**. 
Ocurre porque campos como `country_ids` o `industry_ids` están declarados como `required="1"` tanto a nivel Python como a nivel XML original. Aunque Odoo *no los muestre* en pantalla producto de la regla de visibilidad, el validador del formulario *sigue esperando datos para esos campos* obligatorios.

**La Solución (Atributos Dinámicos):**
Para quitarle el peso obligatorio a un campo nativo en Odoo sin desestabilizar el backend para otros usuarios que sí usen IAP, la regla `required` debe ser evaluada lógicamente en el XML. En lugar de esconder a los padres en grupos generales, se debe inyectar temporalmente una regla que "apague" la obligatoriedad.

```xml
<!-- Inyectando la limpieza de validación -->
<xpath expr="//field[@name='country_ids']" position="attributes">
    <attribute name="required">insotech_lead_source == 'odoo_iap'</attribute>
</xpath>
<xpath expr="//field[@name='industry_ids']" position="attributes">
    <attribute name="required">insotech_lead_source == 'odoo_iap'</attribute>
</xpath>
```
Esta es la forma maestra de hacer *Hijacking* seguro: inyectar dependencias y no romper el flujo nativo para las interfaces compartidas por otros módulos.

---
**Directiva para futuros agentes:** No intentes adivinar IDs de herencia en Odoo V19. Usa siempre el entorno real para extraer la arquitectura (Paso 3, Metodología de Depuración) y recuerda desactivar el *requirement* si procedes a ocultar campos que tradicionalmente el fabricante consideró vitales.

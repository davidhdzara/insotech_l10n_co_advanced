# Plan Estratégico para una Localización Colombiana TOP en Odoo 18

Para potenciar este desarrollo y llevar la localización de Odoo 18 en Guapante a un nivel "TOP nacional" (compitiendo de tú a tú con jugadores súper maduros como Loggro, Siigo, Alegra o los antiguos Helisa/Siesa), necesitamos pasar de una postura reactiva y manual a una altamente **automatizada, preventiva y orientada a la experiencia del contador y auxiliar**.

A continuación, detallo los insumos exactos que necesito de ti (como líder funcional y de negocio) para que estructuremos este plan de trabajo y arranquemos con la etapa de diseño técnico y desarrollo:

## Fase 1: Insumos de Integración y Datos Maestros

Para resolver el problema #1 (Consulta de RUT/RUES automatizada) necesitamos poder conectarnos a bases de datos confiables en Colombia.

**Insumos Requeridos de tu parte:**
1.  **¿Tienes o podemos adquirir una API Key de consulta de la DIAN o RUES?** Existen proveedores en Colombia (como *DataCrédito Experian*, *RUES (Cámaras de Comercio)*, o APIs de validación privadas de terceros ej. *API Colombia*) que, con un NIT, entregan el JSON con la Razón Social, Dirección, Actividades CIIU y Códigos de Responsabilidad (RUT). Necesito saber a qué API nos conectaremos para construir el desarrollo en Odoo.
2.  **Lógica del Dígito de Verificación (DV):** Aunque Odoo lo calcula, a veces la fórmula del módulo base suele fallar con NITs atípicos. Necesito que me confirmes si usamos la fórmula estándar Módulo 11 de la DIAN o si has notado fallas que reportan los usuarios para re-escribir ese fragmento de código.

## Fase 2: Control Estricto de Resoluciones de Facturación DIAN

Para resolver el lío de facturas con "huecos" u "órdenes borrador":

**Insumos Requeridos de tu parte:**
1.  **Definición de Proceso (UX Contable):** Odoo reserva el número contable al *confirmar* la factura. Si la vamos a retener en un estado "Enviando a DIAN" antes de asignar número legal: ¿Cómo quieres que se vea en el sistema? ¿Creamos una secuencia transitoria (ej. `PRE-INV/2026/01`) que luego mute al prefijo final (ej. `FE-881`) una vez el XML devuelva OK?
2.  **Manejo de Casos de Falla:** Si la DIAN está caída (lo cual pasa a menudo), ¿Permitiremos "Facturación de Contingencia" (papel) con una secuencia diferente? Odoo no maneja muy bien esto nativamente. Necesito la directriz de negocio: ¿Esperamos, forzamos reintento en cron de 10 min, o dejamos al usuario pasar a contingencia?

## Fase 3: Cálculo y Acumulado de Retenciones

Este es un agujero negro en Odoo estándar que causa multas si se hace mal.

**Insumos Requeridos de tu parte:**
1.  **Tabla Maestra de Retenciones (La Verdad Absoluta):** Necesito un documento o directriz de tu contador principal con:
    *   Tarifas actuales (ReteFuente, ReteICA, ReteIVA).
    *   Bases Mínimas (UVT actualizadas 2026).
    *   Regla de Acumulación: ¿Vamos a desarrollar un algoritmo en Odoo que acumule las compras del *mes* de un proveedor para saber si superó la base? ¿O asumimos el cálculo transacción por transacción?
2.  **Manejo de ReteICA:** El ICA es municipal en Colombia. ¿Guapante opera de manera multi-municipal exigiendo diferentes tarifas de ReteICA según la ciudad de expedición, o unificamos la retención a la sede principal de Bogotá/Medellín?

## Fase 4: Conciliación, Cuentas de Cobro y Documentos Soporte

**Insumos Requeridos de tu parte:**
1.  **Flujo con Proveedores "Informales":** Para las cuentas de cobro de personas naturales no responsables de IVA (donde Guapante genera el Documento Soporte). ¿Los proveedores envían un portal, o el contador las digitaliza? Necesito definir si desarrollamos un "Portal del Proveedor" en Odoo para que la persona suba su cuenta de cobro y Odoo arme el Documento Soporte automáticamente.
2.  **El problema del flujo de Anticipos:** Ciertos anticipos en Colombia generan causación de impuestos. ¿Guapante tiene esta figura frecuentemente o podemos mantener el cruce contable sencillo estándar de Odoo?

---

### Siguiente Paso
Si me consolidas las respuestas (o decidimos ir investigando punto a punto), **diseñaremos un módulo a la medida (`guapante_l10n_co_advanced`)** que inyectaremos en la instalación de Odoo.sh para sobrescribir las fallas nativas, dándole a los usuarios una experiencia automatizada y a prueba de errores de la DIAN.

¿Por qué fase te gustaría que prioricemos la recolección de esta información?

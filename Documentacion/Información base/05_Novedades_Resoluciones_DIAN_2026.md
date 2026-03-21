# Novedades y Resoluciones DIAN (Proyección 2025/2026)

Este documento recopila las actualizaciones normativas más recientes emitidas por la DIAN (Resolución 000202, proyecto de resolución Feb 2025 y Concepto 0158 de Ene 2026) que impactan directamente el desarrollo de la Localización Avanzada de Insotech en Odoo 19.

## 1. Simplificación de Datos del Adquiriente (Autocompletado NIT)
La DIAN, buscando agilizar las transacciones en mostrador y facturación rápida, ha emitido normativas que limitan a **máximo 3** los datos exigibles obligatoriamente al comprador para emitir una factura electrónica válida:
- Nombre o Razón Social
- Tipo y Número de Identificación (NIT / CC)
- Correo Electrónico (Solo si la entrega de la representación gráfica es digital)

**Impacto Técnico en Odoo:** Esto vuelve imperativo contar con un mecanismo tecnológico que, al ingresar el NIT del cliente, se conecte automáticamente al RUT (vía API RUES, DIAN o API Colombia) para autocompletar la Razón Social y las responsabilidades tributarias. Odoo nativo no posee esto de forma consistente para la creación de Contactos en el Back-End, por lo que el módulo `insotech_l10n_co_advanced` deberá cubrir esta brecha en la Fase 3 del proyecto.

## 2. Flexibilidad y Control del "Documento Soporte" (Concepto 0158 - Enero 2026)
Se actualizaron las reglas concernientes a la deducibilidad de gastos sustentados en Documentos Soporte en Adquisiciones a No Obligados a Facturar (DSNO). 
Se permite que los Documentos Soporte expedidos en el año fiscal *siguiente* a la causación del gasto sigan siendo válidos para la deducción en renta, **siempre y cuando el contribuyente demuestre que el devengo del gasto originario sí ocurrió en el año correspondiente**.

**Impacto Técnico en Odoo:** La localización de Insotech deberá permitir la causación contable de un gasto en una fecha de cierre (ej. 31 Dic 2025) y la posterior transmisión asíncrona del XML del Documento Soporte a la DIAN en otra fecha (ej. 15 Ene 2026), sin generar rechazos por "Desfase de fechas", manteniendo la sincronía estricta de periodos fiscales en los Diarios de Compra.

## 3. Emisiones Diferidas y Facturación en Lote
Para empresas del sector servicios o comercio con barreras tecnológicas momentáneas, la DIAN autoriza ventanas ampliadas de hasta 48 horas para generar el documento equivalente electrónico en caso de fallas comprobadas (contingencia).
Aunque este caso de uso varía según el sector, ratifica la necesidad de la funcionalidad comercial de **"Envíos por Lote Diferido"** (Mass DIAN Sending), que se implementará evitando la saturación del Cron y cediendo el control manual al contador.

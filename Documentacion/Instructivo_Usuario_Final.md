# Instructivo de Usuario: Facturación Electrónica Insotech Avanzada (Odoo 19)

Este módulo optimiza la facturación electrónica nativa de Odoo para evitar que se pierdan o "quemen" números de resolución (consecutivos) cuando la DIAN rechaza una factura debido a errores (ej. NIT inválido, correo mal formado).

## 1. Configuración Inicial (Resoluciones DIAN)
1. Active el "Modo Desarrollador" en Odoo.
2. Diríjase a **Contabilidad > Configuración > Diarios Contables**.
3. Seleccione su Diario de Ventas (Facturas de cliente).
4. En la pestaña de **Facturación Electrónica (DIAN)**, verá un nuevo campo llamado "Asignación Diferida de Secuencia DIAN". Actívelo.

## 2. Flujo de Facturación (Sin saltos de numeración)
En el flujo estándar, Odoo gastaría un número `FE-0001` al enviar la factura. Si la factura es rechazada, ese `FE-0001` se pierde internamente en Odoo. Con Insotech Advanced, el flujo es el siguiente:

1. **Creación de Borrador:** Cree su factura de cliente normalmente.
2. **Confirmar Factura:** Al confirmar, Odoo asienta la contabilidad pero **NO gasta el consecutivo legal de la DIAN**. La factura quedará con el código temporal `Pendiente-DIAN/2026/...`.
3. **Procesar/Enviar a la DIAN:** Al hacer clic en "Procesar", el módulo enviará el XML de validación. 
    * **Si la DIAN Acepta:** Automáticamente la factura adquirirá su número oficial (ej. `FE-0001`).
    * **Si la DIAN Rechaza:** La factura continuará en estado temporal. Podrá corregir el error (ej. arreglar el de la ciudad del cliente) y volver a procesarla sin haber perdido ningún consecutivo oficial.

## 3. Contingencias (Caídas de la DIAN)
El módulo provee un sistema seguro. Si MUISCA está offline, las facturas quedarán en estado asíncrono temporal. El CRON automático del sistema se encargará de realizar reintentos cada 15 minutos hasta lograr registrar oficialemente la factura en la DIAN.

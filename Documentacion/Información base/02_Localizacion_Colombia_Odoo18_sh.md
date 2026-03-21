# Localización Colombiana y Facturación Electrónica en Odoo 18 (Odoo.sh)

## 1. Visión General de la Localización Colombiana (`l10n_co`)
Odoo 18 cuenta con un soporte robusto y nativo para la localización colombiana, cumpliendo con los requerimientos contables, legales y fiscales establecidos por la Dirección de Impuestos y Aduanas Nacionales (DIAN). El paquete de localización base incluye:

*   **Plan Único de Cuentas (PUC):** Árbol de cuentas adaptado a la normatividad contable local pre-configurado para despliegue rápido.
*   **Impuestos y Retenciones:** Configuración predeterminada de IVA, Retefuente, ReteICA, ReteIVA con sus respectivas bases mínimas y porcentajes según legislación vigente.
*   **Posiciones Fiscales (Mapeo de Impuestos):** Reglas automatizadas para la correcta aplicación de impuestos dependientes del tipo de contribuyente (Gran Contribuyente, Régimen Común/Responsable de IVA, Régimen Simplificado/No Responsable, etc.).
*   **Estructura de Identificación:** Incorporación de campos nativos para manejo del RUT, Tipo de Documento (NIT, CC, CE, Pasaporte) y cálculo automático del Dígito de Verificación.

## 2. Facturación Electrónica DIAN: Modalidad "Software Propio"
Uno de los avances y ventajas más importantes de Odoo Enterprise 18 es la posibilidad de realizar integración **directa** con la DIAN bajo la modalidad de **"Software Propio"**, eliminando la obligación de pagar un Proveedor Tecnológico externo (como Carvajal, Cadena o FacturaTech), aunque esta opción de integración externa sigue disponible si la empresa así lo desea.

### Módulos Clave
Esta robustez es entregada mediante la instalación de los módulos principales:
*   `l10n_co_edi`: Estructura para Intercambio Electrónico de Datos (EDI) para Colombia.
*   `l10n_co_dian`: El conector directo que convierte a Odoo en un emisor directo frente a los web services de la DIAN.

### Características Principales del Proceso de Facturación
1.  **Generación de XML a la Medida:** Odoo reúne la data transaccional y crea automáticamente el archivo estructurado XML (estándar UBL 2.1) exigido por la DIAN.
2.  **Firmado Digital Interno:** El XML se firma electrónicamente dentro del propio Odoo utilizando un certificado digital configurado por el usuario.
3.  **Generación de CUFE y Código QR:** Asignación en tiempo real del Código Único de Factura Electrónica (CUFE) o CUDE y estampillado del Código QR dentro del formato PDF (Representación Gráfica).
4.  **Validación Previa Oficial:** Los documentos son enviados automáticamente al servicio web de la DIAN y Odoo registra el *ApplicationResponse* devolviendo un estado de "Aceptado" o "Rechazado", incluyendo el PDF firmado de validación DIAN.
5.  **Envío al Adquiriente:** Generación automática del archivo ZIP que contiene el XML de la factura, el ApplicationResponse de la DIAN y el PDF con representación gráfica y QR, el cual se envía por correo al cliente.

### Tipos de Documentos Soportados Nativamente
*   Factura de Venta Electrónica Nacional y de Exportación.
*   Notas Crédito y Notas Débito Electrónicas.
*   Documento Soporte en Adquisiciones a sujetos No Obligados a Facturar.
*   Acuses de recibo para Facturación de Proveedores (Eventos Título Valor: Acuse de recibo, Recibo del Bien/Servicio, Aceptación).

## 3. Requisitos de Configuración para Emisión Directa (DIAN)
Para utilizar Odoo como "Software Propio" ante la DIAN, se debe completar una serie de requisitos y configuraciones tanto legales como de sistema:

1.  **Registro Único Tributario (RUT):** La empresa debe encontrarse activa y con las responsabilidades tributarias correctas (ej: Obligado a facturar electrónicamente, Impuesto sobre las ventas - IVA, etc.).
2.  **Certificado de Firma Digital (`.p12`):** Es imprescindible adquirir una firma digital de un ente certificador avalado por la ONAC (ej. GSE, Certicámara, Andes, etc.). Odoo requiere que se cargue este archivo P12 para firmar todos los paquetes enviados.
3.  **Proceso de Habilitación en Muisca DIAN:**
    *   Ingresar al portal de habilitación de la DIAN y registrar la compañía.
    *   Seleccionar el modo de operación **"Software Propio"**.
    *   Obtener el `Test Set ID` (Identificador del Set de Pruebas), el `Software ID` y el `Software PIN`. Estos datos se configuran dentro de Odoo.
    *   Enviar desde Odoo el "Set de Pruebas" requerido por la DIAN (generalmente un set de varias facturas, notas débito y crédito) que demuestren que los XMLs emitidos no tienen errores de estructura ni de cálculos matemáticos.
4.  **Paso a Producción y Resolución:** Una vez la empresa supera exitosamente las pruebas, se autoriza el paso a Producción, donde se hace solicitud de los rangos de Resolución de Facturación, se asocian sus prefijos y claves técnicas en la web de la DIAN, para proceder luego a plasmarlos en los "Diarios" contables de Odoo.

## 4. Particularidades y Beneficios en el Entorno Odoo.sh
**Odoo.sh** es la oferta de Plataforma como Servicio (PaaS) en la nube gestionada específicamente para Odoo Enterprise. El hecho de estar hospedado en este entorno no limita en lo absoluto, sino que mejora la operación de la localización:

*   **Seguridad de Certificados:** Odoo almacena de manera encriptada y segura de lado del servidor el certificado `.p12` subido para evitar filtraciones de una credencial de alto riesgo legal.
*   **Entornos Aislados de Staging para el "Set de Pruebas":** Uno de los procesos más delicados es enviar facturas de prueba a la DIAN. Odoo.sh permite crear entornos de *Staging* completos aislados, donde se configuran los credenciales de "Habilitación DIAN". Se puede emitir toda la basura necesaria de prueba y, una vez certificado, pasar los ajustes limpios de configuración general a Producción sin haber contaminado la serie contable productiva.
*   **Cron Jobs Confiables (Tareas Programadas):** En Colombia, es bastante común observar lentitud, fallos o mantenimientos en el servicio web oficial de la DIAN Muisca. En estos casos, las facturas en Odoo quedan en estado "Procesando de manera asíncrona". Un entorno sólido como Odoo.sh garantiza que la tarea cron de chequeo recurrente "Consultar estado de Documentos Electrónicos EDI" corra eficientemente hasta que consiga comunicarse con la DIAN y asiente la validación.

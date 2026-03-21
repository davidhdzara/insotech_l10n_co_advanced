# Paso a Paso: Configuración de Facturación Electrónica en Odoo 18 (Software Propio DIAN)

La configuración de la facturación electrónica como "Software Propio" requiere acciones coordinadas tanto en el portal Muisca de la DIAN como en la plataforma Odoo 18. Este es el flujo detallado de implementación:

## FASE 1: Preparación ante la DIAN y Certificados

Antes de tocar la configuración de Odoo, debes tener resueltos estos prerrequisitos legales:

1.  **Actualización del RUT:**
    *   La compañía debe estar registrada bajo la responsabilidad de "Facturador Electrónico" (Código 52) y Responsable de IVA (Código 48) si aplica.
2.  **Adquisición de Firma Digital (.p12):**
    *   Debes comprar un certificado digital de firma a un organismo autorizado por la ONAC (GSE, Certicámara, Andes SCD, etc.).
    *   **Importante:** Asegúrate de que el certificado se entregue en formato `.p12` o `.pfx` y que poseas la contraseña de instalación.
3.  **Registro en el Portal Habilitación DIAN:**
    *   Ingresa al portal [Habilitación Facturando Electrónicamente de la DIAN](https://catalogo-vpfe.dian.gov.co/User/Login).
    *   Ingresa con los datos del representante legal o NIT de la empresa.
    *   Ve al menú **Participantes > Facturador**. Allí confirma que iniciarás tu proceso de habilitación.
4.  **Asignación de "Software Propio":**
    *   En el menú de la DIAN, ve a **Configuración > Asociar rangos de prueba**.
    *   Selecciona el modo de operación: **Software Propio**.
    *   Al guardar, la plataforma de la DIAN te generará un código larguísimo llamado **Test Set ID** (Identificador del Set de Pruebas). Cópialo y guárdalo.
    *   También requerirás el **Software ID** y el **PIN del Software**, que usualmente se generan en el mismo apartado (el PIN suele ser 12345 por defecto en el ambiente de pruebas).

---

## FASE 2: Configuración Inicial en Odoo 18

En este punto, ya tienes tu certificado `.p12` y el `Test Set ID` de la DIAN.

1.  **Instalación de Módulos:**
    *   Ve a *Aplicaciones*, remueve el filtro "Aplicaciones" para ver los módulos técnicos e instala:
        *   `l10n_co_edi`: Estructura para Intercambio Electrónico.
        *   `l10n_co_dian`: El conector directo con el web service de la DIAN.
2.  **Configuración de la Compañía Matriz:**
    *   Ve a *Ajustes > Usuarios y Empresas > Empresas* y selecciona la tuya.
    *   Es crítico llenar **exactamente** la información tal como está en el RUT:
        *   **Tipo de Documento:** NIT
        *   **NIT:** El número sin dígito de verificación. Odoo calculará (o pedirá) el dígito.
        *   **Tipo de Organización:** Empresa u Persona natural.
        *   **Régimen:** Selecciona el régimen tributario correspondiente (Responsable de IVA, No Responsable, etc.).
        *   **Dirección completa:** Incluyendo el departamento y municipio seleccionados usando el nomenclador geográfico oficial de Odoo para Colombia (esto es mandatorio para el XML).
        *   **Código CIIU:** La actividad económica principal.
        *   **Responsabilidades Fiscales:** Agrega las que figuran en el RUT de tu empresa.

---

## FASE 3: Configuración de Credenciales DIAN en Odoo

Este es el núcleo de la integración "Software Propio":

1.  **Carga del Certificado:**
    *   Ve a *Contabilidad > Configuración > Ajustes > Facturación Electrónica (CO)* (o ve a la ficha de la compañía, en la pestaña de facturación electrónica).
    *   Sube el archivo de Firma Digital (`.p12`).
    *   Ingresa la contraseña del certificado.
2.  **Configuración del Entorno de Pruebas:**
    *   En los ajustes de DIAN Odoo, ubica los campos de integración.
    *   Selecciona el entorno de **Pruebas (Test)**.
    *   Pega el **Test Set ID** que te dio la DIAN.
    *   Pega el **Software ID**.
    *   Pega el **Software PIN** asociado.

---

## FASE 4: Mapeo de Catálogos (Impuestos, Diarios y Contactos)

Para que el XML sea válido, los datos maestros de la operación deben estar alineados:

1.  **Diario Contable de Facturas:**
    *   Ve a *Contabilidad > Configuración > Diarios* y edita el diario de "Facturas de Cliente".
    *   En la pestaña Configuración Avanzada o Facturación Electrónica, asegúrate de activar que este diario envía facturas a la DIAN.
    *   **Aviso:** En la fase de pruebas (Habilitación), el prefijo de la factura que generes debe coincidir obligatoriamente con el prefijo "PRTF" y o usar la serie exacta que la DIAN asigna para el set de pruebas.
2.  **Validación de Clientes (Contactos):**
    *   Verifica que los clientes a los que les vayas a facturar tengan su "Tipo de Documento" definido (CC, NIT), el número de documento puesto, ciudad, departamento y sus correspondientes responsabilidades fiscales, junto con el régimen (ej. Consumidor Final, Gran Contribuyente). Odoo fallará al generar el XML si falta la ciudad del cliente.
3.  **Configuración de Impuestos:**
    *   Los impuestos de IVA y Retenciones deben tener su correspondiente "Tipo de Impuesto DIAN" pre-asociado. Por defecto al instalar `l10n_co` esto viene mapeado, pero nunca está de más revisarlo (ej: IVA es tipo 01).

---

## FASE 5: El Set de Pruebas (Habilitación)

La DIAN exige demostrar que el sistema sabe emitir XMLs conformes enviando un volumen pequeño de prueba (Ej: 8 Facturas, 1 Nota Crédito, 1 Nota Débito).

1.  Crea una factura de cliente y compruébala.
2.  Haz clic en el botón de **Procesar ahora / Enviar a la DIAN**.
3.  Odoo generará el XML y lo enviará al entorno de validación de la DIAN. Si la configuración es correcta, el estado del documento electrónico cambiará a "Aceptado".
4.  Repite generando facturas y emitiendo notas de crédito hasta que en el portal Habilitación de la DIAN veas el mensaje: **"Ha culminado su proceso de habilitación exitosamente"**.

---

## FASE 6: Paso a Producción 🚀

Una vez certificado en Muisca, debes realizar el pase productivo:

1.  **Solicitud de Resolución DIAN:**
    *   En el portal principal (Producción) de la DIAN (MUISCA), solicita una nueva "Resolución de Facturación Electrónica" y una resolución para "Documentos Soporte" si aplica.
2.  **Asociar Rangos y Prefijos en DIAN:**
    *   Ve a *Facturando Electrónicamente > Configuración > Asociar Rangos de Numeración*.
    *   Vincula los prefijos autorizados (Ej: FE) en la resolución que acabas de solicitar a la plataforma de software propio.
3.  **Configurar Producción en Odoo:**
    *   En Odoo: *Contabilidad > Configuración > Ajustes > Facturación Electrónica*.
    *   Cambia el entorno de Pruebas a **Producción**.
    *   Bórra el Test Set ID (ya no es necesario en producción).
4.  **Insertar "Clave Técnica":**
    *   Al asociar los rangos en el portal de la DIAN, se genera una Clave Técnica por cada prefijo de resolución.
    *   En Odoo debes crear/configurar la Resolución de Facturación dentro de la vista del Diario de Ventas o de forma independiente en la secuencia, colocando el número de resolución, fecha de vigencia, rangos numéricos provistos (Ej: FE-1 al FE-1000) y obligatoriamente **la Clave Técnica de ese prefijo** para que Odoo pueda firmar legalmente las facturas reales.

### Flujo Diario de Operación Operativo en Odoo:
1. El usuario crea el Borrador de Factura.
2. Confirma la Factura.
3. Automáticamente (o mediante botón "Enviar e Imprimir"): Odoo genera el XML, lo firma, contacta con la DIAN web-service, y descarga el *ApplicationResponse*.
4. Odoo estampa el código CUFE/CUDE que la DIAN devolvió, genera el código QR, y se le envía el '.zip' por email al respectivo cliente final.

> **💡 Nota Especial para ambientes Odoo.sh:** Se recomienda ampliamente completar las fases 3 a 5 (Habilitación / Set de Pruebas) dentro de una rama **Staging (Pruebas)** en tu proyecto de Odoo.sh. Únicamente cuando te den luz verde en el portal MUISCA, replicas la Fase 6 directamente en los Ajustes de configuración de tu base de datos de producción, manteniendo así la base principal limpia de las facturas falsas de prueba ("facturas basura").

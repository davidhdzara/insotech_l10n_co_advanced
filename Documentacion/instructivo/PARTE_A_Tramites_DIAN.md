# PARTE A: Trámites ante la DIAN (Portal MUISCA)

> **Guía Maestra de Facturación Electrónica DIAN — Odoo 19**
> Versión: 1.0 | Fecha: Marzo 2026

---

## Índice de esta sección

| Paso | Descripción | Prereq. | Entregable |
|------|-------------|---------|------------|
| A.1 | Actualización del RUT | Acceso MUISCA | RUT con código 52 |
| A.2 | Certificado de Firma Digital | Presupuesto aprobado | Archivo `.p12` + contraseña |
| A.3 | Registro en Portal de Habilitación | RUT actualizado | Cuenta activa en catalogo-vpfe |
| A.4 | Software Propio: Credenciales | Registro completado | Software ID, PIN, Test Set ID |
| A.5 | Solicitud de Resolución | Habilitación superada ⚠️ | Número de Resolución, prefijo, rangos |
| A.6 | Asociar Rangos y Clave Técnica | Resolución otorgada | Clave Técnica por prefijo |
| A.7 | Notas Normativas 2026 | — | Conocimiento actualizado |

> [!TIP]
> Guarde **todos** los datos que obtenga en cada paso en una hoja de cálculo segura. Los necesitará en la Parte B (Configuración en Odoo).

---

## A.1 Actualización del RUT

### ¿Qué es?

El RUT (Registro Único Tributario) es la cédula fiscal de su empresa ante la DIAN. Para facturar electrónicamente, su RUT **debe** incluir la responsabilidad de "Facturador Electrónico".

### ¿Quién lo hace?

El **Representante Legal** de la empresa, o un contador/abogado con poder autenticado.

### Paso a paso

1. Ingrese a [muisca.dian.gov.co](https://muisca.dian.gov.co) con las credenciales del Representante Legal.
2. Navegue a **Registro Único Tributario (RUT) → Actualización RUT**.
3. En la sección **Responsabilidades**, verifique que estén marcadas:

| Código | Descripción | ¿Obligatorio? |
|--------|------------|---------------|
| **52** | Facturador Electrónico | ✅ Sí — sin esto la DIAN no le permite emitir |
| **48** | Responsable de IVA | Según su régimen tributario |
| **49** | No Responsable de IVA | Según su régimen tributario (excluyente con 48) |

4. Si alguna responsabilidad falta, agréguela y guarde los cambios.
5. **Descargue el RUT actualizado en PDF** y archívelo — lo necesitará como referencia constante.

### Verificación

- [ ] El RUT descargado muestra el código **52** en la sección de Responsabilidades.
- [ ] Los datos de Razón Social, NIT y dirección son correctos y actualizados.

> [!CAUTION]
> Cada dato del RUT (Razón Social, dirección, NIT) debe coincidir **exactamente** con lo que configure en Odoo. Una sola discrepancia causará rechazo de la DIAN con error **FAJ44b**.

---

## A.2 Adquisición del Certificado de Firma Digital (.p12)

### ¿Qué es?

El certificado digital es su "firma electrónica" ante la DIAN. Es un archivo criptográfico (`.p12` o `.pfx`) que Odoo usa internamente para firmar cada XML de factura electrónica antes de enviarlo. Sin este certificado, la DIAN no acepta ningún documento.

### ¿Quién lo emite?

Únicamente entidades certificadoras autorizadas por la **ONAC** (Organismo Nacional de Acreditación de Colombia). Las tres más utilizadas en Colombia son:

| Entidad | Sitio web | Costo aprox. anual |
|---------|-----------|-------------------|
| **GSE** | [www.gse.com.co](https://www.gse.com.co) | $100.000 – $200.000 COP |
| **Certicámara** | [www.certicamara.com](https://www.certicamara.com) | $150.000 – $300.000 COP |
| **Andes SCD** | [www.andesscd.com.co](https://www.andesscd.com.co) | $100.000 – $250.000 COP |

### Paso a paso

1. **Contacte al proveedor** elegido y solicite un *Certificado de Firma Digital para Facturación Electrónica*.
2. **Especifique que necesita formato `.p12` o `.pfx`** — ambos son compatibles con Odoo. Algunos proveedores ofrecen otros formatos (`.cer`, `.key`) que Odoo **no acepta** directamente.
3. **Complete el proceso de validación de identidad** — generalmente requiere:
   - Copia del RUT actualizado (paso A.1).
   - Cédula del Representante Legal.
   - Cámara de Comercio vigente (para personas jurídicas).
   - Videollamada o presencia física para verificación biométrica.
4. **Reciba y almacene de forma segura:**

| Entregable | Descripción | Dónde lo usará |
|------------|-------------|----------------|
| Archivo `.p12` | El certificado digital propiamente dicho | Se sube a Odoo (Fase 3 de la Parte B) |
| Contraseña del certificado | Clave alfanumérica para usar el `.p12` | Se ingresa en Odoo junto al archivo |

5. **Anote la fecha de vencimiento** del certificado (generalmente 1 año). Programe un recordatorio para renovarlo al menos 30 días antes.

### Verificación

- [ ] Tiene el archivo `.p12` descargado y almacenado en una ubicación segura.
- [ ] Conoce y ha probado la contraseña del certificado.
- [ ] Ha registrado la fecha de vencimiento del certificado.

> [!WARNING]
> **Seguridad del certificado:** Trate el archivo `.p12` como una contraseña maestra. Cualquier persona con acceso a este archivo y su contraseña puede firmar documentos electrónicos en nombre de su empresa. No lo comparta por correo electrónico ni lo almacene en carpetas compartidas sin cifrado.

> [!NOTE]
> **Tiempo estimado:** El proceso de adquisición puede tomar entre 2 y 10 días hábiles dependiendo del proveedor y la rapidez con que complete la validación de identidad.

---

## A.3 Registro como Facturador Electrónico en el Portal de Habilitación

### ¿Qué es?

El portal de habilitación es el entorno de la DIAN donde su empresa se registra oficialmente como emisor de documentos electrónicos. Es diferente del portal MUISCA principal — este es específicamente para el proceso de habilitación de facturación electrónica.

### ¿Cuál es la URL?

- **Portal de habilitación:** [catalogo-vpfe.dian.gov.co](https://catalogo-vpfe.dian.gov.co/User/Login)

> [!IMPORTANT]
> No confunda este portal con el MUISCA principal (`muisca.dian.gov.co`). Son portales diferentes con funciones distintas. El de habilitación (`catalogo-vpfe`) es donde se registra el software, se hacen pruebas y se asocian rangos. El MUISCA principal es donde se solicitan resoluciones de numeración.

### Paso a paso

1. Ingrese a [catalogo-vpfe.dian.gov.co](https://catalogo-vpfe.dian.gov.co/User/Login).
2. Autentíquese con:
   - **NIT** de la empresa (sin dígito de verificación).
   - **Credenciales** del Representante Legal.
3. Navegue a **Participantes → Facturador**.
4. Confirme que desea iniciar su proceso de habilitación como facturador electrónico.
5. El sistema le mostrará un panel con el estado de su habilitación — inicialmente estará en **"Pendiente"**.

### Verificación

- [ ] Puede ingresar al portal de habilitación sin errores.
- [ ] El estado de su empresa como "Facturador" se muestra correctamente.
- [ ] Puede navegar por los menús del portal sin restricciones de acceso.

---

## A.4 Registro de "Software Propio" y Obtención de Credenciales

### ¿Qué es?

Este es el paso donde le indica a la DIAN que **Odoo** será su sistema de facturación electrónica, operando bajo la modalidad de "Software Propio". La DIAN le entregará tres credenciales que Odoo necesita para comunicarse con sus servicios web.

> [!NOTE]
> **¿Por qué "Software Propio"?** En Colombia existen dos modalidades de facturación electrónica:
> 1. **Proveedor Tecnológico:** Usted contrata a un intermediario (Carvajal, Cadena, FacturaTech) que se encarga del envío. Tiene un costo mensual recurrente.
> 2. **Software Propio:** Su ERP (Odoo) se comunica directamente con la DIAN. Sin intermediarios. **Esta es la opción que usamos.**

### Paso a paso

1. En el portal de habilitación ([catalogo-vpfe.dian.gov.co](https://catalogo-vpfe.dian.gov.co/User/Login)), navegue a **Configuración → Asociar Rangos de Prueba**.
2. Seleccione el modo de operación: **Software Propio**.
3. Al guardar, la plataforma DIAN le generará tres datos críticos:

| Dato | Qué es | Ejemplo | Dónde lo usará en Odoo |
|------|--------|---------|------------------------|
| **Software ID** | Identificador único de su software ante la DIAN | `a3d6c1b2-4e5f-...` (UUID largo) | Ajustes → Facturación Electrónica → Modos de Operación |
| **Software PIN** | PIN numérico de su software | `12345` (en pruebas) | Ajustes → Facturación Electrónica → Modos de Operación |
| **Test Set ID** | Identificador del set de pruebas | `f8c2e1d9a7...` (hash alfanumérico) | Ajustes → Facturación Electrónica → Testing ID |

4. **Copie los tres datos y guárdelos inmediatamente** en su hoja de datos segura.

### Verificación

- [ ] Ha copiado y guardado el **Software ID**.
- [ ] Ha copiado y guardado el **Software PIN**.
- [ ] Ha copiado y guardado el **Test Set ID**.
- [ ] Puede volver a consultar estos datos en el portal si los necesita.

> [!CAUTION]
> **No pierda estos datos.** Si pierde el Test Set ID o el Software ID, deberá regenerarlos en el portal de habilitación (lo cual puede reiniciar su proceso de pruebas).

---

## A.5 Solicitud de Resolución de Facturación (Para Producción)

> [!WARNING]
> **⏱️ Este paso se realiza DESPUÉS de superar el Set de Pruebas** (Fase 6 de la Parte B). Lo documentamos aquí para que conozca el flujo completo de trámites ante la DIAN, pero **no lo ejecute aún** hasta haber completado la habilitación exitosamente.

### ¿Qué es?

La Resolución de Facturación es la autorización oficial de la DIAN para que su empresa emita facturas electrónicas dentro de un rango numérico específico y un periodo de vigencia definido. Sin resolución vigente, no puede facturar legalmente.

### Paso a paso

1. Ingrese al portal principal de **MUISCA**: [muisca.dian.gov.co](https://muisca.dian.gov.co) (el de producción, **no** el de habilitación).
2. Navegue a **Facturación → Numeración de Facturación → Solicitud de Numeración**.
3. Solicite una nueva **Resolución de Facturación Electrónica**.
4. Complete los campos requeridos:

| Campo | Qué poner | Ejemplo |
|-------|-----------|---------|
| **Prefijo** | Letras que identificarán sus facturas | `FE` |
| **Rango Desde** | Primer número de la serie | `1` |
| **Rango Hasta** | Último número de la serie | `5000` |

5. La DIAN asignará automáticamente:
   - **Número de Resolución** (ej. `18764000000001`).
   - **Fecha de inicio** y **fecha de fin** de vigencia (generalmente 2 años).
6. **Descargue o imprima** la resolución otorgada.

### ¿Necesita resoluciones adicionales?

Dependiendo de su operación, puede necesitar múltiples resoluciones:

| Tipo de documento | ¿Necesita resolución propia? | Prefijo sugerido |
|---|---|---|
| Factura de Venta Electrónica | ✅ Siempre | `FE` |
| Nota Crédito Electrónica | ⚠️ Consulte con su contador (puede compartir resolución con FE) | `NC` |
| Nota Débito Electrónica | ⚠️ Consulte con su contador | `ND` |
| Documento Soporte (compras a no obligados) | ✅ Sí, resolución independiente | `DS` |
| Factura de Exportación | ✅ Si exporta, resolución separada | `FEX` |

> [!TIP]
> **Recomendación práctica:** Para una empresa típica que vende en Colombia y compra a personas naturales no obligadas a facturar, necesitará al menos **dos resoluciones**: una para Facturas de Venta (`FE`) y otra para Documentos Soporte (`DS`).

### Verificación

- [ ] Tiene el número de resolución anotado.
- [ ] Conoce el prefijo, rango desde, rango hasta.
- [ ] Conoce las fechas de inicio y fin de vigencia.
- [ ] Si aplica, tiene resolución(es) adicional(es) para DS, NC, etc.

---

## A.6 Asociar Rangos y Obtener la Clave Técnica

### ¿Qué es?

La Clave Técnica es un hash criptográfico que la DIAN genera al vincular un prefijo de resolución con su software. Es un dato **obligatorio** para que Odoo pueda firmar y enviar facturas en producción. Sin la Clave Técnica, Odoo no puede generar el CUFE (Código Único de Factura Electrónica).

### Paso a paso

1. Regrese al portal de habilitación: [catalogo-vpfe.dian.gov.co](https://catalogo-vpfe.dian.gov.co/User/Login).
2. Navegue a **Facturando Electrónicamente → Configuración → Asociar Rangos de Numeración**.
3. Vincule cada prefijo autorizado a la resolución correspondiente:
   - Seleccione la resolución (ej. `18764000000001`).
   - Asocie el prefijo (ej. `FE`).
   - Defina el rango de numeración.
4. Al guardar, la DIAN generará una **Clave Técnica** para cada prefijo.
5. **Copie la Clave Técnica inmediatamente** — la necesitará en la configuración de diarios de Odoo.

### Datos obtenidos — Tabla de referencia

Para cada prefijo que haya asociado, debería tener un registro como este:

| Dato | Ejemplo |
|------|---------|
| **Número de Resolución** | `18764000000001` |
| **Prefijo** | `FE` |
| **Rango Desde** | `1` |
| **Rango Hasta** | `5000` |
| **Fecha Inicio Vigencia** | `2026-01-01` |
| **Fecha Fin Vigencia** | `2028-01-01` |
| **Clave Técnica** | `fc8eac422eba16...` (hash alfanumérico largo) |

> [!IMPORTANT]
> **Repita este proceso para cada tipo de documento** que vaya a emitir. Si tiene resoluciones para FE, NC, ND y DS, necesita asociar los rangos y obtener la Clave Técnica para cada uno.

### Verificación

- [ ] Cada prefijo tiene su Clave Técnica anotada.
- [ ] Los rangos de numeración coinciden con lo que solicitó en A.5.
- [ ] Las fechas de vigencia están registradas.

---

## A.7 Notas Normativas Vigentes (2026)

> [!NOTE]
> Esta sección resume las actualizaciones normativas recientes que pueden impactar su configuración. No requiere acción inmediata — es información de contexto para tomar decisiones informadas.

### Simplificación de Datos del Adquiriente (Resolución 000202)

La DIAN redujo a **máximo 3** los datos obligatorios del comprador para emitir una factura electrónica válida:

1. Nombre o Razón Social
2. Tipo y Número de Identificación (NIT / CC)
3. Correo Electrónico (solo si la entrega es digital)

**Impacto práctico:** Para facturación rápida (ej. punto de venta), ya no es obligatorio solicitar la dirección completa del comprador. Sin embargo, para facturación B2B conviene tener los datos completos para evitar rechazos.

### Documento Soporte — Deducibilidad Cross-Año (Concepto 0158 - Enero 2026)

Se permite que los Documentos Soporte expedidos en el año fiscal **siguiente** a la causación del gasto sigan siendo válidos para deducción en renta, siempre que se demuestre que el devengo del gasto ocurrió en el año correspondiente.

**Impacto práctico:** Si compra a una persona natural en diciembre 2025 pero emite el Documento Soporte en enero 2026, el gasto sigue siendo deducible en renta 2025.

### Ventana de Contingencia de 48 Horas

Para empresas con fallas tecnológicas comprobables, la DIAN autoriza una ventana de hasta **48 horas** para generar el documento equivalente electrónico en caso de contingencia.

**Impacto práctico:** Si los servicios web de la DIAN están caídos o su sistema tiene una falla técnica documentada, tiene hasta 48 horas para retransmitir los documentos sin penalización.

---

## Resumen: Datos Obtenidos en la Parte A

Al completar todos los pasos de esta parte debe tener los siguientes datos listos para la configuración en Odoo (Parte B):

| # | Dato | Obtenido en paso | ¿Lo tiene? |
|---|------|-------------------|------------|
| 1 | RUT actualizado (PDF) con código 52 | A.1 | ☐ |
| 2 | Archivo `.p12` (certificado digital) | A.2 | ☐ |
| 3 | Contraseña del certificado `.p12` | A.2 | ☐ |
| 4 | Fecha de vencimiento del certificado | A.2 | ☐ |
| 5 | Acceso al portal de habilitación | A.3 | ☐ |
| 6 | Software ID | A.4 | ☐ |
| 7 | Software PIN | A.4 | ☐ |
| 8 | Test Set ID | A.4 | ☐ |
| 9 | Número(s) de Resolución | A.5 ⚠️ | ☐ |
| 10 | Prefijo(s) y Rangos | A.5 ⚠️ | ☐ |
| 11 | Clave(s) Técnica(s) | A.6 ⚠️ | ☐ |

> Los ítems marcados con ⚠️ se obtienen **después** de superar el Set de Pruebas (Parte B, Fase 6).

---

> **Siguiente sección:** [PARTE B: Configuración en Odoo 19](./PARTE_B_Configuracion_Odoo.md) *(próximamente)*

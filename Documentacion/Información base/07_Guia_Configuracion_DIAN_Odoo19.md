# Guía Completa: Configuración de Facturación Electrónica DIAN en Odoo 19

Esta guía está diseñada para usuarios que nunca han configurado facturación electrónica. Cubre **todo el proceso de punta a punta**: desde la gestión ante la DIAN hasta la emisión de su primera factura en Odoo 19.

> **Nota:** La interfaz del portal MUISCA de la DIAN puede cambiar periódicamente. Los pasos descritos reflejan el flujo vigente a **marzo de 2026**. La lógica general del proceso permanece igual aunque la DIAN reubique botones.

---

## PARTE A: Trámites ante la DIAN (Portal MUISCA)

Antes de configurar Odoo, debe completar los siguientes trámites legales directamente en el portal de la DIAN.

### A.1 Actualización del RUT

Su empresa debe estar registrada como Facturador Electrónico ante la DIAN.

1. Ingrese a [muisca.dian.gov.co](https://muisca.dian.gov.co) con las credenciales del **Representante Legal**.
2. Vaya a **Registro Único Tributario (RUT) → Actualización RUT**.
3. En la sección de **Responsabilidades**, verifique que tenga marcadas:
   - **Código 52** — Facturador Electrónico (obligatorio).
   - **Código 48** — Responsable de IVA (si aplica según su régimen).
4. Guarde los cambios y descargue el RUT actualizado en PDF.

### A.2 Adquisición del Certificado de Firma Digital (.p12)

El certificado digital es su "firma electrónica" ante la DIAN. Sin él, no puede emitir documentos electrónicos.

1. Contacte a una entidad certificadora autorizada por la ONAC:
   - **GSE** — [www.gse.com.co](https://www.gse.com.co)
   - **Certicámara** — [www.certicamara.com](https://www.certicamara.com)
   - **Andes SCD** — [www.andesscd.com.co](https://www.andesscd.com.co)
2. Solicite un **Certificado de Firma Digital para Facturación Electrónica**.
3. Pida que se entregue en formato **`.p12`** o **`.pfx`**.
4. Al recibirlo, guarde en un lugar seguro:
   - El **archivo `.p12`** (lo subirá a Odoo).
   - La **contraseña** del certificado (la necesitará en Odoo).
5. Costo aproximado: entre $100.000 y $300.000 COP anuales según el proveedor.

### A.3 Registro como Facturador Electrónico en el Portal de Habilitación

1. Ingrese al portal de habilitación: [catalogo-vpfe.dian.gov.co](https://catalogo-vpfe.dian.gov.co/User/Login).
2. Autentíquese con los datos del Representante Legal o NIT de la empresa.
3. Vaya al menú **Participantes → Facturador**.
4. Confirme que desea iniciar su proceso de habilitación como facturador electrónico.

### A.4 Registro de "Software Propio" y Obtención de Credenciales

Este es el paso donde la DIAN le entrega las llaves que Odoo necesita para comunicarse con ella.

1. En el portal de habilitación, vaya a **Configuración → Asociar Rangos de Prueba**.
2. Seleccione el modo de operación: **Software Propio**.
3. Al guardar, la DIAN le generará tres datos críticos. **Cópielos y guárdelos:**

| Dato | Qué es | Para qué lo usará |
|---|---|---|
| **Test Set ID** | Identificador del set de pruebas (código alfanumérico largo) | Configurar el entorno de pruebas en Odoo |
| **Software ID** | Identificador único de su software ante la DIAN | Configurar los Modos de Operación en Odoo |
| **Software PIN** | PIN numérico de su software (generalmente `12345` en pruebas) | Configurar los Modos de Operación en Odoo |

### A.5 Solicitud de Resolución de Facturación (Para Producción)

> **Nota:** Este paso se realiza DESPUÉS de superar el Set de Pruebas (Fase 6 de esta guía). Lo incluimos aquí para que conozca el flujo completo.

Cuando ya esté certificado (habilitado) ante la DIAN:

1. Ingrese al portal principal de **MUISCA** (el de producción, no el de habilitación).
2. Vaya a **Facturación → Numeración de Facturación → Solicitud de Numeración**.
3. Solicite una nueva **Resolución de Facturación Electrónica**.
   - Indique el **prefijo** deseado (ej. `FE`).
   - Indique el **rango de numeración** (ej. del 1 al 5000).
   - La DIAN le asignará un **Número de Resolución** y una **fecha de vigencia**.
4. Si también necesita emitir **Documentos Soporte** a no obligados, solicite una resolución adicional con prefijo diferente (ej. `DS`).

### A.6 Asociar Rangos y Obtener la Clave Técnica

1. Vuelva al portal de habilitación: [catalogo-vpfe.dian.gov.co](https://catalogo-vpfe.dian.gov.co/User/Login).
2. Vaya a **Facturando Electrónicamente → Configuración → Asociar Rangos de Numeración**.
3. Vincule cada prefijo autorizado (ej. `FE`, `NC`, `DS`) a la resolución correspondiente.
4. Al guardar, la DIAN generará una **Clave Técnica** por cada prefijo. **Cópiela y guárdela.**

| Dato | Ejemplo |
|---|---|
| Número de Resolución | 18764000000001 |
| Prefijo | FE |
| Rango Desde | 1 |
| Rango Hasta | 5000 |
| Fecha Inicio Vigencia | 2026-01-01 |
| Fecha Fin Vigencia | 2028-01-01 |
| **Clave Técnica** | fc8eac422eba16… (hash alfanumérico largo) |

> **💡 Consejo:** Guarde todos estos datos en una hoja de cálculo o documento seguro. Los necesitará para configurar los diarios en Odoo.

---

## PARTE B: Configuración en Odoo 19

Con los trámites ante la DIAN completados y los datos en mano, ahora sí configuramos Odoo.

### Resumen de Datos que Necesitará

Antes de comenzar, tenga a la mano:

| Dato | Dónde lo obtuvo |
|---|---|
| Archivo `.p12` + contraseña | Entidad certificadora ONAC |
| Software ID | Portal Habilitación DIAN (paso A.4) |
| Software PIN | Portal Habilitación DIAN (paso A.4) |
| Test Set ID | Portal Habilitación DIAN (paso A.4) |
| Número de Resolución | Portal MUISCA (paso A.5) |
| Prefijo, Rangos y Clave Técnica | Portal Habilitación DIAN (paso A.6) |

---

## Fase 1: Instalación de Módulos

1. Ingrese a Odoo 19 como **Administrador**.
2. Vaya a **Aplicaciones**.
3. Busque e instale los siguientes módulos (en este orden):

| Módulo | Nombre Técnico | Descripción |
|---|---|---|
| Colombia - Contabilidad | `l10n_co` | Plan de cuentas, impuestos y estructura fiscal colombiana |
| Colombia - Facturación Electrónica EDI | `l10n_co_edi` | Estructura XML para intercambio electrónico |
| Colombia - Conector DIAN | `l10n_co_dian` | Emisor directo ante los web services de la DIAN |

> **Nota:** Al instalar `l10n_co_dian`, Odoo instalará automáticamente sus dependencias (`l10n_co_edi` y `l10n_co`).

---

## Fase 2: Configuración de la Compañía

Es **crítico** que la información de su empresa coincida exactamente con lo que aparece en el RUT. Un solo dato diferente causará rechazos de la DIAN.

1. Vaya a **Ajustes → Usuarios y Empresas → Empresas**.
2. Haga clic en su empresa.
3. Complete los siguientes campos **con exactitud**:

### Pestaña Principal
| Campo | Qué poner | Ejemplo |
|---|---|---|
| Nombre de la Empresa | Razón Social exacta del RUT | INSOTECH S.A.S. |
| NIT | Sin dígito de verificación (Odoo lo calcula) | 901234567 |
| Tipo de Documento | NIT | — |
| Tipo de Organización | Persona Jurídica o Natural | Persona Jurídica |
| Dirección | Completa: Calle, Ciudad, Departamento, País | Cra 7 # 45-12, Bogotá, Cundinamarca, Colombia |

> **⚠️ IMPORTANTE:** El campo de **Ciudad** y **Departamento** debe seleccionarse del catálogo oficial de Odoo (no escribirlo a mano). Si la ciudad falta, la DIAN rechazará la factura con error FAJ44b.

### Pestaña Ventas y Compras / Información Fiscal
| Campo | Qué poner |
|---|---|
| Régimen Fiscal | Responsable de IVA / No Responsable (según su RUT) |
| Obligaciones y Responsabilidades | Agregar las que figuren en su RUT (ej. O-13, O-15, O-23, O-47, O-48, R-99-PN) |
| Código CIIU | Actividad económica principal |

4. Haga clic en **Guardar**.

---

## Fase 3: Carga del Certificado Digital (.p12)

El certificado digital es lo que le permite a Odoo "firmar" las facturas electrónicas. Sin él, la DIAN no aceptará ningún documento.

1. Vaya a **Contabilidad → Configuración → Ajustes**.
2. Busque la sección **"Facturación Electrónica de Colombia"**.
3. En el campo **"Proveedor de Facturación Electrónica"**, seleccione: **DIAN: Servicio gratuito**.
4. En la sección de **Certificado de Firma Digital**:
   - Haga clic en **"Subir su archivo"** y seleccione su archivo `.p12`.
   - Ingrese la **contraseña** del certificado en el campo correspondiente.
5. Haga clic en **Guardar**.

> **¿No tiene certificado?** Debe comprarlo a un organismo autorizado por la ONAC. Los más comunes en Colombia son:
> - **GSE** (www.gse.com.co)
> - **Certicámara** (www.certicamara.com)
> - **Andes SCD** (www.andesscd.com.co)
>
> Solicite el formato `.p12` o `.pfx`. El costo oscila entre $100.000 y $300.000 COP anuales.

---

## Fase 4: Configuración de Modos de Operación (Software Propio)

Los "Modos de Operación" le dicen a Odoo qué tipos de documentos electrónicos va a emitir y con qué credenciales DIAN.

1. En la misma pantalla de Ajustes de Facturación Electrónica, busque **"Modos de Operación"**.
2. Haga clic en **"Añadir una línea"**.
3. Complete los campos:

| Campo | Qué poner | De dónde lo saco |
|---|---|---|
| Modo de Software | Factura Electrónica de Venta | Seleccionar del menú |
| Software ID | El código largo que le dio la DIAN | Portal Habilitación → Configuración → Software Propio |
| NIP de Software | Generalmente `12345` en pruebas, o el asignado | Portal Habilitación DIAN |
| Testing ID (Test Set ID) | El identificador del set de pruebas | Portal Habilitación → Asociar Rangos de Prueba |

4. Si también va a emitir **Documentos Soporte** (compras a no obligados a facturar), agregue otra línea con el modo correspondiente.
5. Haga clic en **Guardar**.

---

## Fase 5: Creación y Configuración de Diarios Contables

Los diarios contables son los "cuadernos" donde Odoo registra las transacciones. Necesita crear diarios separados para cada tipo de documento electrónico.

### 5.1 Diario de Facturas de Venta (Obligatorio)

1. Vaya a **Contabilidad → Configuración → Diarios**.
2. Haga clic en **"Nuevo"**.
3. Complete:

| Campo | Valor |
|---|---|
| Nombre del Diario | Facturas de Venta Electrónicas |
| Tipo | Ventas |
| Código Corto | FE (o el prefijo de su resolución) |

4. En la pestaña **"Asientos Contables"**:
   - Configure las cuentas de ingreso y de pagos pendientes según su PUC.

5. En la pestaña **"Ajustes Avanzados"**:
   - Active la opción **"Facturación electrónica"** y seleccione **UBL 2.1 (Colombia)**.
   - Ingrese el **Número de Resolución** que la DIAN le otorgó.

6. Haga clic en **Guardar**.

### 5.2 Diario de Notas Crédito (Obligatorio)

1. Cree un nuevo diario con:

| Campo | Valor |
|---|---|
| Nombre del Diario | Notas Crédito Electrónicas |
| Tipo | Ventas |
| Código Corto | NC |

2. En **Ajustes Avanzados**, active la facturación electrónica UBL 2.1 (Colombia).
3. Ingrese la resolución DIAN correspondiente (si usa una resolución separada para notas crédito).

> **Nota Odoo 19:** En muchos casos, las Notas Crédito y Débito pueden compartir el mismo diario de ventas y la misma resolución. Consulte con su contador si su resolución DIAN cubre ambos documentos.

### 5.3 Diario de Notas Débito (Si aplica)

Repita el proceso del punto 5.2 con el prefijo y resolución correspondiente para Notas Débito.

### 5.4 Diario de Documentos Soporte (Si aplica)

Si su empresa realiza compras a **personas no obligadas a facturar** (personas naturales del régimen simplificado), necesita un diario adicional:

| Campo | Valor |
|---|---|
| Nombre del Diario | Documentos Soporte Electrónicos |
| Tipo | Compras |
| Código Corto | DS |

Active la facturación electrónica e ingrese la resolución independiente que la DIAN emitió para Documentos Soporte.

---

## Fase 6: Proceso de Habilitación (Set de Pruebas DIAN)

La DIAN exige que su sistema demuestre que puede generar XMLs correctos antes de permitirle facturar en producción. Esto se hace enviando un "Set de Pruebas" (generalmente 8-10 documentos).

### Odoo 19 — Proceso Simplificado

Odoo 19 simplificó enormemente este proceso con un asistente automático:

1. En **Contabilidad → Configuración → Ajustes → Facturación Electrónica**:
   - Active la casilla **"Entorno de Prueba"**.
   - Active la casilla **"Activar proceso de certificación"**.
   - Indique la **cantidad de documentos** que la DIAN requiere (consulte el portal de habilitación para conocer la cifra exacta, generalmente son 8 facturas, 1 nota crédito, 1 nota débito).
2. Haga clic en **"Iniciar Proceso de Habilitación"**.
3. Odoo generará automáticamente:
   - Clientes de prueba ficticios.
   - Productos de prueba.
   - Las facturas, notas crédito y débito necesarias.
4. Odoo enviará estos documentos a la DIAN y esperará la respuesta.
5. Cuando el portal de habilitación de la DIAN muestre el mensaje **"Ha culminado su proceso de habilitación exitosamente"**, usted está certificado.

### Verificación Manual (Si prefiere no usar el asistente)

1. Cree una factura de venta de prueba normalmente.
2. Confirme la factura.
3. Haga clic en **"Enviar e Imprimir"** o en el botón de **"Procesar"**.
4. Odoo generará el XML, lo firmará y lo enviará a la DIAN.
5. Verifique en el **Chatter** de la factura que el estado sea **"Aceptado"**.
6. Repita hasta completar el volumen requerido por la DIAN.

> **💡 Consejo para Odoo.sh:** Realice todo el Set de Pruebas en una rama de **Staging**. Así, las facturas "basura" de prueba no contaminarán su base de datos de producción.

---

## Fase 7: Paso a Producción 🚀

Una vez certificado en el portal de habilitación de la DIAN:

1. **En el portal MUISCA de la DIAN:**
   - Solicite la **Resolución de Facturación Electrónica** definitiva.
   - Vaya a **Facturando Electrónicamente → Configuración → Asociar Rangos de Numeración**.
   - Vincule los prefijos autorizados (ej. `FE`) a la resolución.
   - Copie la **Clave Técnica** generada para cada prefijo.

2. **En Odoo:**
   - Vaya a **Contabilidad → Configuración → Ajustes → Facturación Electrónica**.
   - Cambie el entorno de **Pruebas** a **Producción**.
   - Borre el Test Set ID (ya no es necesario).
   - Actualice los diarios de ventas con:
     - El número de resolución definitivo.
     - El rango autorizado (ej. FE-1 al FE-5000).
     - La **Clave Técnica** del prefijo.
     - La fecha de vigencia de la resolución.

3. **Emita su primera factura real** y verifique en el Chatter que la DIAN la aceptó con el CUFE oficial.

---

## Fase 8: Configuración de Contactos (Clientes)

Para que la DIAN no rechace sus facturas, cada cliente debe tener datos completos:

| Campo Obligatorio | Ejemplo |
|---|---|
| Tipo de Documento | NIT / CC / CE / Pasaporte |
| Número de Documento | 901234567 |
| Razón Social / Nombre | Exacto como aparece en el RUT del cliente |
| Ciudad | Seleccionada del catálogo oficial de Odoo |
| Departamento | Seleccionado del catálogo oficial de Odoo |
| Correo Electrónico | Para envío de la representación gráfica |
| Obligaciones Fiscales | Gran Contribuyente, Responsable de IVA, etc. |

> **⚠️ Error más común:** La dirección o razón social del cliente no coincide con la del RUT. Esto genera el error `FAJ44b` de la DIAN. Siempre verifique los datos contra el RUT oficial del cliente.

---

## Resumen Visual del Flujo Completo

```
┌──────────────────────┐
│ 1. Instalar módulos  │
│    l10n_co_dian       │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 2. Configurar empresa│
│    (datos del RUT)    │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 3. Subir certificado │
│    digital .p12       │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 4. Configurar modos  │
│    de operación DIAN  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 5. Crear diarios     │
│    FE / NC / ND / DS  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 6. Set de Pruebas    │
│    (Habilitación)     │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 7. Paso a Producción │
│    (Resolución real)  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 8. ¡Facturar! 🎉     │
└──────────────────────┘
```

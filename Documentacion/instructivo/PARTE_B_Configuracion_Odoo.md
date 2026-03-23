# PARTE B: Configuración en Odoo 19

> **Guía Maestra de Facturación Electrónica DIAN — Odoo 19**
> Versión: 1.0 | Fecha: Marzo 2026

---

## Índice de esta sección

| Fase | Descripción | Prereq. | Entregable |
|------|-------------|---------|------------|
| B.1 | Instalación de Módulos | Acceso admin Odoo | Módulos `l10n_co_dian` activos |
| B.2 | Configuración de la Compañía | RUT actualizado (A.1) | Datos empresa = RUT exacto |
| B.3 | Carga del Certificado Digital | Archivo .p12 (A.2) | Certificado activo sin errores |
| B.4 | Modos de Operación | Software ID y PIN (A.4/A.6) | Modo producción configurado |
| B.5 | Diarios Contables | Resolución y Clave Técnica (A.5/A.6) | Diarios FE, NC, ND, DS listos |
| B.6 | Verificación de Contactos | Datos receptor (RUT cliente) | Contactos con datos DIAN completos |
| B.7 | Primera Factura Real | Todas las fases anteriores | Factura aceptada por la DIAN |

> [!TIP]
> Tenga a la mano el **RUT actualizado** de su empresa y la tabla de datos de producción de la Parte A. Cada dato se usará en esta sección.

> [!IMPORTANT]
> **Prerequisito absoluto:** La Parte A debe estar completada. Necesita: Software habilitado (StatusCode 00), resolución de producción, Clave Técnica por prefijo, y certificado .p12.

---

## B.1 Instalación de Módulos

### ¿Qué es?

Odoo 19 incluye los módulos de facturación electrónica colombiana de forma nativa, pero deben estar instalados y activos.

### Paso a paso

1. Ingrese a Odoo 19 como **Administrador**.
2. Vaya a **Aplicaciones**.
3. Busque e instale los siguientes módulos (en este orden):

| Módulo | Nombre Técnico | Descripción |
|--------|---------------|-------------|
| Colombia - Contabilidad | `l10n_co` | Plan de cuentas, impuestos y estructura fiscal colombiana |
| Colombia - Facturación Electrónica EDI | `l10n_co_edi` | Estructura XML para intercambio electrónico con la DIAN |
| Colombia - Conector DIAN | `l10n_co_dian` | Emisor directo ante los web services de la DIAN |

> [!NOTE]
> Al instalar `l10n_co_dian`, Odoo instalará automáticamente sus dependencias (`l10n_co_edi` y `l10n_co`). Si ya tiene la localización colombiana activa, es posible que solo falte `l10n_co_dian`.

### Módulos adicionales (InSoTech)

Si está usando la suite InSoTech, instale también:

| Módulo | Nombre Técnico | Descripción |
|--------|---------------|-------------|
| InSoTech Localización Avanzada | `insotech_l10n_co_advanced` | PRE-INV, contador de resolución, mejoras UX |
| InSoTech DIAN Wizard | `insotech_dian_wizard` | Habilitador desacoplado (ya usado en Parte A) |

### Verificación

- [ ] El módulo `l10n_co_dian` aparece como "Instalado" en Aplicaciones.
- [ ] Al ir a Contabilidad → Ajustes, aparece la sección "Facturación Electrónica de Colombia".

> [!CAUTION]
> **Instancias sin demo data (Odoo.sh):** Si al intentar certificar aparece el error `product.product_category_goods not found`, debe crear manualmente el identificador externo. Vea la sección de [Solución de Problemas](#solución-de-problemas-conocidos) al final de esta guía.

---

## B.2 Configuración de la Compañía

### ¿Qué es?

La DIAN valida que los datos del emisor en cada factura electrónica coincidan **exactamente** con el RUT. Un solo carácter diferente genera rechazo con error **FAJ44b**.

### ¿Dónde se configura?

**Ruta:** Ajustes → Usuarios y Compañías → Compañías → *seleccionar su empresa*

### Paso a paso

1. Abra la ficha de su empresa.
2. Complete o verifique **cada campo** de la tabla siguiente:

#### Pestaña Principal (Información General)

| # | Campo Odoo | Qué poner | Fuente | ⚠️ Trampa común |
|---|-----------|-----------|--------|------------------|
| 1 | **Nombre de la empresa** | Razón Social EXACTA del RUT | RUT casilla 35 | No agregar ni quitar puntos, tildes ni espacios |
| 2 | **NIT** | Solo el número, SIN dígito de verificación | RUT casilla 5 | Odoo calcula el DV automáticamente |
| 3 | **Dígito de Verificación** | El que Odoo calcule (verificar que coincida) | RUT casilla 6 | Si no coincide, el NIT está mal ingresado |
| 4 | **Tipo de Documento** | NIT | — | Debe ser código 31 |
| 5 | **Tipo de Organización** | Persona Jurídica | — | O "Persona Natural" según aplique |
| 6 | **Dirección (calle)** | Dirección EXACTA del RUT | RUT casilla 24 | Abreviaciones deben ser idénticas (DG, CRA, CL, etc.) |
| 7 | **Ciudad** | Seleccionar del catálogo oficial de Odoo | RUT casilla 27 | **NUNCA escribir a mano** — debe tener código DANE |
| 8 | **Departamento** | Seleccionar del catálogo oficial de Odoo | RUT casilla 26 | Se autocompleta al seleccionar la ciudad |
| 9 | **Código Postal** | El que aparece en el RUT | RUT casilla 28 | Verificar que Odoo lo acepte sin error |
| 10 | **País** | Colombia | — | Código CO |
| 11 | **Email** | Email oficial de la empresa | — | Usado para recibir respuestas de la DIAN |
| 12 | **Teléfono** | Teléfono de la empresa | — | — |

#### Pestaña Ventas y Compras / Información Fiscal

| # | Campo Odoo | Qué poner | Fuente |
|---|-----------|-----------|--------|
| 13 | **Régimen Fiscal** | Responsable de IVA / No Responsable | RUT sección responsabilidades |
| 14 | **Obligaciones y Responsabilidades** | Agregar TODAS las que figuren en su RUT | RUT casilla 53 |
| 15 | **Código CIIU** | Actividad económica principal | RUT casilla 46 |

> [!CAUTION]
> **Regla de Oro #2:** Datos del emisor = RUT exacto. Carácter por carácter: razón social, dirección, códigos DANE. Un espacio extra, una tilde faltante o una abreviación diferente causa rechazo **FAJ44b**.

### Responsabilidades tributarias comunes

| Código | Descripción | ¿Cuándo aplica? |
|--------|------------|-----------------|
| O-13 | Gran contribuyente | Si la DIAN lo designó como tal |
| O-15 | Autorretenedor | Si la DIAN lo designó como tal |
| O-23 | Agente de retención IVA | Si aplica según normativa |
| O-47 | Régimen Simple de Tributación | Si está en régimen simple |
| O-48 | Responsable de IVA | Si es responsable de IVA |
| R-99-PN | No responsable | Si es persona natural no responsable de IVA |

### Ejemplo real — InSoTech

```
Nombre:       INFINITY SOLUTIONS TECHNOLOGY S.A.S.
NIT:          901797249
DV:           5
Dirección:    DG 54 19 20
Ciudad:       Bello (DANE 05088)
Departamento: Antioquia (05)
Código Postal: 051050
País:         Colombia
```

### Verificación

- [ ] Cada campo coincide carácter por carácter con el RUT.
- [ ] La ciudad fue seleccionada del catálogo (no escrita a mano).
- [ ] El DV que muestra Odoo coincide con el del RUT.
- [ ] Las responsabilidades tributarias están completas.

---

## B.3 Carga del Certificado Digital (.p12)

### ¿Qué es?

El certificado digital es lo que permite a Odoo "firmar" cada factura electrónica antes de enviarla a la DIAN. Sin firma digital, la DIAN rechaza el documento.

### ¿Dónde se configura?

**Ruta:** Contabilidad → Configuración → Ajustes → sección **"Facturación Electrónica de Colombia"**

### Paso a paso

1. En el campo **"Proveedor de Facturación Electrónica"**, seleccione: **DIAN: Servicio gratuito**.
2. En la sección de **Certificado de Firma Digital**:
   - Haga clic en **"Subir su archivo"** y seleccione su archivo `.p12`.
   - Ingrese la **contraseña** del certificado en el campo correspondiente.
3. Haga clic en **Guardar**.
4. Verifique que **no aparezca** ningún banner de error rojo.

> [!WARNING]
> **Formato del archivo:** Odoo solo acepta archivos `.p12` o `.pfx`. Si su certificadora le entregó archivos `.cer` + `.key` por separado, debe solicitar la conversión a `.p12` (o usar OpenSSL para combinarlos).

> [!IMPORTANT]
> **Fecha de vencimiento:** El certificado digital tiene vigencia de 1 año (generalmente). Programe un recordatorio para renovarlo al menos **30 días antes** de su vencimiento. Si el certificado vence, Odoo dejará de poder firmar facturas **inmediatamente**.

### Verificación

- [ ] El archivo `.p12` se cargó sin errores.
- [ ] La contraseña fue aceptada.
- [ ] Al guardar, no aparece ningún mensaje de error.

---

## B.4 Configuración de Modos de Operación (Software Propio)

### ¿Qué es?

Los "Modos de Operación" le dicen a Odoo qué tipos de documentos electrónicos va a emitir y con qué credenciales DIAN. Aquí es donde se vincula Odoo con el software que registró ante la DIAN.

### ¿Dónde se configura?

**Ruta:** Contabilidad → Configuración → Ajustes → sección **"Facturación Electrónica de Colombia"** → tabla **"Modos de Operación"**

### Paso a paso

1. Haga clic en **"Añadir una línea"**.
2. Complete los campos:

| Campo | Valor | De dónde sale |
|-------|-------|---------------|
| **Modo de Software** | Factura Electrónica de Venta | Seleccionar del menú |
| **Software ID** | El código largo del portal de producción | Paso A.6 — Portal `catalogo-vpfe.dian.gov.co` |
| **NIP de Software** | El PIN numérico asignado | Portal DIAN |

3. Si también va a emitir **Documentos Soporte** (compras a no obligados), agregue otra línea con el modo correspondiente.

### Configuración del entorno

En la misma pantalla de ajustes, verifique:

| Casilla | Estado requerido |
|---------|-----------------|
| ☐ Entorno de Prueba | **DESACTIVADA** — Ya estamos en producción |
| ☐ Activar proceso de certificación | **DESACTIVADA** — La habilitación ya se completó |

4. Haga clic en **Guardar**.

> [!CAUTION]
> **No confunda credenciales de prueba con producción.** El Software ID puede variar entre entornos. Asegúrese de usar el Software ID que aparece en el portal de **producción** (`catalogo-vpfe.dian.gov.co`), no en el de habilitación (`catalogo-vpfe-hab.dian.gov.co`).

### Verificación

- [ ] El modo "Factura Electrónica de Venta" aparece en la tabla.
- [ ] El Software ID coincide con el del portal de producción.
- [ ] El entorno está en modo **Producción** (casilla de pruebas DESACTIVADA).
- [ ] El proceso de certificación está DESACTIVADO.

---

## B.5 Creación y Configuración de Diarios Contables

### ¿Qué es?

Los diarios contables son los "cuadernos" donde Odoo registra las transacciones. Para facturación electrónica colombiana, necesita diarios específicos para cada tipo de documento, vinculados a la resolución DIAN y con la Clave Técnica correspondiente.

### ¿Dónde se configura?

**Ruta:** Contabilidad → Configuración → Diarios

---

### B.5.1 Diario de Facturas de Venta (Obligatorio)

Este es el diario principal donde se registrarán todas las facturas electrónicas de venta.

1. Haga clic en **"Nuevo"**.
2. Complete la pestaña principal:

| Campo | Valor |
|-------|-------|
| **Nombre del Diario** | Facturas de Venta Electrónicas |
| **Tipo** | Ventas |
| **Código Corto** | `FE` |

3. Vaya a la pestaña **"Ajustes Avanzados"**:
   - Active la opción **"Facturación electrónica"** y seleccione **UBL 2.1 (Colombia)**.

4. Ingrese los datos de la resolución DIAN:

| Campo | Valor | Paso de origen |
|-------|-------|----------------|
| **Número de Resolución DIAN** | Su número de resolución | A.5 |
| **Fecha resolución desde** | Fecha de inicio de vigencia | A.5 |
| **Fecha resolución hasta** | Fecha de fin de vigencia | A.5 / A.6 |
| **Rango desde** | Primer número autorizado | A.5 |
| **Rango hasta** | Último número autorizado | A.5 |
| **Clave Técnica** | Hash alfanumérico largo | A.6 — clic en la fila de asociación |

5. En la pestaña **"Asientos Contables"**:
   - Configure las cuentas de ingreso y pagos pendientes según su PUC.

6. Haga clic en **Guardar**.

> [!IMPORTANT]
> **La Clave Técnica es obligatoria.** Sin ella, Odoo no puede generar el CUFE (Código Único de Factura Electrónica) y la DIAN rechazará la factura con error **FAD06**.

---

### B.5.2 Diario de Notas Crédito (Obligatorio)

Las Notas Crédito se usan para anular o corregir facturas emitidas.

1. Cree un nuevo diario:

| Campo | Valor |
|-------|-------|
| **Nombre del Diario** | Notas Crédito Electrónicas |
| **Tipo** | Ventas |
| **Código Corto** | `NC` |

2. En **Ajustes Avanzados**:
   - Active **"Facturación electrónica"** → **UBL 2.1 (Colombia)**.
   - Ingrese la **misma resolución** del diario de facturas de venta.

> [!NOTE]
> Las Notas Crédito **no requieren resolución independiente**. Comparten la resolución de la factura de venta. Solo necesita otra resolución si su contador lo indica explícitamente.

3. Haga clic en **Guardar**.

---

### B.5.3 Diario de Notas Débito (Si aplica)

Las Notas Débito se usan para ajustes al valor de facturas emitidas (ej. intereses de mora, ajustes de precio).

1. Cree un nuevo diario:

| Campo | Valor |
|-------|-------|
| **Nombre del Diario** | Notas Débito Electrónicas |
| **Tipo** | Ventas |
| **Código Corto** | `ND` |

2. En **Ajustes Avanzados**:
   - Active **"Facturación electrónica"** → **UBL 2.1 (Colombia)**.
   - Ingrese la **misma resolución** del diario de facturas de venta.

3. Haga clic en **Guardar**.

> [!TIP]
> No todas las empresas necesitan Notas Débito desde el inicio. Si no está seguro, puede crear este diario más adelante cuando lo necesite.

---

### B.5.4 Diario de Documentos Soporte (Si aplica)

Si su empresa realiza compras a **personas naturales no obligadas a facturar** (ej. agricultores, artesanos, prestadores de servicios informales), necesita emitir Documentos Soporte electrónicos.

> [!IMPORTANT]
> **Resolución independiente requerida.** Los Documentos Soporte NO comparten la resolución de las facturas de venta. Debe solicitar una resolución separada en MUISCA con un prefijo distinto (ej. `DS`), y asociarla en el portal de producción para obtener su propia Clave Técnica.

1. Cree un nuevo diario:

| Campo | Valor |
|-------|-------|
| **Nombre del Diario** | Documentos Soporte Electrónicos |
| **Tipo** | Compras |
| **Código Corto** | `DS` |

2. En **Ajustes Avanzados**:
   - Active **"Facturación electrónica"** → **UBL 2.1 (Colombia)**.
   - Ingrese la resolución **independiente** de Documentos Soporte.
   - Ingrese la Clave Técnica obtenida al asociar el prefijo `DS` en el portal de producción.

3. Haga clic en **Guardar**.

### Tabla resumen de diarios

| Diario | Tipo | Código | Resolución | Clave Técnica | ¿Obligatorio? |
|--------|------|--------|------------|---------------|----------------|
| Facturas de Venta | Ventas | FE | Propia (A.5) | Propia (A.6) | ✅ Siempre |
| Notas Crédito | Ventas | NC | Misma de FE | Misma de FE | ✅ Siempre |
| Notas Débito | Ventas | ND | Misma de FE | Misma de FE | Según necesidad |
| Documentos Soporte | Compras | DS | Independiente | Independiente | Solo si compra a no obligados |

### Verificación

- [ ] El diario FE tiene resolución, rango y Clave Técnica configurados.
- [ ] El diario NC está creado con facturación electrónica activa.
- [ ] El diario ND está creado (si aplica).
- [ ] El diario DS está creado con resolución independiente (si aplica).
- [ ] Todos los diarios tienen la columna "Facturación electrónica" visible y activa.

---

## B.6 Verificación de Contactos (Clientes y Proveedores)

### ¿Qué es?

La DIAN valida los datos del **receptor** (cliente) en cada factura electrónica. Si un dato falta o es incorrecto, la factura es rechazada. Esta verificación debe hacerse **antes** de emitir la primera factura.

### ¿Dónde se configura?

**Ruta:** Contactos → seleccionar el contacto → editar

### Datos obligatorios por contacto

| # | Campo | Ejemplo | ¿De dónde sale? | ⚠️ Trampa |
|---|-------|---------|-----------------|-----------|
| 1 | **Tipo de Documento** | NIT (31) / CC (13) / CE (22) | RUT del cliente | Debe ser el tipo correcto |
| 2 | **Número de Identificación** | `901234567` | RUT del cliente | SIN dígito de verificación |
| 3 | **Dígito de Verificación** | `3` | Calculado por Odoo | Verificar que coincida con el RUT del cliente |
| 4 | **Razón Social / Nombre** | Exacto del RUT | RUT del cliente casilla 35 | Error FAJ44b si difiere |
| 5 | **Ciudad** | Seleccionar del catálogo | RUT del cliente | **NUNCA escribir a mano** — debe tener código DANE |
| 6 | **Departamento** | Seleccionar del catálogo | RUT del cliente | Se autocompleta con la ciudad |
| 7 | **Código Postal** | `110111` | RUT del cliente | — |
| 8 | **Dirección (calle)** | `Cra 7 # 45-12` | RUT del cliente | — |
| 9 | **País** | Colombia | — | — |
| 10 | **Responsabilidad Fiscal** | Ej. `O-48` o `R-99-PN` | RUT del cliente | Ver tabla abajo |
| 11 | **Email** | Para envío de la factura | Cliente | — |

### Responsabilidad fiscal del receptor

| Código | ¿Cuándo usarlo? |
|--------|-----------------|
| O-48 Responsable de IVA | El cliente es responsable de IVA |
| R-99-PN No responsable | El cliente NO es responsable de IVA (persona natural) |
| O-13 Gran contribuyente | Si la DIAN lo designó como tal |
| O-15 Autorretenedor | Si aplica |

> [!CAUTION]
> **Regla de Oro #10 — TaxScheme SIEMPRE es 01 (IVA).**
> La no-responsabilidad se indica con el campo `TaxLevelCode` (ej. `R-99-PN`), **NUNCA** cambiando el TaxScheme a `ZZ` o `No Aplica`. Si el TaxScheme está en `ZZ`, la DIAN rechazará con error **FAK41**.
>
> ```
> ❌ INCORRECTO: TaxScheme = ZZ, TaxSchemeName = "No Aplica"
> ✅ CORRECTO:   TaxScheme = 01, TaxSchemeName = "IVA", TaxLevelCode = "R-99-PN"
> ```

### Consumidor Final

Para ventas a consumidores finales (sin RUT), puede usar un contacto genérico con:

| Campo | Valor |
|-------|-------|
| Tipo de Documento | CC (Cédula de Ciudadanía - 13) |
| Número | `222222222222` (consumidor genérico) |
| Nombre | Consumidor Final |
| Tipo de Persona | Persona Natural (`AdditionalAccountID = 2`) |
| Responsabilidad Fiscal | R-99-PN |

> [!WARNING]
> **AdditionalAccountID:** `1` = Persona Jurídica, `2` = Persona Natural. Usar el tipo incorrecto genera warnings en la respuesta DIAN. Para consumidor final, siempre `2`.

### Verificación

- [ ] El contacto receptor tiene tipo de documento y número de identificación.
- [ ] La razón social coincide con el RUT del cliente.
- [ ] La ciudad fue seleccionada del catálogo (con código DANE).
- [ ] La responsabilidad fiscal está asignada.
- [ ] El TaxScheme es 01/IVA (**no** ZZ).

---

## B.7 Primera Factura Real 🚀

### ¿Qué es?

El momento de la verdad: emitir la primera factura electrónica real en producción y verificar que la DIAN la acepte.

### Paso a paso

1. Vaya a **Contabilidad → Clientes → Facturas → Nuevo**.
2. Seleccione el **diario FE** (Facturas de Venta Electrónicas).
3. Seleccione el **cliente** verificado en la Fase B.6.
4. Agregue al menos **1 línea de producto** con un impuesto IVA.
5. **Verifique todo antes de confirmar:**

| Elemento | Qué verificar |
|----------|--------------|
| Diario | Debe ser `FE` (no otro diario de ventas) |
| Cliente | Debe tener datos DIAN completos (Fase B.6) |
| Impuesto | Debe tener IVA configurado correctamente |
| Dirección de entrega | Debe estar completa (Regla FAJ28) |

> [!TIP]
> **PRE-INV:** Si el módulo `insotech_l10n_co_advanced` está instalado, el sistema interceptará la factura antes de confirmarla para proteger los consecutivos DIAN. Esto es una capa de seguridad adicional.

6. Haga clic en **Confirmar**.
7. Haga clic en **"Enviar e Imprimir"** o el botón de **"Procesar"** para enviar a la DIAN.

### ¿Qué esperar en la respuesta?

Revise el **Chatter** (historial) de la factura. Debería ver la respuesta de la DIAN:

| Campo | ✅ Éxito | ❌ Error |
|-------|---------|---------|
| **StatusCode** | `00` | `99` u otro |
| **IsValid** | `true` | `false` |
| **CUFE** | Hash largo (código único) | Ausente |
| **StatusDescription** | Documento validado | Descripción del error |

### Si la factura es aceptada ✅

¡Felicitaciones! 🎉 Su empresa está facturando electrónicamente en producción. Puede:

- Descargar la **Representación Gráfica** (PDF con QR y CUFE).
- Enviarla al cliente por email.
- Verificar la factura en el **catálogo DIAN** buscando por CUFE.

### Si hay error ❌ — Tabla de diagnóstico rápido

| Error DIAN | Regla | Causa más probable | Cómo solucionarlo |
|-----------|-------|--------------------|--------------------|
| Datos no coinciden con RUT | FAJ44b | Razón social, dirección o NIT del emisor/receptor ≠ RUT | Corregir datos en la ficha de empresa o contacto |
| CUFE incorrecto | FAD06 | Clave Técnica equivocada en el diario | Verificar y corregir la Clave Técnica (Paso A.6) |
| Código inválido en catálogo | FAK41 | TaxScheme = ZZ en vez de 01 | Cambiar a 01/IVA en el contacto receptor |
| Delivery address faltante | FAJ28 | Dirección de entrega incompleta | Completar dirección del contacto (ciudad, depto, postal) |
| Documento duplicado | Regla 90 | Consecutivo ya fue usado anteriormente | Verificar la secuencia del diario — puede necesitar reiniciar |
| Prefijo no coincide | FAB10a | Prefijo del diario ≠ prefijo asociado en DIAN | Corregir código corto del diario |
| ProfileID incompleto | FAD03 | Error interno del módulo | Verificar que `l10n_co_dian` esté actualizado |
| Método pago inválido | FAN02 | Campo de método de pago vacío o incorrecto | Configurar método de pago en la factura |
| AuthorizationProvider faltante | FAB31 | Error interno del módulo | Verificar versión de `l10n_co_dian` |
| QR Code faltante | FAB36 | Error interno del módulo | Verificar versión de `l10n_co_dian` |

> [!TIP]
> Para diagnóstico avanzado, consulte el documento completo de [15 Errores DIAN](../../.agent/skills/base-de-conocimiento/aprendizajes/dian-habilitacion-facturacion-electronica.md) que documenta cada error con ejemplos reales y soluciones.

---

## Solución de Problemas Conocidos

### Error: `product.product_category_goods not found`

**Aplica a:** Instancias Odoo.sh **sin demo data** al usar el habilitador nativo de `l10n_co_dian`.

**Solución:**
1. Active el **modo desarrollador** (Ajustes → barra de URL → `?debug=1`).
2. Vaya a **Ajustes → Técnico → Identificadores Externos**.
3. Clic en **Nuevo** y complete:
   - **Módulo:** `product`
   - **Nombre externo:** `product_category_goods`
   - **Modelo:** `product.category`
   - **ID del Registro:** El ID de la categoría "All" (véalo en la URL al abrir esa categoría).
4. **Guardar** y reintentar la certificación.

### Error: NIT con guiones

**Síntoma:** "El número de identificación contiene '-' pero no es un NIT"

**Solución:** En el campo NIT de la empresa, ingrese **solo el número** sin guiones ni dígito de verificación. Odoo calcula el DV y lo muestra en campo separado.

---

## Resumen: Checklist Final Pre-Facturación

Antes de emitir su primera factura real, verifique que **TODOS** estos elementos estén configurados:

| # | Elemento | Estado |
|---|----------|--------|
| 1 | Módulos `l10n_co_dian` instalados | ☐ |
| 2 | Datos empresa = RUT exacto | ☐ |
| 3 | Certificado .p12 cargado y sin errores | ☐ |
| 4 | Modo de operación en Producción con Software ID correcto | ☐ |
| 5 | Diario FE con resolución, rangos y Clave Técnica | ☐ |
| 6 | Diario NC creado con facturación electrónica | ☐ |
| 7 | Contacto receptor con datos DIAN completos | ☐ |
| 8 | TaxScheme = 01/IVA (no ZZ) en todos los contactos | ☐ |
| 9 | Entorno de Prueba DESACTIVADO | ☐ |
| 10 | Proceso de certificación DESACTIVADO | ☐ |

---

> **Sección anterior:** [PARTE A: Trámites ante la DIAN](./PARTE_A_Tramites_DIAN.md)

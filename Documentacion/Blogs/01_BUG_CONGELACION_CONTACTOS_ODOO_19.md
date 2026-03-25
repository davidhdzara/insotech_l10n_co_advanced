# ¿Tu Odoo 19 se congela al crear Contactos? El Bug Criptográfico de la DIAN y la solución definitiva

Si estás implementando o migrando a Odoo 19 (Localización Colombiana) y de repente, al escribir el Número de Identificación (NIT o Cédula) de un proveedor en el módulo de Contactos, tu pantalla se queda en blanco o arroja un temido `RPC_ERROR`, no estás solo. Se trata de uno de los bugs nativos más frustrantes de esta versión.

Hoy en **InSoTech** queremos desentrañar el origen de este Traceback invisible y compartirte exactamente cómo logramos neutralizarlo en nuestro ecosistema _Advance_ para garantizar operaciones en milisegundos.

### 🔍 El Origen del Mal: Un 'Onchange' Demasiado Reactivo

La capa `l10n_co_dian` de Odoo 19 busca ser muy proactiva. Cuando un usuario teclea un NIT o Cédula, Odoo intenta disparar un evento nativo oculto (`onchange`) para ir a tocar la puerta de la DIAN y autocompletar la Responsabilidad Fiscal del contacto. 

El problema surge con el certificado de firma electrónica (`.p12`). Odoo invoca su módulo criptográfico (`certificate`) para armar la petición SOAP en milisegundos. Sin embargo, si la llave privada (`PEM`) se extrajo del certificado P12 **sin estar protegida por una contraseña en el XML nativo**, la librería `cryptography` de Python integrada en Odoo 19 explota con el siguiente error:

```python
TypeError: Password was given but private key is not encrypted.
```

¿El resultado? El usuario ve un pantallazo blanco (`RPC_ERROR`). Un simple *typo* en una vista de contactos termina derrumbando el ERP.

### 🛡️ La Solución "Zero Huecos" de InSoTech

En InSoTech aplicamos una filosofía de arquitectura clara: **"No permitimos que funciones de validación externa inestables rompan la experiencia de los flujos de creación (UX)".** 

En lugar de hacer modificaciones frágiles a la librería criptográfica nativa (con el riesgo de que la siguiente actualización de Odoo rompa el servidor), desarrollamos un _Monkey-Patch_ defensivo que silencia esta llamada arriesgada de manera atómica.

#### 1. Bypassear la consulta SOAP en vivo
Al crear un módulo custom, interceptamos el método de validación problemática de Odoo 19 (`_l10n_co_dian_onchange_identification_type`).

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('l10n_co_document_type', 'vat')
    def _l10n_co_dian_onchange_identification_type(self):
        # Neuralizamos la llamada letal nativa bloqueando el super()
        for partner in self:
            doc_type = getattr(partner, 'l10n_co_document_type', False)
```

#### 2. Calcular el Dígito de Verificación Localmente
Dado que el objetivo final de esa lenta consulta a la DIAN era obtener y computar información predecible (como el Dígito de Verificación), en InSoTech inyectamos matemáticamente el algoritmo oficial **Módulo-11** en el código base.

Odoo ahora recibe el NIT tecleado, e inmediatamente, **en modalidad Offline**, calcula el DV y refresca el formulario sin consumir ni un solo byte de ancho de banda o arriesgarse a un `Timeout` del certificado PEM.

### 🚀 Resultados

Con este simple principio de evasión asíncrona ("Bypass & Local Computing"):
1. Hemos neutralizado indefinidamente la exposición de certificados sin encriptar ante Peticiones HTTP en caliente.
2. Hemos reducido a latencia cero el alta de nuevos clientes.
3. Lo hicimos inmune a los `AttributeError` o "Renombrado de Campos" constantes que el equipo local de Odoo aplica sorpresivamente en la versión 19.

Implementar ERPs de alto rendimiento en Colombia significa construir código "anti-frágil" (SaaS). Si te enfrentas a una arquitectura predecible, no consumas la nube; cálculalo local.

*¿Tu empresa requiere un ecosistema de Facturación Electrónica estable que resista los "Updates" del Core Oficial y los apagones de la DIAN? Conoce nuestro músculo **InSoTech Advance** en [tu-website-aqui].*

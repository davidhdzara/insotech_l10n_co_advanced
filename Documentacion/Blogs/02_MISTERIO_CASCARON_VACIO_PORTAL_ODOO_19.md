# El misterio del "Cascarón Vacío": Solucionando alertas invisibles en el Portal de Clientes (Odoo 19)

Si eres un desarrollador u operario construyendo un ecosistema B2B (como el **Acuse de Recibo RADIAN** de InSoTech) utilizando el Portal web nativo de Odoo 19, seguramente has chocado contra una pared invisible a la hora de mandarle mensajes o validaciones a tu usuario en pantalla.

El cliente pulsa el botón, el código Python en el backend detecta exitosamente una regla de negocio rota (ej. *"Debes aceptar el mandato legal primero"*), rediriges la URL con tu mensaje de error... ¿Y qué recibe el cliente? **Un bloque rojo flotante, totalmente vacío y estéticamente roto en la parte superior de su pantalla.**

En InSoTech le llamamos el *"Cascarón Vacío"*. Hoy te contamos por qué sucede este capricho de Odoo 19 y cómo nuestra arquitectura _Advance_ lo solucionó para entregar una **UX (Experiencia de Usuario) corporativa y confiable**.

### 🧩 El "Bug" en el Diseño QWeb de Odoo 19

Tradicionalmente, en Odoo, si un controlador HTTP quería advertir al usuario en el portal, devolvía a la vista mediante un query parameter `?error=Mi+Mensaje`. La plantilla base (`portal.portal_record_layout` o `account.portal_invoice_page`) detecta la palabra _error_ y dibuja un bloque rojo de Bootstrap.

**El problema actual:** En los últimos refactors visuales de Odoo 19, esa plantilla espera que el objeto `error` sea tratado primariamente como una lista, un array o un tipo de diccionario renderizado por `kwargs`. Al inyectarle un String HTTP al estilo de la vieja escuela (`request.params.get('error')`), la función de escape `t-esc` de Odoo muchas veces ignora la evaluación de la cadena de texto, dibujando la caja HTML pero **tragándose silenciosamente tu texto**. 

Dejar a un cliente B2B con una caja roja sin texto es la receta perfecta para la desconfianza del usuario.

### 🛡️ El "Namespace Propio": Cómo InSoTech domina el Portal

Nuestra filosofía de ingeniería prohíbe depender de renderizadores volátiles del *framework* cuando se trata de la experiencia del cliente. Para garantizar un portal RADIAN espectacular y robusto, abandonamos las directivas globales de error de Odoo y configuramos un modelo aislado y controlable.

#### 1. Abandona la clave "error"
En tu controlador HTTP (`portal_radian.py`), no utilices las variables reservadas `error` o `warning`. Construye tu propia envoltura de enrutamiento utilizando diccionarios de `werkzeug` e hiper-parámetros propios como `radian_error` o `radian_success`.

```python
# Nuestro parche en InSoTech:
def _redirect_msg(invoice, msg_type, message):
    from werkzeug.urls import url_encode
    url = invoice.get_portal_url()
    # Codificamos correctamente el espacio y los caracteres especiales
    qs = url_encode({msg_type: message}) 
    return request.redirect(f"{url}&{qs}")

# Retornas tu propia variable:
return _redirect_msg(invoice, 'radian_error', 'Firma electrónica rechazada.')
```

#### 2. Dibuja tus propias alertas (El Inyector Bootstrap)
A través de las vistas XML heredadas (`QWeb`), leemos manualmente nuestro variable segura vía `request.params.get('radian_error')` y la forzamos explícitamente dentro de nuestros componentes de Bootstrap aislados. 

De esta forma, desactivamos cualquier heredabilidad conflictiva del layout base de Odoo y garantizamos que la alerta aparezca hermosa, limpia y legible el 100% de las veces.

```xml
<t t-set="radian_error" t-value="request.params.get('radian_error')"/>
<div t-if="radian_error" class="alert alert-danger p-2 small" role="alert">
    <i class="fa fa-exclamation-circle"/> <strong t-esc="radian_error"/>
</div>
```

### 🚀 Despliegue Impecable

Con esta sencilla estrategia de _Aislamiento Paramétrico_, el ecosistema **InSoTech Advance** maneja todas las respuestas, rechazos y validaciones SOAP de la DIAN directamente en la cara del cliente con total fluidez, sin que Odoo silencie nuestros valiosos retornos de error.

*Crear Software as a Service (SaaS) sobre plataformas preexistentes como Odoo no significa someterse a sus errores nativos; significa tener la arquitectura para bypassearlos.*  
*Descubre más sobre cómo potenciamos la facturación B2B en [tu-website-aqui].*

# Configuración de Dominio Raíz en Odoo.sh usando Cloudflare

**Fecha de Registro:** 2026-03-09
**Contexto del Problema:**
Al intentar configurar un dominio raíz (ej. `insotech.it` o `donguapante.com` sin el "www") en Odoo.sh, los gestores de DNS de proveedores tradicionales (como Hostinger o GoDaddy) no permiten crear registros CNAME apuntando a la URL del proyecto en Odoo.sh, exigiendo una dirección IP estática en su lugar para un registro tipo A.

## 🚨 El Problema o Error
Los paneles de control de dominio tradicionales muestran errores como *"You cannot redirect your domain to itself"* o impiden crear redirecciones de la versión sin "www" a la versión con "www".
Además, ya que Odoo.sh **no provee direcciones IP estáticas**, no es posible usar registros tipo A para el dominio raíz, lo que hace imposible que los usuarios entren al sitio web omitiendo el "www" desde un navegador si solo usamos el proveedor original.

## 🔍 Causa Raíz
Este problema se debe a una limitación estricta del protocolo DNS: la especificación oficial dicta que no puede existir un registro `CNAME` en la raíz de un dominio (el *Apex* o `@`), ya que sobrescribiría otros registros esenciales de la zona técnica y de correos electrónicos (como los MX o TXT).
Los proveedores clásicos siguen esta regla al pie de la letra, pero a diferencia de Cloudflare, carecen de tecnologías avanzadas como "CNAME flattenning" y "Edge Page Rules" gratuitas.

## ✅ Solución Adoptada
La solución definitiva y recomendada para plataformas PaaS como Odoo.sh es **delegar la gestión DNS a Cloudflare**.

**Paso a paso de la configuración:**

1. **Crear cuenta y escanear dominio:** 
   Registrarse en [Cloudflare](https://www.cloudflare.com/) (Plan Gratuito), pulsar en "Add a Site" e ingresar el dominio (ej. `insotech.it`). Cloudflare importará automáticamente los registros actuales (A, CNAME, MX, TXT).

2. **Ajuste CRÍTICO en el CNAME `www` (Apagar Proxy):**
   Durante la importación de registros en Cloudflare, buscar el registro `CNAME` que apunta `www` hacia el servidor de Odoo.sh (ej. `miproyecto.odoo.com`).
   * **ACCIÓN OBLIGATORIA:** Desactivar la nube naranja (Proxy status). Debe quedar en **DNS only** (burbuja gris).
   * *Razón:* Odoo.sh genera y administra su propio certificado SSL. Si Cloudflare intenta añadir una capa adicional de encriptación proxy (nube naranja), generará un conflicto de SSL (Error 525 o Too Many Redirects).
   * Nota: Los demás registros A se pueden mantener con la nube naranja (Proxied) sin problema, servirán de ancla.

3. **Copiar Nameservers hacia el Proveedor:**
   Cloudflare asignará dos Nameservers (ej. `greg.ns.cloudflare.com` y `vida.ns.cloudflare.com`). Ingresar a la gestión DNS del proveedor original (Hostinger/GoDaddy) y sustituir los Nameservers por defecto por los provistos por Cloudflare. Guardar y esperar propagación.

4. **Crear la Regla de Redirección Inteligente (Page Rule):**
   En el panel de Cloudflare, navegar a **Rules > Page Rules** y hacer clic en **Create Page Rule**.
   Añadir exactamente esta configuración (respetando asteriscos y variables):
   * **URL:** `tudominio.com/*` (Ej. `insotech.it/*`)
   * **Setting:** Seleccionar `Forwarding URL`
   * **Status Code:** `301 - Permanent Redirect`
   * **Destination URL:** `https://www.tudominio.com/$1` (Ej. `https://www.insotech.it/$1`)
   
Guardar y hacer Deploy de la regla. Con esto, Cloudflare atrapa las solicitudes a la raíz del dominio bajo HTTP o HTTPS y redirige elegantemente cualquier contenido (gracias a la variable `$1`) al subdominio `www`, el cual sí cumple con todos los estándares y carga directo en Odoo.sh.

## 💡 Buenas Prácticas / Cómo evitarlo
* **Siempre iniciar nuevos proyectos en Odoo.sh directamente en Cloudflare.** No intentes luchar contra el proveedor de tu dominio para las redirecciones, delega los DNS a Cloudflare desde el día 1.
* **Respetar el SSL de Odoo.sh:** Jamás enciendas la nube naranja de Cloudflare al registro CNAME principal de tu base de datos Odoo.sh. Odoo hace un excelente trabajo manejando sus certificados Let's Encrypt de forma nativa.
* **Añadir esta guía al manual de pase a producción:** Cada vez que vayas a lanzar un nuevo website para un cliente sobre Odoo.sh, aplica estos mismos 4 pasos.

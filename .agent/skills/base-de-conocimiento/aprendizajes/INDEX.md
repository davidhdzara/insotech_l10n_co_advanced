# Índice de Aprendizajes y Lecciones (InSoTech Knowledge Base)

Aquí se enlista la documentación técnica histórica recabada a lo largo del desarrollo y mantenimiento de la plataforma InSoTech sobre Odoo v19.

### Arquitectura Core y Vistas
- [Configuración de Dominio Raíz (Cloudflare + Odoo.sh)](configuracion-dominio-raiz-cloudflare-odoo-sh.md) // `DNS`, `Domain`, `Odoo.sh`
- [Peligros Críticos: XMLSyntaxError por LXML Mismatches en QWeb](odoo-v19-xml-lxml-parse-mismatch.md) // `XML`, `LXML`, `Crash`
- [Solucionando Error 500 por Strict XML Entities en Snippets](odoo-v19-xml-strict-entities-bull.md) // `XML`, `Snippets`

### Frontend, Theme InSoTech y CSS
- [Error de Loop Infinito en SASS por ColorPlugin nativo Odoo B2B](bug-odoo-v19-colorplugin-infiniteloop.md) // `SASS`, `Compiler`
- [Peligro: Falla de Servidor y Compilación SCSS en Odoo 19 Theme](error-compilacion-scss-odoo19.md) // `SCSS`, `Theme`
- [Tags Dinámicas para el Blog usando QWeb Condicionales](qweb-dynamic-blog-tags-odoo19.md) // `QWeb`, `Blog`, `Tags`

### Seguridad y Controladores Públicos 
- [Evitar Error 403 Forbidden a res.partner en Vistas Públicas QWeb](odoo-v19-blog-403-res-partner-public.md) // `Security`, `res.partner`, `403`
- [Buenas Prácticas: Controladores RPC de Acceso Público](odoo-v19-rpc-controllers-public.md) // `Controllers`, `RPC`, `Public`
- [Sobrescribiendo la Paginación Nativa del Blog vía Python Controller](odoo-v19-blog-custom-pagination-controllers.md) // `Pagination`, `Python`, `Controllers`

### OWL y Comunicación Front-Back (JavaScript)
- [Implementación Cliente-Action RPC en Framework OWL (Frontend)](odoo-v19-owl-client-action-rpc.md) // `OWL`, `JS`, `RPC`
- [Ejecutando SOQL contra APIs Externas (Socrata) vs Odoo Async Queues](api-socrata-soql-timeout-vs-q.md) // `API`, `Timeouts`, `Async`

### Módulos Funcionales
- [Estándares y Hacks sobre las plantillas de Cotización Saas B2B](estandar-cotizacion-b2b-odoo.md) // `Sales`, `QWeb`
- [Herencia de Vistas en el Módulo CRM de Odoo (IAP Componentes)](odoo-v19-crm-iap-herencia.md) // `CRM`, `Views`

### Contabilidad y Productos
- [Parametrización de Productos y Contabilidad InSoTech](parametrizacion-productos-contabilidad-insotech.md) // `Accounting`, `Products`, `Pricing`

### 🆕 Migración y Compatibilidad V19 (SaaS Server)
- [sale_subscription como dependencia rompe builds con l10n_co](odoo-v19-sale-subscription-l10n-co-build-fail.md) // `Build`, `l10n_co`, `Dependencies` // 📝⭐⭐⭐⭐⭐
- [category_id eliminado de res.groups — usar privilege_id](odoo-v19-privilege-id-replaces-category-id.md) // `Security`, `Groups`, `Migration` // 📝⭐⭐⭐⭐⭐
- [_sql_constraints eliminado — usar models.Constraint con prefijo _](odoo-v19-models-constraint-underscore-prefix.md) // `ORM`, `Constraints`, `Migration` // 📝⭐⭐⭐⭐⭐
- [Deprecaciones en Controllers (jsonrpc) y Search Views (group attrs)](odoo-v19-controller-jsonrpc-search-view-group.md) // `Controllers`, `Views`, `Deprecation` // 📝⭐⭐⭐⭐
- [mail.thread obligatorio para chatter y tracking](odoo-v19-mail-thread-chatter-tracking.md) // `mail`, `tracking`, `chatter` // 📝⭐⭐⭐

---
## Leyenda Blog Potential
- 📝⭐⭐⭐⭐⭐ = **Publicar con prioridad** — problema universal, poca documentación existente
- 📝⭐⭐⭐⭐ = **Buen candidato** — afecta a muchos desarrolladores
- 📝⭐⭐⭐ = **Material complementario** — útil pero ya hay documentación oficial

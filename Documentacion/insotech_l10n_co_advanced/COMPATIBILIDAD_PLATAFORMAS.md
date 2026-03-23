# Compatibilidad Multi-Plataforma — insotech_l10n_co_advanced

- **Fecha:** 2026-03-23
- **Módulo:** `insotech_l10n_co_advanced`
- **Versión:** 19.0.1.1.0

## Matriz de Compatibilidad

| Plataforma | Compatible | Dependencia Crítica | Notas |
|---|:-:|---|---|
| **Odoo.sh Enterprise** | ✅ | `l10n_co_dian` (incluido) | Plataforma actual de InSoTech |
| **Odoo On-Premise Enterprise** | ✅ | `l10n_co_dian` (incluido en Enterprise) | Requiere instalación manual |
| **Odoo Community** | ❌ | `l10n_co_dian` **NO existe** en Community | Ver alternativas abajo |

## Dependencias del Módulo

```python
'depends': [
    'account',              # ✅ Community + Enterprise
    'l10n_co_edi',          # ⚠️  Solo Enterprise
    'l10n_co_dian',         # ⚠️  Solo Enterprise
    'insotech_core',        # ✅ Propio InSoTech
    'insotech_dian_wizard', # ✅ Propio InSoTech
],
```

> **`l10n_co_dian` es Enterprise-only.** La facturación electrónica colombiana nativa de Odoo solo existe en la versión Enterprise. Sin este módulo, no hay XML DIAN, ni firma digital, ni CUFE.

## Detalles por Plataforma

### Odoo.sh Enterprise ✅
```
Estado: PRODUCCIÓN ✅ (probado 2026-03-23)
```
- El módulo se copia como directorio hijo directo del repo
- Push a rama `produccion` → build automático
- Actualizar módulo desde Aplicaciones tras cada despliegue
- `l10n_co_dian` viene preinstalado

### Odoo On-Premise Enterprise ✅
```
Estado: Compatible (no probado en on-premise específico)
```
**Instalación:**
```bash
cd /opt/odoo/custom-addons/
git clone --branch 19.0 git@github.com:davidhdzara/insotech_l10n_co_advanced.git
# Agregar al addons_path en odoo.conf
sudo systemctl restart odoo
# En Odoo: Aplicaciones → Buscar "insotech" → Instalar
```

**Consideraciones on-premise:**
- Verificar que `l10n_co_edi` + `l10n_co_dian` estén instalados
- Certificado DIAN (.p12) debe estar accesible por el servidor
- El reloj del servidor debe estar sincronizado (NTP) — DIAN valida timestamps
- Port 443 saliente debe estar abierto para SOAP calls a DIAN

### Odoo Community ❌
```
Estado: NO COMPATIBLE (por diseño)
```
**¿Por qué no funciona?**
- `l10n_co_dian` no existe en Community Edition
- Sin `l10n_co_dian` no hay: generación XML UBL 2.1, firma digital, conexión SOAP, CUFE
- Nuestro módulo HEREDA de `l10n_co_dian` — sin él, Odoo no puede instalar el módulo

**¿Es posible agregarlo en el futuro?**
Técnicamente sí, pero requeriría reemplazar toda la funcionalidad de `l10n_co_dian`:
1. Generación XML UBL 2.1 Colombia
2. Firma digital (certificado .p12)
3. Conexión SOAP con web services DIAN
4. Cálculo de CUFE/CUDE
5. Procesamiento de ApplicationResponse

> **Estimación:** +400 horas de desarrollo. No recomendado — es más rentable que los clientes usen Enterprise.

## Funcionalidades que SÍ son Multiplataforma

| Feature | Depende de `l10n_co_dian`? | Community? |
|---|:-:|:-:|
| Protección consecutivos (PRE-INV) | Sí (detecta diarios DIAN) | ❌ |
| Transformación nombre FE1 | Sí (envío vía DIAN) | ❌ |
| Contador de resolución | Sí (lee campos DIAN del diario) | ❌ |
| Validación de licencia SaaS | No (insotech_core) | ✅ |
| Banners y botones UI | No (vistas genéricas) | ✅ |
| Sanitización NIT GetNumberingRange | Sí (método de l10n_co_dian) | ❌ |

## 💡 Regla de oro #22
**El módulo `insotech_l10n_co_advanced` es intrínsecamente Enterprise.** Nunca prometer compatibilidad Community. Si un cliente tiene Community, la recomendación es migrar a Enterprise para facturación electrónica colombiana.

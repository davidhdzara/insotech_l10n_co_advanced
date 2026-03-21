# l10n_co_dian_advanced

## Colombia - DIAN Advanced EDI (Odoo 18)
### *Zero-gap Electronic Invoicing — Decoupled Sequence Architecture*

---

### Qué hace este módulo

Extiende el módulo nativo `l10n_co_dian` de Odoo 18 para solucionar el problema crítico más reportado en Colombia: **pérdida de consecutivos de facturación DIAN por rechazos técnicos**, un comportamiento que viola la obligatoriedad de la numeración continua de la Resolución DIAN.

| Característica | Odoo 18 Nativo | Con este módulo |
|---|---|---|
| Consecutivo quemado al confirmar | ✅ Sí (aunque la DIAN rechace) | ❌ No — solo se consume si la DIAN aprueba |
| Timeout MUISCA colapsado | ❌ Pantalla congelada | ✅ 8s timeout → aviso → rollback automático |
| Contingencia sin DIAN | ❌ No factura | ✅ Prefijo `PC-` alternativo activo |
| Reintento automático nocturno | ❌ Manual | ✅ Cron configurable cada N horas |

---

### Arquitectura: La Regla de Oro

El método `_post()` de `account.move` se sobreescribe para:
1. Generar el XML UBL 2.1 (usando el motor nativo de `l10n_co_dian`)
2. Enviar el XML a la DIAN con `timeout=8s`
3. **Solo si la DIAN responde OK** → Odoo toma el número de la Resolución (`ir.sequence`) y lo estampa
4. Si la DIAN falla/rechaza → `UserError` → Postgres hace Rollback automático → La factura vuelve a Borrador. El `FE-XXX` no se consumió.

---

### Versiones soportadas

| Versión Odoo | Estado |
|---|---|
| 18.0 | ✅ Activo (rama `18.0`) |
| 19.0 | ⏳ Planificado (rama `19.0` al lanzar) |

---

### Instalación (Odoo.sh)

1. Agregar este repositorio como sub-módulo o dependencia en el proyecto Odoo.sh.
2. Instalar el módulo `l10n_co_dian_advanced` desde el menú de Aplicaciones.
3. En cada Diario de Ventas, configurar la Resolución DIAN, el prefijo y los rangos.
4. Activar la Acción Programada *"Reintento Automático Facturas DIAN"* y parametrizar el intervalo deseado (recomendado: cada 3 horas, máximo 5 intentos por factura).

---

### Estructura del Módulo

```
l10n_co_dian_advanced/
├── __manifest__.py           # Dependencias y configuración del módulo
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── account_move.py       # Override _post() — Core de la arquitectura
│   └── account_journal.py    # Campo is_dian_contingency y config resolución
├── data/
│   └── ir_cron_data.xml      # Acción programada de reintento nocturno
├── security/
│   └── ir.model.access.csv
├── views/
│   └── account_journal_views.xml  # UI del Modo Contingencia en el Diario
├── tests/
│   ├── __init__.py
│   └── test_dian_rejection.py     # Test obligatorio: secuencia NO avanza en rechazo
└── static/description/
    └── icon.png
```

---

### Licencia y Comercialización

*   **Licencia:** OPL-1 (Odoo Proprietary License)
*   **Modelo de Venta 1:** Pago Único por versión en Odoo Apps Store — $150 USD a $300 USD
*   **Modelo de Venta 2:** Suscripción SaaS Anual — $250 USD a $400 USD (incluye Fase 2: WhatsApp, RUES Auditor, Radian)

---

### Hoja de Ruta (Roadmap)

Ver `docs/ROADMAP.md` para el detalle completo de las Fases 1, 2 y 3.

# l10n_co_dian_advanced — Instrucciones de Git y GitHub

## Estructura de Ramas
Este repositorio sigue la convención estándar de Odoo Community:

| Rama | Propósito |
|---|---|
| `18.0` | Producción para Odoo 18 |
| `19.0` | (Futuro) Producción para Odoo 19 |
| `18.0-feature/fase-1-mvp` | Feature branch para desarrollo activo Fase 1 |
| `18.0-feature/fase-2-automation` | Feature branch para WhatsApp, RUES, Radian |

---

## Pasos para publicar en GitHub (Primera vez)

1. **Crear el repositorio en GitHub** (hazlo PUBLIC si vas a venderlo en Odoo Apps Store, o PRIVATE para venta directa):
   Ve a github.com/new y crea un repositorio llamado `l10n_co_dian_advanced`.

2. **Inicializar Git localmente** (ejecutar desde `/home/david/odoo-projects/l10n_co_dian_advanced/`):

```bash
git init
git remote add origin https://github.com/davidhdzara/l10n_co_dian_advanced.git
git checkout -b 18.0
git add .
git commit -m "chore: initial module scaffold l10n_co_dian_advanced v18.0.1.0.0"
git push -u origin 18.0
```

3. **Configurar la rama `18.0` como rama por defecto** en los ajustes del repositorio de GitHub.

---

## Cómo agregar este módulo en Odoo.sh (Como Sub-módulo)

En el proyecto Odoo.sh de tu cliente, ve a la pestaña "Submódulos" y agrega:
- **URL del repositorio:** `https://github.com/davidhdzara/l10n_co_dian_advanced.git`
- **Rama:** `18.0`
- Odoo.sh sincronizará automáticamente el código cada vez que hagas push a esa rama.

---

## Migración a Odoo 19 (Cuando sea el momento)

1. Crear rama nueva desde la última versión estable: `git checkout -b 19.0 18.0`
2. En `__manifest__.py`, cambiar version a `19.0.1.0.0` y la clave `version` del `depends` si aplica.
3. Ejecutar la suite de tests (`test_dian_rejection.py`) para validar que la intercepción de `_post()` sigue funcionando.
4. Si Odoo cambió la firma del método `_post()` en la v19, ajustar la herencia en `models/account_move.py`.
5. El motor XML de UBL 2.1 y el webservice DIAN lo maneja `l10n_co_dian` (mantenido por Odoo SA) — no necesitas tocar esa parte.
6. Hacer push a la rama `19.0` y notificar a los clientes con suscripción activa.

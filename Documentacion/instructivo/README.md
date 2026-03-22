# Guía Maestra: Facturación Electrónica DIAN — Odoo 19

> Versión: 1.0 | Inicio: Marzo 2026 | Autor: Insotech S.A.S.

Guía completa de punta a punta para configurar facturación electrónica DIAN en Odoo 19 como Software Propio. Desde los trámites legales ante la DIAN hasta la operación diaria.

---

## Estructura del Instructivo

| Parte | Documento | Estado | Descripción |
|-------|-----------|--------|-------------|
| **A** | [PARTE_A_Tramites_DIAN.md](./PARTE_A_Tramites_DIAN.md) | ✅ Completo | Trámites ante la DIAN (Portal MUISCA) |
| **B** | PARTE_B_Configuracion_Odoo.md | 🔜 Próximo | Configuración en Odoo 19 (Fases 1-9) |
| **C** | PARTE_C_Operacion_Diaria.md | 📋 Pendiente | Operación diaria y troubleshooting |
| **APX** | APENDICES.md | 📋 Pendiente | Errores DIAN, limitaciones, glosario, checklist |

---

## Flujo General

```mermaid
flowchart TD
    A1[A.1 Actualizar RUT\nCódigo 52] --> A2[A.2 Certificado .p12\nFirma Digital]
    A2 --> A3[A.3 Portal de\nHabilitación DIAN]
    A3 --> A4[A.4 Software Propio\nSoftware ID / PIN / Test Set ID]

    A4 --> B1[Fase 1: Instalar Módulos]
    B1 --> B2[Fase 2: Configurar Empresa]
    B2 --> B3[Fase 3: Subir .p12]
    B3 --> B4[Fase 4: Modos de Operación]
    B4 --> B5[Fase 5: Diarios Contables]
    B5 --> B6[Fase 6: Set de Pruebas]

    B6 --> A5[A.5 Solicitar Resolución]
    A5 --> A6[A.6 Asociar Rangos\nClave Técnica]
    A6 --> B7[Fase 7: Paso a Producción]
    B7 --> B8[Fase 8: Contactos]
    B8 --> B9[Fase 9: Módulo Insotech]
    B9 --> C1[🎉 Facturar]

    style A1 fill:#FF6B35,color:#fff
    style A2 fill:#FF6B35,color:#fff
    style A3 fill:#FF6B35,color:#fff
    style A4 fill:#FF6B35,color:#fff
    style A5 fill:#FF6B35,color:#fff
    style A6 fill:#FF6B35,color:#fff
    style B1 fill:#004E89,color:#fff
    style B2 fill:#004E89,color:#fff
    style B3 fill:#004E89,color:#fff
    style B4 fill:#004E89,color:#fff
    style B5 fill:#004E89,color:#fff
    style B6 fill:#004E89,color:#fff
    style B7 fill:#004E89,color:#fff
    style B8 fill:#004E89,color:#fff
    style B9 fill:#004E89,color:#fff
    style C1 fill:#2ECC71,color:#fff
```

**Leyenda:** 🟠 Trámites DIAN (Parte A) → 🔵 Configuración Odoo (Parte B) → 🟢 ¡Listo!

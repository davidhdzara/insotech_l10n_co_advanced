# Estándar de Cotización B2B Odoo: Pagos y Exclusiones (Scope Creep)

**Fecha de Registro:** 2026-03-09
**Contexto del Problema:**
Durante el rediseño de las plantillas PDF Premium para el Quote Builder de Odoo (Encabezado y Footer), se identificó la necesidad de proteger a InSoTech financiera y operativamente mediante el uso explícito de lenguaje agnóstico ("paraguas") aplicable a cualquier módulo Odoo, mitigando el *Scope Creep* (Corrupción del Alcance) y mejorando el flujo impositivo de un ERP.

## 🚨 El Problema o Riesgo
En implementaciones Odoo u otros ERPs, los presupuestos colapsan frecuentemente por tres factores:
1.  **Asunción de Módulos:** El cliente asume que un flujo no estipulado en la oferta económica comercial está incluido por considerarlo "Básico".
2.  **Basura Histórica:** El cliente espera que la consultora ordene, limpie manualmente o descuadre su histórico contable o de inventario.
3.  **Flujo de Caja Impositivo:** Iniciar un proyecto B2B con un pago inicial del 50% genera un fuerte impacto en el flujo de caja debido a retenciones e IVA inmediatos que deben ser asumidos sin que la estabilización de operaciones haya iniciado verdaderamente.

## 🔍 Causa Raíz
La falta de "Muros de Exclusiones" explícitos en los Footers B2B de las empresas SaaS y el uso de estructuras de pago simplistas (50/50 o 50/30/20) en lugar de esquemas orientados a hitos de adopción de software.

## ✅ Solución Adoptada (Estándar InSoTech)

### 1. Sistema de Inversión en 4 Hitos (Regla 20/30/30/20)
Toda cotización, sin importar el número de horas o módulos, se recomienda regirse por esta tabla de facturación referenciada explícitamente en el Footer Premium B2B:
- **20% Anticipo y Kick-off:** Firma y blueprint (Optimiza carga impositiva inicial).
- **30% Cierre de Parametrización:** Entrega técnica de módulos y modelo de datos base importado.
- **30% Aprobación en Staging (Capacitación):** Validación de flujos en QA y transferencia al equipo core.
- **20% Go-Live a Producción:** Salida en vivo y firma de aceptación total.

### 2. Muro de Exclusiones Universales
El componente del pie de página (Page 2) **siempre debe incluir las siguientes exclusiones** de forma inmodificable, sin hacer mención a nombres de módulos específicos para que funcionen como escudo legal en toda la suite Odoo:
*   Limpieza o digitación manual de data histórica desorganizada.
*   Cierres contables o migración de saldos dinámicos de años anteriores (solo subida de saldos iniciales del corte contable provistos en Excel).
*   Desarrollos a medida, botones, flujos, o reportes no estipulados explícitamente en las líneas o requerimientos de cambio (CR).
*   Soporte IT sobre hardware legacy local o administración de Workspace/Exchange ajeno a Odoo.

## 💡 Buenas Prácticas / Cómo evitarlo
*   **Dictamen Arquitectónico:** Obligar siempre al diseño de la caja: *"Designación de Responsable del Cliente"* dentro del PDF. Todo proyecto Odoo **exige** un Project Manager único del lado del cliente para bloquear el fenómeno de peticiones descentralizadas de su equipo base que alteran el *Blueprint* técnico inicial (Consenso vs Múltiples voces).

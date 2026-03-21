# Instructivo de Usuario: Facturación Electrónica Insotech Avanzada (Odoo 19)

## ¿Qué hace este módulo?

Evita que se pierdan números de consecutivo de la resolución DIAN cuando una factura electrónica es rechazada por errores (NIT inválido, correo mal formado, datos incorrectos).

---

## Flujo de Facturación (Sin saltos de numeración)

### 1. Crear y Confirmar

Cree su factura de cliente normalmente. Al confirmar:
- La factura queda con un código temporal: **PRE-INV/2026/00001**
- Aparece un **banner amarillo** indicando que está pendiente de validación DIAN
- La contabilidad se registra normalmente — no hay impacto contable

### 2. Enviar a la DIAN

Al enviar la factura a la DIAN (botón "Enviar"):

- **Si la DIAN acepta**: El código temporal cambia automáticamente al número oficial del diario (ej. `INV/2026/00001`). El banner desaparece.
- **Si la DIAN rechaza**: La factura conserva el código temporal. Aparece un **banner rojo** con instrucciones. Corrija el error y use el botón **"Reintentar Envío DIAN"**.

### 3. Facturas rechazadas

Si la DIAN rechaza su factura:
1. Revise el motivo del rechazo en el **historial (chatter)** de la factura.
2. Corrija el error (datos del cliente, NIT, dirección, etc.).
3. Haga clic en **"Reintentar Envío DIAN"**.
4. **No se pierde ningún consecutivo** de la resolución.

---

## Elementos visuales

| Elemento | Significado |
|---|---|
| 🟡 Banner amarillo | La factura está pendiente de validación DIAN |
| 🔴 Banner rojo | La DIAN rechazó la factura — corrija y reintente |
| Sin banner | La factura fue aceptada por la DIAN o no aplica EDI |

---

## Botones disponibles

| Botón | ¿Cuándo aparece? | ¿Quién puede usarlo? |
|---|---|---|
| **Reintentar Envío DIAN** | Cuando la factura fue rechazada | Cualquier usuario con permisos de facturación |
| **Forzar Aceptación DIAN** | Cuando está pendiente o rechazada | Solo administradores contables |

> **Nota sobre "Forzar Aceptación DIAN"**: Use este botón **solo** si la DIAN aceptó la factura pero el sistema no lo registró automáticamente. Esta es una acción de emergencia.

---

## Preguntas frecuentes

**¿Puedo seguir creando facturas si la licencia Insotech expira?**
Sí. Puede crear y confirmar facturas normalmente. Solo se bloquea el **envío a la DIAN**.

**¿Qué significan los códigos PRE-INV?**
Son nombres temporales internos. No aparecen en el PDF de la factura enviada al cliente. El número oficial se asigna cuando la DIAN acepta.

**¿Puedo ver el número oficial reservado antes de que la DIAN acepte?**
Sí, en modo desarrollador puede ver el campo "Nombre DIAN Reservado" en la factura.

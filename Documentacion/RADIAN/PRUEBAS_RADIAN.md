# Plan de Pruebas — RADIAN InSoTech

> **Proyecto:** InSoTech Localización Colombiana Avanzada
> **Última actualización:** 2026-03-24
> **Entorno:** Odoo.sh staging (`staging_produccion`)

---

## Sprint 0 — Infraestructura Base ✅ Validado

### P0.1: Alerta Certificado Digital
| # | Prueba | Cómo verificar | Resultado esperado | Estado |
|---|--------|----------------|---------------------|--------|
| 1 | Fecha de vencimiento se muestra | Ajustes → InSoTech → Certificado Digital DIAN | Muestra fecha + días restantes | ✅ |
| 2 | CRON ejecuta sin error | Técnico → Acciones Planificadas → "Verificar Vencimiento Certificado DIAN" → Ejecutar manual | Completa sin error | ✅ |
| 3 | No alerta si >90 días | Verificar chatter de la empresa tras CRON | No hay mensaje publicado | ✅ |
| 4 | Alerta ≤90 días | ⏳ Esperar julio 2026 o subir cert de prueba con fecha cercana | Publica aviso 🟢 en chatter | ⏳ |
| 5 | Alerta ≤30 días | ⏳ Necesita cert próximo a vencer | Publica advertencia 🟡 | ⏳ |
| 6 | Alerta ≤7 días | ⏳ Necesita cert próximo a vencer | Publica URGENTE 🔴 | ⏳ |

### P0.2: Selector Vocación de Circulación
| # | Prueba | Cómo verificar | Resultado esperado | Estado |
|---|--------|----------------|---------------------|--------|
| 1 | Selector visible en Ajustes | Ajustes → InSoTech → Configuración RADIAN | Dropdown con 3 opciones | ✅ |
| 2 | Persistencia al cambiar modo | Cambiar a "Todas las facturas a crédito" → Guardar → Recargar | Persiste el cambio | ✅ |
| 3 | Default = "Solo facturas marcadas" | Instalar módulo en empresa nueva | Default correcto | ✅ |

---

## Sprint 1 — Aceptación Tácita + Bloqueo NC/ND ✅ Validado parcial

### P1.1: Calendario Colombiano
| # | Prueba | Cómo verificar | Resultado esperado | Estado |
|---|--------|----------------|---------------------|--------|
| 1 | 18 festivos calculados | Shell: `len(get_colombian_holidays(2026))` | 18 | ✅ |
| 2 | Festivos correctos 2026 | Shell: verificar fechas vs calendario oficial | Coinciden con festivos reales | ✅ |
| 3 | Funciona para cualquier año | Shell: `get_colombian_holidays(2030)` | 18 fechas sin error | ⏳ |
| 4 | Festivo manual no duplica | Agregar festivo que ya existe → verificar `set` | Sin duplicados | ⏳ |

### P1.2: Modelo RADIAN Event
| # | Prueba | Cómo verificar | Resultado esperado | Estado |
|---|--------|----------------|---------------------|--------|
| 1 | Modelo cargado | Shell: `env['insotech.radian.event']._fields.keys()` | Lista todos los campos | ✅ |
| 2 | Crear evento manualmente | Shell: `env['insotech.radian.event'].create({...})` | Crea sin error | ⏳ |
| 3 | Nombre calculado | Crear evento → verificar `name` | Formato `RAD-030/FE1` | ⏳ |

### P1.3: CRON Aceptación Tácita
| # | Prueba | Cómo verificar | Resultado esperado | Estado |
|---|--------|----------------|---------------------|--------|
| 1 | CRON existe y activo | Técnico → Acciones Planificadas → buscar "RADIAN" | Existe, activo, cada 1 día | ✅ |
| 2 | Ejecuta sin error (sin datos) | Ejecutar manualmente | Completa, no crea nada | ✅ |
| 3 | Genera 034 tras 3 días hábiles | Requiere: emitir factura → crear evento 030 manual → esperar o simular | Crea evento 034 + post chatter | ⏳ |
| 4 | No genera 034 si existe 033 | Factura con evento 033 → CRON | No crea nada | ⏳ |
| 5 | No genera 034 si existe 031 | Factura con evento 031 → CRON | No crea nada | ⏳ |
| 6 | Respeta festivos colombianos | Acuse en viernes → deadline debe saltar fines de semana | Deadline = miércoles | ⏳ |

### P1.4: Bloqueo NC/ND Irrevocabilidad
| # | Prueba | Cómo verificar | Resultado esperado | Estado |
|---|--------|----------------|---------------------|--------|
| 1 | NC bloqueada sin override | Factura con evento 033 → crear NC → confirmar | UserError: "No se puede emitir" | ⏳ |
| 2 | NC permitida con override | Asignar grupo RADIAN al usuario → repetir | NC se crea + alerta en chatter | ⏳ |
| 3 | ND bloqueada igual que NC | Factura con evento 034 → crear ND | UserError bloqueante | ⏳ |
| 4 | Factura sin evento → NC normal | Factura sin eventos RADIAN → crear NC | NC se crea sin intervención | ⏳ |

### P1.5: Grupo de Seguridad
| # | Prueba | Cómo verificar | Resultado esperado | Estado |
|---|--------|----------------|---------------------|--------|
| 1 | Grupo existe | Técnico → Grupos → buscar "RADIAN" | Visible | ✅ |
| 2 | Visible en permisos usuario | Ajustes → Usuarios → editar usuario | Checkbox "RADIAN: Permitir NC/ND..." | ✅ |

### P1.6: Modelo Festivos Personalizados
| # | Prueba | Cómo verificar | Resultado esperado | Estado |
|---|--------|----------------|---------------------|--------|
| 1 | Modelo cargado | Shell: `env['insotech.custom.holiday']._fields.keys()` | Lista campos | ✅ |
| 2 | Crear festivo personalizado | Shell o backend: crear registro | Se crea sin error | ⏳ |
| 3 | CRON respeta festivo manual | Agregar festivo + verificar cálculo de días | El festivo se excluye del conteo | ⏳ |

---

## Pruebas E2E — Requieren facturación real

> ⚠️ Estas pruebas requieren emitir facturas reales y crear eventos RADIAN manualmente (dry run).

### PE2E.1: Flujo completo de aceptación tácita
```
1. Emitir factura de venta → DIAN la acepta
2. Crear evento 030 (Acuse de Recibo) manualmente:
   env['insotech.radian.event'].create({
       'move_id': factura.id,
       'company_id': env.company.id,
       'event_code': '030',
       'state': 'done',
       'source': 'manual',
   })
3. Esperar 3 días hábiles (o modificar la fecha del evento al pasado)
4. Ejecutar CRON "RADIAN Aceptación Tácita" manualmente
5. Verificar que se creó evento 034 + mensaje en chatter de la factura
```

### PE2E.2: Flujo de bloqueo NC/ND
```
1. Completar PE2E.1 (factura con evento 034)
2. Crear Nota Crédito sobre esa factura (botón "Agregar Nota de Crédito")
3. Intentar confirmar la NC
4. Sin grupo override → debe bloquearse con UserError
5. Agregar grupo "RADIAN: Permitir NC/ND..." al usuario
6. Repetir → debe permitirse pero con alerta en chatter
```

---

## Leyenda

| Icono | Significado |
|-------|-------------|
| ✅ | Validado con evidencia |
| ⏳ | Pendiente de validar |
| ❌ | Fallo detectado |

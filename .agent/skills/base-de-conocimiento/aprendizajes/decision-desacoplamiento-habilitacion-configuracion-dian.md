# Decisión Arquitectónica: Desacoplamiento Habilitación vs Configuración DIAN

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
El habilitador nativo de Odoo (`l10n_co_dian`) requiere que toda la empresa, productos, categorías y diarios estén configurados ANTES de poder ejecutar el set de pruebas DIAN. Esto genera una cascada de errores (`product_category_goods`, `Obligaciones y Responsabilidades`, `ID de la ciudad`, `NIT con guiones`) que bloquean a usuarios SaaS.

## 🚨 El Problema o Error
```text
# Error 1: product_category_goods
ValueError: External ID not found in the system: product.product_category_goods

# Error 2: Datos empresa incompletos
Operación no válida
- El campo 'Obligaciones y Responsabilidades' es necesario
- El campo 'ID de la ciudad' es necesario
- El número de identificación contiene '-' pero no es un NIT
```

## 🔍 Causa Raíz
El flujo nativo de Odoo **mezcla** dos procesos que deberían ser independientes:

1. **Habilitación**: demostrar a la DIAN que tu software puede generar XMLs válidos
2. **Configuración para producción**: cargar datos reales (empresa, resolución, diarios)

La DIAN no necesita tus datos reales para la habilitación — solo necesita XMLs técnicamente correctos con un NIT, emisor y receptor.

## ✅ Solución Adoptada
Creamos `insotech_dian_wizard` con un habilitador directo que:

1. **Genera XMLs UBL 2.1 con datos emulados** (emisor/receptor ficticios)
2. **Firma con XAdES-BES** usando el certificado real (.p12)
3. **Envía directamente al SOAP DIAN** via `SendTestSetAsync`
4. **No toca ningún dato de Odoo** — cero productos, cero contactos, cero diarios

### Flujo resultante:
```
ANTES (acoplado):                    DESPUÉS (desacoplado):
1. Configurar empresa                1. Pegar 5 credenciales
2. Crear productos                   2. Clic "Iniciar Habilitación"  
3. Crear categorías                  3. ✅ Software habilitado
4. Configurar diarios                4. Configurar Odoo con calma
5. Cargar resolución
6. Iniciar habilitación
7. ❌ Error → volver al paso 1
```

## 💡 Buenas Prácticas / Cómo evitarlo
- **Principio de responsabilidad única**: la habilitación es un proceso independiente de la configuración operativa.
- **No mezclar pre-requisitos técnicos con operativos**: la DIAN solo necesita XMLs válidos para habilitar, no datos reales del contribuyente.
- **Diseñar para el peor caso SaaS**: un cliente nuevo no tiene NADA configurado en Odoo. El módulo debe funcionar igual.
- **Emular en vez de requerir**: si los datos no son verificados por la DIAN en el set de pruebas, no hay razón para exigirlos.

## 📁 Archivos Clave
- `insotech_dian_wizard/services/ubl_generator.py` — genera XMLs emulados
- `insotech_dian_wizard/services/xml_signer.py` — firma XAdES-BES  
- `insotech_dian_wizard/services/soap_client.py` — envío SOAP directo
- `insotech_dian_wizard/services/test_data.py` — datos ficticios

> **📝 Blog Potential:** ⭐⭐⭐⭐⭐ (Máximo — decisión arquitectónica diferenciadora, aplicable a todo integrador Odoo en Colombia)

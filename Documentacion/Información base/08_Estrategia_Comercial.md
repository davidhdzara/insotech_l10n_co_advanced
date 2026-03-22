# Estrategia Comercial — Insotech Localización Avanzada

> **Versión:** 1.0 — Marzo 2026
> **Estado:** Aprobada por Product Owner

---

## Modelos de Precio

### Segmento 1 — PYME Directa (Self-service)

| Plan | Facturas incluidas/mes | Precio mensual |
|---|---|---|
| **Starter** | Hasta 100 | $49,900 COP |
| **Business** | Hasta 500 | $99,900 COP |
| **Enterprise** | Ilimitado | $199,900 COP |
| Excedente (cualquier plan) | Por factura adicional | $150 COP/factura |

> El excedente no bloquea al cliente. Se acumula y se factura a fin de mes.

---

### Segmento 2 — Partners (Revendedores / Consultores contables)

| Plan | Sub-clientes incluidos | Precio mensual |
|---|---|---|
| **Partner** | Hasta 10 | $299,900 COP |
| **Partner Pro** | Hasta 50 | $799,900 COP |
| Sub-cliente adicional | +1 | $29,900 COP/mes |

> El Partner revende el servicio a sus PYMEs a su propio precio ($80K-$120K típico). Margen del Partner: $500K-$900K sobre lo que paga a Insotech.

---

### Segmento 3 — Servicios Profesionales

| Servicio | Precio | Tipo |
|---|---|---|
| **Configuración asistida** (wizard + acompañamiento) | $120,000 COP | Única vez |
| **Paquete soporte** (4 horas) | $80,000 COP | Por paquete |
| **Implementación premium** (certificación DIAN completa + capacitación) | $350,000 - $500,000 COP | Única vez |
| **Soporte prioritario** (respuesta <4h) | $59,900 COP/mes | Recurrente |

---

## Implementación Técnica en el Servidor API

| Campo en `insotech.license` | Starter | Business | Enterprise | Partner |
|---|---|---|---|---|
| `license_type` | payperuse | payperuse | payperuse | partner |
| `max_usage` | 100 | 500 | 0 (ilimitado) | 0 |
| Suscripción Odoo | Mensual | Mensual | Mensual | Mensual |
| Excedente | Sí ($150) | Sí ($150) | N/A | N/A |

---

## Proyección de Ingresos (Conservadora)

### Mes 6

| Segmento | Clientes | Ingreso/mes |
|---|---|---|
| 15 PYMEs Starter | 15 × $49,900 | $748,500 |
| 5 PYMEs Business | 5 × $99,900 | $499,500 |
| 2 Partners | 2 × $299,900 | $599,800 |
| Implementaciones | 10 × $350,000 ÷ 6 | $583,333 |
| Excedentes | ~500 × $150 | $75,000 |
| **Total** | | **$2,506,133** |

### Mes 12

| Segmento | Clientes | Ingreso/mes |
|---|---|---|
| 40 PYMEs (mix) | ~$75,000 promedio | $3,000,000 |
| 5 Partners | 5 × $299,900 | $1,499,500 |
| Soporte prioritario | 10 × $59,900 | $599,000 |
| Excedentes | ~1,500 × $150 | $225,000 |
| **Total** | | **$5,323,500** |

---

## Ventajas Competitivas vs Competencia

| Feature | Insotech | Siigo (~$60K) | Alegra (~$50K) |
|---|---|---|---|
| Protección de consecutivos DIAN | ✅ PRE-INV | ❌ | ❌ |
| Configuración express (wizard) | ✅ 3 clics | ❌ Manual | ❌ Manual |
| Contador de resolución visual | ✅ | ❌ | ❌ |
| Modelo Partner (reventa) | ✅ | ❌ | ❌ |
| Integrado en Odoo ERP | ✅ Nativo | ❌ Externo | ❌ Externo |
| Precio Starter | $49,900 | ~$60,000+ | ~$50,000+ |

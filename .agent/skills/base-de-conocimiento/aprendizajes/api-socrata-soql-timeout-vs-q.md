# API SECOP Socrata: Timeout por consultas Ineficientes ($where LIKE vs $q indexado)

**Contexto:**  
En el desarrollo del *InSoTech SECOP Opportunity Radar*, enfrentamos una de las consecuencias más clásicas de extraer datos desde fuentes gubernamentales abiertas ("Datos Abiertos de Colombia") utilizando su motor Socrata.

Al filtrar contratos mediante la palabra clave (ej. "Software ERP"), el backend de Odoo esperaba recibir la petición en 10, e incluso 45 segundos, solo para acabar abortando con:

```python
Error Interno en ERP: HTTPSConnectionPool(host='www.datos.gov.co', port=443): Read timed out (read timeout=45)
```

## Aprendizaje 1: El uso del operador `LIKE` desatará "Full Table Scans" destructivos en Socrata

Al principio, tratamos de filtrar usando SQL nativo de Socrata (SoQL) con un `% wildcard %`, enviando por parámetro de request:

`$where = "(descripcion_del_proceso like '%Software ERP%' OR nombre_entidad like '%Software ERP%')"`

### Problema del Escaneo Linear (LIKE)
Esta sintaxis obliga al API de Colombia a recorrer **cada dígito, cada carácter** de las decenas de millones de registros buscando si en alguna parte de cualquier posición de texto existe secuencialmente la sub-cadena "Software ERP".
Al toparse con recursos finitos, Socrata agota la memoria, entra en "hang" eterno, interrumpiendo jamás la respuesta y forzando a que Odoo en su controlador arroje Timeout.

---

## Aprendizaje 2: Socrata expone un motor nativo `Full-Text Search` con el Parámetro `$q`

Toda recolección y búsqueda B2B donde el usuario provee palabras libres que podrían ser un extracto de una frase más grande, jamas debe hacerse usando `LIKE %`.

Socrata, al igual que Elasticsearch o motores potentes, pre-indexa el contenido tabular en mapas semánticos usando el parámetro **`$q`**.

**Solución 1: Mudar la sentencia SQL a Búsqueda Full-Text (De 45+ segs a 0.5 segs)**

**Incorrecto (Odoo Backend Timeout) ❌**
```python
import requests
# Se intentó buscar usando condicionales string y dobles porcentajes.
donde = "(descripcion_del_proceso like '%Software ERP%')"
requests.get(url, params={'$limit': 20, '$where': donde})
```

**Correcto (Respuestas en Milisegundos) ✅**
```python
import requests
# Usando la búsqueda indexada de Socrata
# Nota: Funciona simultáneamente sobre todas las columnas relevantes soltando la sintaxis engorrosa.
requests.get(url, params={'$limit': 20, '$q': 'Software ERP'})
```

**Resultado Final:**
1. **Velocidad abismalmente superior.**
2. **Resiliencia ante errores sintácticos o URL-enconding (%25):** El parámetro `$q` tolera caracteres especiales y espacios sin desatar corrupciones o Full-Scans en la DB.
3. **Mejor correlación semántica:** "Software ERP" pre-filtra por peso, mientras que "LIKE" habría forzado la frase a ser estrictamente contigua. Alguien que busca "ERP" no quiere encontrar resultados que contengan la palabra "CuERPo". `$q` previene esto al entender límites de palabras en bases B2B.

# Inicialización de Funciones RPC en Client Actions (OWL - Odoo V19)

**Contexto:**  
Al desarrollar Módulos de Frontend puro (específicamente Client Actions a pantalla completa sin depender de FormViews o KanbanViews) dentro de la arquitectura más estricta de Odoo V19 utilizando OWL 2, es frecuente encontrarse con crashes fatales en la carga de componentes vinculados a las llamadas del servidor:

```js
UncaughtPromiseError > OwlError
Uncaught Promise > An error occured in the owl lifecycle
TypeError: rpc is not a function
```

## Aprendizaje: No inyectar `rpc` vía `useService` en métodos de ciclo de vida (`setup()`) para Client Actions puros

En versiones tempranas o dentro de componentes que nacen amarrados al WebClient tradicional (donde el entorno ya está pre-cargado con el registro de servicios), los desarrolladores asumen que pedir `this.rpc = useService("rpc")` en el método `setup()` del componente raíz es seguro.

Sin embargo, para las **Client Actions puros (registrados como ir.actions.client en V19):**
El marco de trabajo de UI dispara la instanciación de la acción del cliente de una manera en la que los servicios dependientes aún no se han provisto al Contexto o Registry del componente al momento del `setup()`. Pedir el servicio RPC global usando un Hook asíncrono en ese instante exacto provoca que el componente OWL aborte su ciclo de vida y bloquee el renderizado con un fallo catastrófico (ciclo `An error occured in the owl lifecycle`).

### Solución / Patrón Estricto

En Odoo V19, la función `rpc` para hacer llamadas JSON-RPC expone ahora una exportación estática garantizada desde el core de networking, desacoplándola de la inyección por Hooks obligatoria (como sucedía con `action`).

**Incorrecto (Provoca UncaughtPromiseError) ❌**
```javascript
import { Component, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MiDashboard extends Component {
    setup() {
        // En Odoo V19 Client Actions esto explota el setup()
        this.rpc = useService("rpc"); 

        onMounted(() => { this.fetchDatos(); });
    }
    async fetchDatos() {
        const result = await this.rpc("/mi/endpoint", { ... });
    }
}
```

**Correcto (A prueba de Fallos Odoo V19) ✅**
```javascript
import { Component, onMounted } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc"; // Importación estática de core

export class MiDashboard extends Component {
    setup() {
        // No solicitar rpc como servicio aquí. 
        // Solo para dependencias que DEBAN ser hooks nativos de vista como "action"
        this.action = useService("action"); 

        onMounted(() => { this.fetchDatos(); });
    }
    async fetchDatos() {
        // Usar la función importada estáticamente desde core network
        const result = await rpc("/mi/endpoint", { ... });
    }
}
```

Al utilizar esta importación estática, sorteamos cualquier carrera contra el registrador de servicios del Root Environment de Odoo V19 y logramos llamadas asíncronas totalmente independientes en los sub-componentes.

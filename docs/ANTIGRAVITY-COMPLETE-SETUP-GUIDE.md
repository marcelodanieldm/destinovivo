# 🚀 Guía de Configuración Completa de Antigravity DESDE CERO (Sin Docker)
## System: Destino Vivo Hotel Revenue Management System (RMS)

Este documento es una guía paso a paso lista para uso en producción. Diseñada para que un ingeniero pueda desplegar, configurar y verificar Antigravity como orquestador del RMS **sin requerir Docker ni virtualización**.

---

## 1. SETUP INICIAL

### 1.1 Crear Cuenta y Organización
1. Ingresa a la consola de Antigravity: `https://console.antigravity.dev`.
2. Haz clic en **Create Account / Sign Up** e inicia sesión con tu cuenta corporativa.
3. En la pantalla inicial, crea la organización:
   - **Organization Name:** `Destino Vivo LatAm`
   - **Workspace Name:** `destinovivo-production`

### 1.2 Crear Proyecto para RMS
1. Dentro del Workspace, haz clic en **`+ New Project`**.
2. Completa los campos:
   - **Project Name:** `destino-vivo-rms-mvp`
   - **Environment:** `production`
   - **Region:** `us-central1`

### 1.3 Conectar VCS (GitHub Integration)
1. Ve a **Project Settings > Integrations > Version Control**.
2. Selecciona **GitHub Connection** y autoriza a Antigravity.
3. Vincula el repositorio: `marcelodanieldm/destinovivo`.
4. Define la rama de despliegue automático: `main`.

### 1.4 Configurar Variables de Entorno (`.env`)
En **Project Settings > Environment Variables**, define las siguientes llaves:

```bash
# Variables del Orquestador Antigravity
ANTIGRAVITY_ENV=production
ANTIGRAVITY_APP_ID=destino-vivo-rms-mvp

# Credenciales de Supabase
SUPABASE_URL=https://[YOUR_PROJECT_ID].supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Integraciones de Notificación
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxx
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxx
OPENWEATHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxx
```

---

## 2. PRIMER DAG SIMPLE (Hello World - `hello_rms`)

Crea el archivo [`antigravity/workflows/hello-rms.json`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/antigravity/workflows/hello-rms.json) para verificar la ejecución del orquestador:

### Especificación JSON:

```json
{
  "$schema": "https://antigravity.dev/schemas/workflow.json",
  "id": "hello_rms",
  "name": "Hello World RMS Initializer",
  "description": "DAG simple de verificación inicial para Destino Vivo RMS",
  "active": true,
  "nodes": [
    {
      "id": "task-init-print",
      "name": "Print RMS Initialized",
      "type": "JavaScriptCode",
      "config": {
        "code": "console.log('RMS initialized successfully for Destino Vivo LatAm!'); return { status: 'INITIALIZED', timestamp: new Date().toISOString() };"
      }
    }
  ]
}
```

### Pasos para Ejecutar y Verificar:
1. En la consola de Antigravity, ve a **Workflows > hello_rms**.
2. Haz clic en **`Trigger DAG / Run Now`**.
3. En la pestaña **Execution Log**, confirma la salida:
   ```text
   [INFO] [task-init-print] Starting task execution...
   [LOG]  RMS initialized successfully for Destino Vivo LatAm!
   [INFO] [task-init-print] Task finished with Status: SUCCESS
   ```

---

## 3. CONFIGURACIÓN DE CLUSTERS (Sizing & Scaling)

### 3.1 Sizing Recomendado para 10 Hoteles (Fase 0/1 MVP)

| Recurso | Mínimo Garantizado | Límite Máximo (Burst) | Justificación |
| :--- | :--- | :--- | :--- |
| **CPU** | 0.5 vCPU | 2.0 vCPU | Procesamiento liviano de expresiones JS y payloads JSON. |
| **RAM** | 512 MB | 2.0 GB | Manejo en memoria de 30 días de historial de precios. |
| **Storage** | 5 GB SSD | 20 GB SSD | Almacenamiento de logs locales y caché temporal. |

### 3.2 Autoscaling Strategy
En **Cluster Settings > Auto-scaling**:
- **Min Workers:** `1` (Worker siempre activo para triggers cron de las 02:00 AM).
- **Max Workers:** `3` (Escalado automático si la cola supera los 20 trabajos pendientes).
- **Scale-Up Threshold:** CPU > 70% durante 2 minutos.

---

## 4. INTEGRACIÓN CON SUPABASE

### 4.1 Connection String Setup
En Antigravity **Data Sources > Add New > HTTP REST (Supabase)**:

- **Base URL:** `https://[YOUR_PROJECT_ID].supabase.co/rest/v1`
- **Global Headers:**
  ```http
  apikey: {{ $env.SUPABASE_ANON_KEY }}
  Authorization: Bearer {{ $env.SUPABASE_SERVICE_ROLE_KEY }}
  Content-Type: application/json
  ```

---

## 5. SECRETOS Y CREDENCIALES

1. **Almacenamiento Seguro:** Guardar API Keys sensibles en **Antigravity Vault** (`$secrets.MY_KEY`), nunca en código fuente visible en GitHub.
2. **Acceso desde Tasks:** `$secrets.SENDGRID_API_KEY`, `$secrets.SUPABASE_SERVICE_ROLE_KEY`.

---

## 6. LOGGING Y MONITORING BÁSICO

1. **Stackdriver / CloudWatch Logging:** Habilitar log stream a nivel `INFO`.
2. **Alertas de Sistema:**
   - `Task Failure Count > 0` → Notificar a Slack `#destino-vivo-alerts`.
   - `Execution Time > 60s` → Alerta por correo electrónico.

---

## 7. ENTORNO DE DESARROLLO LOCAL NATIVO (Sin Docker)

Para desarrollar y probar localmente en tu sistema operativo (Windows/macOS/Linux) **sin necesidad de instalar Docker**:

### 7.1 Requisito Previos
- **Node.js** (Versión 18+ instalada localmente).

### 7.2 Comandos de Ejecución Local
```bash
# 1. Iniciar el Servidor de Vista Previa HTML en el puerto 3000
node scratch/preview-server.js

# 2. En otra terminal, ejecutar la suite de pruebas del motor de precios
node scratch/test-engine.js

# 3. Ejecutar la suite de pruebas End-to-End
node scratch/e2e-test-runner.js
```

El servidor web nativo de Antigravity quedará disponible inmediatamente en **`http://localhost:3000`**.

---

## 8. TROUBLESHOOTING COMÚN

### ❌ Problema 1: "DAG / Workflow no aparece en la UI"
- **Causa:** Sintaxis JSON inválida en el archivo del workflow.
- **Solución:** Valida el archivo JSON ejecutando `node -e "JSON.parse(fs.readFileSync('antigravity/workflows/hello-rms.json'))"`.

### ❌ Problema 2: "Task Execution Timeout (> 30s)"
- **Causa:** Petición HTTP bloqueada esperando respuesta de un endpoint externo inalcanzable.
- **Solución:** Agrega `"timeout": 5000` y `"ignoreError": true` a los nodos de integración de APIs externas.

### ❌ Problema 3: "Error HTTP 403 Forbidden al consultar Supabase"
- **Causa:** Las políticas RLS en PostgreSQL están activas y la petición usa la `ANON_KEY` en lugar de `SERVICE_ROLE_KEY`.
- **Solución:** Revisa que los workflows nocturnos usen `SERVICE_ROLE_KEY` en el header `Authorization`.

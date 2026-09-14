# 🚀 Guía de Configuración Completa de Antigravity DESDE CERO
## System: Destino Vivo Hotel Revenue Management System (RMS)

Este documento es una guía paso a paso lista para uso en producción. Diseñada para que un ingeniero pueda desplegar, configurar y verificar Antigravity como orquestador del RMS en menos de 4 horas.

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
   - **Region:** `us-central1` (o la región más cercana a tus hoteles en LatAm).

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
3. Revisa la pestaña **Execution Log**:
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

### 3.3 Cost Optimization
- **Idle Timeout:** Apagar workers secundarios después de 5 minutos de inactividad.
- **Costo estimado mensual:** **$0.00 USD** (Dentro de la capa gratuita de Antigravity).

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

### 4.2 Verificación de Conectividad desde el DAG
Ejecuta el siguiente snippet cURL o test HTTP en Antigravity:

```bash
curl -i -X GET "https://[YOUR_PROJECT_ID].supabase.co/rest/v1/hotels?select=count" \
  -H "apikey: [YOUR_SUPABASE_ANON_KEY]" \
  -H "Authorization: Bearer [YOUR_SUPABASE_SERVICE_ROLE_KEY]"
```
*Respuesta esperada:* HTTP `200 OK` con la cantidad de registros.

---

## 5. SECRETOS Y CREDENCIALES

### 5.1 Almacenamiento Seguro
- **NUNCA** guardes API keys en archivos JSON de workflows o código fuente en GitHub.
- Utiliza la bóveda de secretos integrada en **Antigravity Vault** (`$secrets.MY_KEY`).

### 5.2 Acceso desde las Tareas (Tasks)
```javascript
// Acceso seguro a credenciales en nodos JS
const sendgridKey = $secrets.SENDGRID_API_KEY;
const supabaseKey = $secrets.SUPABASE_SERVICE_ROLE_KEY;
```

### 5.3 Política de Rotación (Rotation Policy)
- Rotar la `SUPABASE_SERVICE_ROLE_KEY` cada 90 días.
- Mantener un registro de auditoría en **Vault > Audit Logs**.

---

## 6. LOGGING Y MONITORING BÁSICO

### 6.1 Configurar CloudWatch / Stackdriver Logging
En **Project Settings > Observability**:
- Habilitar **Stream Logs to CloudWatch / Google Cloud Logging**.
- Log Level: `INFO` (Cambiar a `DEBUG` solo durante diagnósticos).

### 6.2 Alertas de Sistema
Configurar en **Alert Rules**:
- **Alerta 1:** `Task Failure Count > 0` → Notificar vía Slack `#destino-vivo-alerts`.
- **Alerta 2:** `Workflow Execution Time > 60s` → Enviar correo de advertencia.

---

## 7. AMBIENTE DE DESARROLLO LOCAL (`docker-compose.yml`)

Para ejecutar todo el stack de forma local sin conexión a Internet, utiliza el archivo [`docker-compose.yml`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docker-compose.yml):

```bash
# Iniciar stack completo en segundo plano
docker-compose up -d

# Verificar contenedores corriendo
docker-compose ps

# Ver logs del motor Antigravity
docker-compose logs -f antigravity-engine
```

El servidor local quedará disponible en **`http://localhost:3000`** y el backend PostgreSQL simulado en el puerto `5432`.

---

## 8. TROUBLESHOOTING COMÚN

### ❌ Problema 1: "DAG / Workflow no aparece en la UI"
- **Causa:** Sintaxis JSON inválida en el archivo del workflow.
- **Solución:** Valida el archivo JSON con `jq . antigravity/workflows/my-workflow.json` antes de hacer commit.

### ❌ Problema 2: "Task Execution Timeout (> 30s)"
- **Causa:** Petición HTTP bloqueada esperando respuesta de un endpoint externo inalcanzable.
- **Solución:** Agrega `"timeout": 5000` y `"ignoreError": true` a los nodos de integración de APIs de terceros (ej. OpenWeather).

### ❌ Problema 3: "Error HTTP 403 Forbidden al consultar Supabase"
- **Causa:** Las políticas RLS en PostgreSQL están activas y la petición usa la `ANON_KEY` en lugar de `SERVICE_ROLE_KEY`.
- **Solución:** Revisa que los workflows nocturnos usen `SERVICE_ROLE_KEY` en el header `Authorization`.

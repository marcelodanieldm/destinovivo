# 📐 STACK-ANTIGRAVITY.md - Arquitectura Técnica Completa

Visión integral del stack tecnológico de **Destino Vivo**, sus capas de integración y modelo de costos.

---

## 🏛️ Visión de la Arquitectura

```
[ Antigravity UI / Workflows ]
        │
        ├── (Google OAuth 2.0) ──> [ Google Identity Services ]
        │
        ├── (REST / Sheet Connector) ──> [ Google Sheets (Database) ]
        │                                  ├── Users
        │                                  ├── Hotels
        │                                  ├── Pricing_Rules
        │                                  ├── Price_History
        │                                  └── Alerts_Config
        │
        └── (HTTP Webhooks) ──────────> [ Google Cloud Functions ]
                                           ├── calculatePricing (Python / Node.js)
                                           └── detectAlerts
```

---

## 🔧 Componentes del Stack

### 1. Frontend & Orchestration (Antigravity)
- **Rol:** Construcción de interfaces no-code, formularios de onboarding, dashboards de tarifas y gestión de workflows programados.
- **Ventajas:** Agilidad en iteración visual, integración nativa con conectores Google Workspace.

### 2. Base de Datos (Google Sheets)
- **Rol:** Base de datos relacional simplificada para la Fase 0 y Fase 1 MVP.
- **Acceso:** Google Sheets API v4 mediante conectores de Antigravity o Google Apps Script.

### 3. Capa de Cálculo (Google Cloud Functions)
- **Rol:** Ejecución de lógica de Revenue Management compleja, llamadas a modelos ML (TensorFlow.js / Scikit-Learn) y conexión con APIs externas (clima, eventos locales).

---

## 💰 Estimación de Costos (Fase 0 - MVP)

| Componente | Capa Gratuita / Plan | Costo Estimado Mensual |
| :--- | :--- | :--- |
| **Antigravity Plan** | Plan Gratuito / Developer | \$0.00 USD |
| **Google Sheets API** | Incluido en Google Workspace | \$0.00 USD |
| **Google Cloud Functions** | 2 Millones de invocaciones/mes gratis | \$0.00 USD |
| **Total Estimado** | | **\$0.00 USD / mes** |

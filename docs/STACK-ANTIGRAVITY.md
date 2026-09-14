# 📐 STACK-ANTIGRAVITY.md - Arquitectura Técnica Autónomamente Integrada

Visión integral del stack tecnológico de **Destino Vivo**, operando sin dependencias de Google Sheets ni Google Cloud (GCP).

---

## 🏛️ Visión de la Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    ANTIGRAVITY PLATFORM                     │
│                                                             │
│  ┌──────────────────────┐     ┌──────────────────────────┐  │
│  │   UI & Dashboards    │ ──> │   Workflows Programados  │  │
│  │   (Login, Onboarding,│     │   (Daily Pricing Update, │  │
│  │    Tarifas, Alertas) │     │    Alert Detection, etc) │  │
│  └──────────────────────┘     └────────────┬─────────────┘  │
│             │                              │                │
│             ▼                              ▼                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               Data Store Nativo                       │  │
│  │   (Users, Hotels, Pricing_Rules, Price_History)       │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │ (SMTP / Gmail Integration)
                               ▼
                    ┌─────────────────────┐
                    │  Gmail Service      │
                    │  (Alertas y Email)  │
                    └─────────────────────┘
```

---

## 🔧 Componentes del Stack

### 1. Frontend, Workflows & Data Store (Antigravity)
- **UI & Dashboard:** Construcción de interfaces no-code, formularios de onboarding, visualizadores de tarifas y resúmenes de alertas.
- **Data Store Nativo:** Persistencia interna de tablas en Antigravity para almacenamiento rápido, seguro y sin límites de cuotas de APIs externas.
- **Engine de Cómputo:** Expresiones en JavaScript y nodos de transformación ejecutados dentro de los workflows de Antigravity.

### 2. Notificaciones y Correo (Gmail Integration)
- **Notificaciones por Email:** Envío de alertas de ocupación crítica, resúmenes diarios de tarifas recomendadas y confirmaciones de onboarding a través de la integración nativa de Gmail.

---

## 💰 Estimación de Costos (Fase 0 & MVP)

| Componente | Plan / Capa | Costo Estimado Mensual |
| :--- | :--- | :--- |
| **Antigravity Engine & Storage** | Plan Developer / Standard | \$0.00 USD |
| **Google Cloud / GCP** | **NO UTILIZADO** | \$0.00 USD |
| **Google Sheets API** | **NO UTILIZADO** | \$0.00 USD |
| **Gmail API / SMTP** | Incluido en cuenta de correo Gmail | \$0.00 USD |
| **Total Estimado** | | **\$0.00 USD / mes** |

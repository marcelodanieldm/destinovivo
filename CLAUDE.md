# 🤖 CLAUDE.md - Sistema de Trabajo & Contexto Destino Vivo (Autónomo)

Este archivo contiene el contexto del proyecto **Destino Vivo**, la arquitectura elegida y las reglas operativas para trabajar de forma autónoma.

---

## 🎯 Contexto del Proyecto

- **Nombre:** Destino Vivo MVP
- **Propósito:** Revenue Management System (RMS) para hoteles boutique e independientes en LATAM / Brasil.
- **Stack:** Antigravity (No-code Frontend, Native Data Store & Workflows) + Gmail Integration (Notificaciones). Sin dependencias de Google Sheets ni Google Cloud (GCP).
- **Repositorio Git:** `https://github.com/marcelodanieldm/destinovivo.git`

---

## 🏗️ Decisiones de Arquitectura Principal

1. **Persistencia (Data Layer):** Data Store Nativo de Antigravity (tablas internas). Las tablas principales son: `Users`, `Hotels`, `Pricing_Rules`, `Price_History`, `Alerts_Config`. (Ver [`ADR-002`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/decisions/DECISION-002-Autonomous-Stack.md)).
2. **Motor de Trabajo (Workflows & Cómputo):** Antigravity orquesta las tareas periódicas y ejecuta la lógica de pricing internamente mediante JS Expressions:
   - `Daily Pricing Update`: Recálculo nocturno de tarifas en Antigravity.
   - `Alert Detection & Gmail Notification`: Monitoreo constante de ocupación y alertas enviadas por Gmail.
   - `Hotel Onboarding`: Alta de nuevos establecimientos y correo de bienvenida.
3. **Control de Versiones:** Guardar configuraciones de Antigravity exportadas en JSON dentro de `antigravity/workflows/` y `antigravity/pages/`.

---

## 📋 Reglas Operativas para el Agente AI

- **Formato Git:** Commits descriptivos siguiendo convención (`feat:`, `docs:`, `fix:`, `refactor:`).
- **Consistencia de Datos:** Todos los datos deben respetar las tablas y campos definidos en [`docs/NATIVE-DATA-SCHEMA.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/NATIVE-DATA-SCHEMA.md).
- **Sin GCP / Sheets:** No agregar scripts de Google Cloud Functions ni requerir la API de Google Sheets.

---

## 📚 Documentos de Referencia Directa

- [`docs/FASE-0-ANTIGRAVITY.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/FASE-0-ANTIGRAVITY.md)
- [`docs/NATIVE-DATA-SCHEMA.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/NATIVE-DATA-SCHEMA.md)
- [`docs/ANTIGRAVITY-WORKFLOWS.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/ANTIGRAVITY-WORKFLOWS.md)
- [`docs/STACK-ANTIGRAVITY.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/STACK-ANTIGRAVITY.md)
- [`docs/GITHUB-COLLABORATION.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/GITHUB-COLLABORATION.md)
- [`docs/decisions/DECISION-002-Autonomous-Stack.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/decisions/DECISION-002-Autonomous-Stack.md)

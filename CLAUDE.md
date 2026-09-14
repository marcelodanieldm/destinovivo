# 🤖 CLAUDE.md - Sistema de Trabajo & Contexto Destino Vivo

Este archivo contiene el contexto del proyecto **Destino Vivo**, la arquitectura elegida y las reglas operativas para trabajar de forma ágil y coordinada.

---

## 🎯 Contexto del Proyecto

- **Nombre:** Destino Vivo MVP
- **Propósito:** Revenue Management System (RMS) para hoteles boutique e independientes en LATAM / Brasil.
- **Stack:** Antigravity (No-code Frontend & Orchestration) + Google Sheets (Database) + Google Cloud Functions (Calculations/ML) + Google OAuth.
- **Repositorio Git:** `https://github.com/marcelodanieldm/destinovivo.git`

---

## 🏗️ Decisiones de Arquitectura Principal

1. **Persistencia (Data Layer):** Google Sheets como base de datos inicial para Fase 0/1. Las tablas principales son: `Users`, `Hotels`, `Pricing_Rules`, `Price_History`, `Alerts_Config`.
2. **Motor de Trabajo (Workflows):** Antigravity orquesta las tareas periódicas y la lógica UI:
   - `Daily Pricing Update`: Ejecución diaria de recálculo de tarifas.
   - `Alert Detection`: Monitoreo constante de variaciones de demanda y competencia.
   - `Hotel Onboarding`: Alta de nuevos establecimientos y configuración inicial.
3. **Control de Versiones:** Guardar configuraciones de Antigravity exportadas en JSON dentro de `antigravity/workflows/` y `antigravity/pages/`.

---

## 📋 Reglas Operativas para el Agente AI

- **Formato Git:** Commits descriptivos siguiendo convención (`feat:`, `docs:`, `fix:`, `refactor:`).
- **Consistencia de Datos:** Todos los cambios en la base de datos deben respetar los tipos de datos y nombres definidos en [`docs/GOOGLE-SHEETS-SCHEMA.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/GOOGLE-SHEETS-SCHEMA.md).
- **Ramas:** Crear ramas por característica (`feature/pricing-workflow`, `docs/update-schema`) antes de enviar cambios a `main`.

---

## 📚 Documentos de Referencia Directa

- [`docs/FASE-0-ANTIGRAVITY.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/FASE-0-ANTIGRAVITY.md)
- [`docs/GOOGLE-SHEETS-SCHEMA.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/GOOGLE-SHEETS-SCHEMA.md)
- [`docs/ANTIGRAVITY-WORKFLOWS.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/ANTIGRAVITY-WORKFLOWS.md)
- [`docs/STACK-ANTIGRAVITY.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/STACK-ANTIGRAVITY.md)
- [`docs/GITHUB-COLLABORATION.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/GITHUB-COLLABORATION.md)

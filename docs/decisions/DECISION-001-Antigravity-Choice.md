# ADR-001: Selección de Antigravity y Google Sheets para Fase 0/1 MVP

- **Estado:** Aprobado
- **Fecha:** 2026-09-14
- **Autores:** Equipo Destino Vivo

---

## Contexto
Se requiere construir un MVP de un Revenue Management System (RMS) para hoteles independientes en Latinoamérica con un tiempo de salida al mercado (Time-to-Market) de 2 a 4 semanas.

## Decisión
Aadoptar **Antigravity** como plataforma no-code de frontend y orquestación de workflows junto con **Google Sheets** como capa de persistencia inicial y **Google Cloud Functions** para cómputo complejo.

## Consecuencias
- **Positivas:** Costos de infraestructura cercanos a \$0.00 USD en Fase 0, rápida velocidad de iteración UI y facilidad para auditar datos directamente en hojas de cálculo.
- **Riesgos:** Escalabilidad limitada si un hotel supera las 500k filas en historial (mitigable migrando a BigQuery/Firestore en Fase 2).

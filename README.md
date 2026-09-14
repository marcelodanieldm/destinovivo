# 🏨 Destino Vivo MVP

> **Revenue Management System (RMS) para hoteles boutique e independientes en Latinoamérica y Brasil.**

---

## 📌 Visión General

**Destino Vivo** es un sistema inteligente de gestión de ingresos (Revenue Management System - RMS) diseñado para optimizar el inventario de habitaciones, tarifas dinámicas y ocupación hotelera en el mercado latinoamericano.

- **Stack:** Antigravity (No-Code App / Workflows) + Google Sheets (Data Layer) + Google Cloud Functions (Calculations & Integrations)
- **Fase Actual:** Fase 0 (Setup & Proof of Concept - 2 Semanas) → Fase 1 (MVP)
- **Repositorio:** [https://github.com/marcelodanieldm/destinovivo.git](https://github.com/marcelodanieldm/destinovivo.git)

---

## 📂 Estructura del Repositorio

```
destino-vivo/
├── README.md                          # Documento principal del proyecto
├── CLAUDE.md                          # Guía del sistema de trabajo y contexto
├── .env.example                       # Plantilla de variables de entorno
├── .gitignore                         # Archivos ignorados por git
├── docs/                              # Documentación detallada del proyecto
│   ├── FASE-0-ANTIGRAVITY.md          # Checklist y plan de ejecución (2 semanas)
│   ├── GOOGLE-SHEETS-SCHEMA.md        # Esquema detallado del modelo de datos
│   ├── ANTIGRAVITY-WORKFLOWS.md       # Especificación de workflows de Antigravity
│   ├── STACK-ANTIGRAVITY.md           # Arquitectura técnica del sistema
│   ├── GITHUB-COLLABORATION.md        # Estándares de Git, ramas y PRs
│   ├── AGENTES-SKILLS-CONTEXTO.md     # Catálogo de agentes y skills
│   ├── PROMPTS-LISTOS.md              # Biblioteca de prompts operativos
│   └── decisions/                     # Registro de decisiones de arquitectura (ADRs)
│       └── DECISION-001-Antigravity-Choice.md
├── antigravity/                       # Exportaciones y componentes de Antigravity
│   ├── README.md                      # Instrucciones de exportación e importación
│   ├── workflows/                     # Workflows JSON exportados
│   ├── pages/                         # UI Pages exportadas
│   ├── components/                    # Componentes reutilizables
│   └── exports/                       # Backups completos del proyecto
└── google-workspace/                  # Recursos de Google Workspace
    ├── sheets/                        # Esquemas CSV y plantillas de Sheets
    │   └── SCHEMA.md
    └── apps-script/                   # Scripts de integración Google Apps Script
```

---

## ⚡ Inicio Rápido (Fase 0)

1. **Clonar repositorio:**
   ```bash
   git clone https://github.com/marcelodanieldm/destinovivo.git
   cd destinovivo
   ```

2. **Revisar Documentación:**
   - Lee [`CLAUDE.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/CLAUDE.md) para entender el modelo de trabajo y reglas.
   - Revisa [`docs/FASE-0-ANTIGRAVITY.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/FASE-0-ANTIGRAVITY.md) para el plan de ejecución de 2 semanas.

3. **Modelo de Datos:**
   - Consulta [`docs/GOOGLE-SHEETS-SCHEMA.md`](file:///c:/Users/danie/Documents/antigravity/resilient-volta/docs/GOOGLE-SHEETS-SCHEMA.md) para configurar la hoja madre en Google Sheets.

---

## 📄 Licencia y Autores

Desarrollado para el ecosistema **Destino Vivo Latam/Brasil**.

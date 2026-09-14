# 🐙 GITHUB-COLLABORATION.md - Workflow de Git y Colaboración

Guía y estándares de trabajo en GitHub para el desarrollo del proyecto **Destino Vivo**.

---

## 🌿 Estrategia de Ramas (Branching)

- **`main`**: Rama de producción estable. Todo cambio debe ingresar mediante Pull Request (PR) aprobado.
- **`feature/*`**: Para el desarrollo de nuevas características o workflows (ej. `feature/daily-pricing-workflow`).
- **`fix/*`**: Correcciones de bugs en esquemas o integraciones (ej. `fix/sheets-date-format`).
- **`docs/*`**: Actualización de documentación (ej. `docs/update-workflows`).

---

## 📝 Convención de Mensajes de Commit

Seguimos la convención **Conventional Commits**:

- `feat:` Nuevas funcionalidades o exportaciones de Antigravity.
- `fix:` Correcciones de errores.
- `docs:` Cambios en archivos markdown o esquemas.
- `refactor:` Mejoras de estructura de código o esquemas sin cambiar su comportamiento.
- `chore:` Tareas de mantenimiento o configuración.

### Ejemplo
```bash
git commit -m "feat(antigravity): add Daily Pricing Update workflow definition

- Configured cron trigger at 02:00 AM
- Connected Cloud Function pricing endpoint
- Added Price_History output mapping"
```

---

## 🔀 Workflow de Pull Request (PR)

1. Crear una rama local a partir de `main`.
2. Realizar los cambios y validar contra los documentos de especificación.
3. Hacer push de la rama al remoto `origin`.
4. Abrir un Pull Request detallando los cambios y vinculando la tarea correspondiente.
5. Aprobar y fusionar (Squash & Merge) a `main`.

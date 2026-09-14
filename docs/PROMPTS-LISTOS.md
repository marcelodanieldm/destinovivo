# 💬 PROMPTS-LISTOS.md - Biblioteca de Prompts Operativos

Colección de prompts pre-construidos para agilizar el desarrollo de Destino Vivo.

---

## 1. Prompt: Crear Formulario de Onboarding de Hotel

```text
Destino Vivo: Genera la especificación paso a paso para construir la pantalla de "Hotel Onboarding" en Antigravity.
Incluye los campos del formulario acorde a docs/GOOGLE-SHEETS-SCHEMA.md (Hotels sheet) y las reglas de validación en tiempo real.
```

---

## 2. Prompt: Implementar Workflow "Daily Pricing Update"

```text
Destino Vivo: Ayúdame a diseñar el workflow "Daily Pricing Update" en Antigravity.
Debe ejecutarse a las 02:00 AM, leer los hoteles activos de Google Sheets, llamar a la Cloud Function calculatePricing y guardar los resultados en la pestaña Price_History.
```

---

## 3. Prompt: Validar Esquema de Google Sheets

```text
Destino Vivo: Revisa si los campos de la pestaña Pricing_Rules en docs/GOOGLE-SHEETS-SCHEMA.md son suficientes para soportar descuentos por temporada alta y sobrecargos de fin de semana. Propón cambios si es necesario.
```

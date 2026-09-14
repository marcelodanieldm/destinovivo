# 🐘 SUPABASE-POSTGRESQL-SCHEMA.md - Esquema de Base de Datos (8 Tablas)

Especificación completa del esquema PostgreSQL para **Destino Vivo** en Supabase.

---

## 📜 Script SQL de Creación (DDL)

```sql
-- 1. Tabla: users
CREATE TABLE IF NOT EXISTS public.users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'HOTEL_MANAGER',
  hotel_ids TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now(),
  status TEXT DEFAULT 'ACTIVE'
);

-- 2. Tabla: hotels
CREATE TABLE IF NOT EXISTS public.hotels (
  hotel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  country TEXT NOT NULL DEFAULT 'Argentina',
  city TEXT NOT NULL DEFAULT 'Buenos Aires',
  currency TEXT NOT NULL DEFAULT 'USD',
  total_rooms INT NOT NULL DEFAULT 30,
  base_rate NUMERIC(10, 2) NOT NULL DEFAULT 100.00,
  min_rate NUMERIC(10, 2) NOT NULL DEFAULT 70.00,
  max_rate NUMERIC(10, 2) NOT NULL DEFAULT 300.00,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Tabla: pricing_rules
CREATE TABLE IF NOT EXISTS public.pricing_rules (
  rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id UUID REFERENCES public.hotels(hotel_id) ON DELETE CASCADE,
  rule_type TEXT NOT NULL,
  threshold_min NUMERIC(5, 2) DEFAULT 80.00,
  threshold_max NUMERIC(5, 2) DEFAULT 100.00,
  adjustment_type TEXT NOT NULL DEFAULT 'PERCENTAGE',
  adjustment_value NUMERIC(10, 2) NOT NULL DEFAULT 15.00,
  is_active BOOLEAN DEFAULT true
);

-- 4. Tabla: price_history
CREATE TABLE IF NOT EXISTS public.price_history (
  history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id UUID REFERENCES public.hotels(hotel_id) ON DELETE CASCADE,
  target_date DATE NOT NULL,
  recommended_rate NUMERIC(10, 2) NOT NULL,
  applied_rate NUMERIC(10, 2) NOT NULL,
  occupancy_pct NUMERIC(5, 2) NOT NULL,
  rules_applied TEXT[] DEFAULT '{}',
  calculated_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Tabla: alerts_config
CREATE TABLE IF NOT EXISTS public.alerts_config (
  alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id UUID REFERENCES public.hotels(hotel_id) ON DELETE CASCADE,
  alert_type TEXT NOT NULL,
  severity TEXT NOT NULL DEFAULT 'WARNING',
  message TEXT NOT NULL,
  sent_via_gmail BOOLEAN DEFAULT false,
  is_resolved BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Tabla: alerts_log
CREATE TABLE IF NOT EXISTS public.alerts_log (
  log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID REFERENCES public.alerts_config(alert_id) ON DELETE CASCADE,
  recipient_email TEXT NOT NULL,
  delivery_status TEXT NOT NULL DEFAULT 'SENT',
  dispatched_at TIMESTAMPTZ DEFAULT now()
);

-- 7. Tabla: bookings_sync
CREATE TABLE IF NOT EXISTS public.bookings_sync (
  sync_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id UUID REFERENCES public.hotels(hotel_id) ON DELETE CASCADE,
  source_channel TEXT NOT NULL DEFAULT 'DIRECT',
  rooms_booked INT NOT NULL DEFAULT 1,
  total_amount NUMERIC(10, 2) NOT NULL,
  synced_at TIMESTAMPTZ DEFAULT now()
);

-- 8. Tabla: api_keys
CREATE TABLE IF NOT EXISTS public.api_keys (
  key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(user_id) ON DELETE CASCADE,
  api_key_hash TEXT NOT NULL,
  label TEXT DEFAULT 'Default API Key',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

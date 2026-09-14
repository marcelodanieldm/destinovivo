-- ====================================================================
-- DESTINO VIVO RMS - COMPLETE SUPABASE POSTGRESQL MIGRATION SCRIPT
-- Version: 2.0 (Production Ready)
-- Target DB: PostgreSQL 15+ (Supabase)
-- ====================================================================

BEGIN;

-- --------------------------------------------------------------------
-- 0. ENUMS CREATION
-- --------------------------------------------------------------------
CREATE TYPE booking_status AS ENUM ('confirmed', 'cancelled', 'pending');
CREATE TYPE booking_source AS ENUM ('direct', 'booking.com', 'expedia', 'airbnb', 'despegar', 'other');
CREATE TYPE forecast_model AS ENUM ('arima', 'prophet', 'lstm', 'ensemble');
CREATE TYPE variable_type AS ENUM ('internal', 'external', 'derived');

-- --------------------------------------------------------------------
-- 1. TABLES CREATION
-- --------------------------------------------------------------------

-- a) hotels
CREATE TABLE IF NOT EXISTS public.hotels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  country TEXT NOT NULL DEFAULT 'MX',
  rooms_count INT NOT NULL DEFAULT 30,
  types JSONB DEFAULT '{"single": 10, "double": 15, "suite": 5}'::jsonb,
  pms_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- b) bookings
CREATE TABLE IF NOT EXISTS public.bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id UUID NOT NULL REFERENCES public.hotels(id) ON DELETE CASCADE,
  check_in DATE NOT NULL,
  check_out DATE NOT NULL,
  room_type TEXT NOT NULL DEFAULT 'double',
  price NUMERIC(10, 2) NOT NULL,
  status booking_status NOT NULL DEFAULT 'confirmed',
  source booking_source NOT NULL DEFAULT 'direct',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT check_dates CHECK (check_out > check_in)
);

-- c) daily_prices
CREATE TABLE IF NOT EXISTS public.daily_prices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id UUID NOT NULL REFERENCES public.hotels(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  room_type TEXT NOT NULL DEFAULT 'double',
  price_rule_based NUMERIC(10, 2) NOT NULL,
  price_ml NUMERIC(10, 2),
  price_hybrid NUMERIC(10, 2) NOT NULL,
  accepted BOOLEAN DEFAULT false,
  overridden_to NUMERIC(10, 2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT unique_hotel_date_room UNIQUE (hotel_id, date, room_type)
);

-- d) forecasts
CREATE TABLE IF NOT EXISTS public.forecasts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id UUID NOT NULL REFERENCES public.hotels(id) ON DELETE CASCADE,
  forecast_date DATE NOT NULL,
  model forecast_model NOT NULL DEFAULT 'ensemble',
  demand_1d INT NOT NULL DEFAULT 0,
  demand_7d INT NOT NULL DEFAULT 0,
  demand_30d INT NOT NULL DEFAULT 0,
  confidence_1d NUMERIC(3, 2) CHECK (confidence_1d BETWEEN 0 AND 1),
  accuracy_mape NUMERIC(5, 2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- e) variables_daily
CREATE TABLE IF NOT EXISTS public.variables_daily (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id UUID NOT NULL REFERENCES public.hotels(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  variable_name TEXT NOT NULL,
  variable_value TEXT NOT NULL,
  variable_type variable_type NOT NULL DEFAULT 'external',
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT unique_hotel_date_var UNIQUE (hotel_id, date, variable_name)
);

-- f) competitive_data
CREATE TABLE IF NOT EXISTS public.competitive_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hotel_id UUID NOT NULL REFERENCES public.hotels(id) ON DELETE CASCADE,
  competitor_id TEXT NOT NULL,
  competitor_name TEXT NOT NULL,
  competitor_price NUMERIC(10, 2) NOT NULL,
  our_price NUMERIC(10, 2) NOT NULL,
  competitive_index NUMERIC(5, 2),
  scraped_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- g) api_logs
CREATE TABLE IF NOT EXISTS public.api_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  method TEXT NOT NULL DEFAULT 'GET',
  status_code INT NOT NULL,
  response_time_ms INT NOT NULL,
  success BOOLEAN NOT NULL DEFAULT true,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- --------------------------------------------------------------------
-- 2. PERFORMANCE INDEXES
-- --------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_bookings_hotel_checkin ON public.bookings(hotel_id, check_in);
CREATE INDEX IF NOT EXISTS idx_daily_prices_hotel_date ON public.daily_prices(hotel_id, date);
CREATE INDEX IF NOT EXISTS idx_forecasts_hotel_date ON public.forecasts(hotel_id, forecast_date);
CREATE INDEX IF NOT EXISTS idx_variables_hotel_date ON public.variables_daily(hotel_id, date);
CREATE INDEX IF NOT EXISTS idx_competitive_hotel_scraped ON public.competitive_data(hotel_id, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_service_created ON public.api_logs(service, created_at DESC);

-- --------------------------------------------------------------------
-- 3. ROW LEVEL SECURITY (RLS) & POLICIES
-- --------------------------------------------------------------------
ALTER TABLE public.hotels ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.variables_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.competitive_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_logs ENABLE ROW LEVEL SECURITY;

-- Allow Service Role Service Bypass (Full Access for Backend Cron / Antigravity System)
CREATE POLICY "Service Role Full Access Hotels" ON public.hotels FOR ALL TO service_role USING (true);
CREATE POLICY "Service Role Full Access Bookings" ON public.bookings FOR ALL TO service_role USING (true);
CREATE POLICY "Service Role Full Access DailyPrices" ON public.daily_prices FOR ALL TO service_role USING (true);
CREATE POLICY "Service Role Full Access Forecasts" ON public.forecasts FOR ALL TO service_role USING (true);
CREATE POLICY "Service Role Full Access Variables" ON public.variables_daily FOR ALL TO service_role USING (true);
CREATE POLICY "Service Role Full Access Competitive" ON public.competitive_data FOR ALL TO service_role USING (true);
CREATE POLICY "Service Role Full Access ApiLogs" ON public.api_logs FOR ALL TO service_role USING (true);

-- Allow Public Read for Authenticated Users (Read Access for UI)
CREATE POLICY "Authenticated Read Hotels" ON public.hotels FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated Read Bookings" ON public.bookings FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated Read DailyPrices" ON public.daily_prices FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated Read Forecasts" ON public.forecasts FOR SELECT TO authenticated USING (true);

-- --------------------------------------------------------------------
-- 4. UTILITY SQL FUNCTIONS (Occupancy, RevPAR, ADR, Competitive Index)
-- --------------------------------------------------------------------

-- Function 1: calculate_occupancy(p_hotel_id, p_date)
CREATE OR REPLACE FUNCTION public.calculate_occupancy(p_hotel_id UUID, p_date DATE)
RETURNS NUMERIC AS $$
DECLARE
  v_total_rooms INT;
  v_booked_rooms INT;
BEGIN
  SELECT rooms_count INTO v_total_rooms FROM public.hotels WHERE id = p_hotel_id;
  IF v_total_rooms IS NULL OR v_total_rooms = 0 THEN RETURN 0; END IF;

  SELECT COUNT(*) INTO v_booked_rooms
  FROM public.bookings
  WHERE hotel_id = p_hotel_id
    AND p_date >= check_in
    AND p_date < check_out
    AND status = 'confirmed';

  RETURN ROUND((v_booked_rooms::NUMERIC / v_total_rooms::NUMERIC) * 100, 2);
END;
$$ LANGUAGE plpgsql STABLE;

-- Function 2: calculate_adr(p_hotel_id, p_date) -> Average Daily Rate
CREATE OR REPLACE FUNCTION public.calculate_adr(p_hotel_id UUID, p_date DATE)
RETURNS NUMERIC AS $$
DECLARE
  v_adr NUMERIC;
BEGIN
  SELECT AVG(price) INTO v_adr
  FROM public.bookings
  WHERE hotel_id = p_hotel_id
    AND p_date >= check_in
    AND p_date < check_out
    AND status = 'confirmed';

  RETURN COALESCE(ROUND(v_adr, 2), 0.00);
END;
$$ LANGUAGE plpgsql STABLE;

-- Function 3: calculate_revpar(p_hotel_id, p_date) -> Revenue Per Available Room
CREATE OR REPLACE FUNCTION public.calculate_revpar(p_hotel_id UUID, p_date DATE)
RETURNS NUMERIC AS $$
DECLARE
  v_occupancy NUMERIC;
  v_adr NUMERIC;
BEGIN
  v_occupancy := public.calculate_occupancy(p_hotel_id, p_date);
  v_adr := public.calculate_adr(p_hotel_id, p_date);
  RETURN ROUND((v_adr * (v_occupancy / 100)), 2);
END;
$$ LANGUAGE plpgsql STABLE;

-- Function 4: get_competitive_index(p_hotel_id)
CREATE OR REPLACE FUNCTION public.get_competitive_index(p_hotel_id UUID)
RETURNS NUMERIC AS $$
DECLARE
  v_index NUMERIC;
BEGIN
  SELECT AVG(our_price / NULLIF(competitor_price, 0)) INTO v_index
  FROM public.competitive_data
  WHERE hotel_id = p_hotel_id
    AND scraped_at >= (now() - INTERVAL '7 days');

  RETURN COALESCE(ROUND(v_index, 2), 1.00);
END;
$$ LANGUAGE plpgsql STABLE;

-- --------------------------------------------------------------------
-- 5. SEED MOCK DATA
-- --------------------------------------------------------------------
INSERT INTO public.hotels (id, name, country, rooms_count, types, pms_id)
VALUES (
  'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
  'Hotel Boutique Sol',
  'AR',
  45,
  '{"single": 15, "double": 20, "suite": 10}'::jsonb,
  'pms_sol_001'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO public.bookings (hotel_id, check_in, check_out, room_type, price, status, source)
VALUES
( 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', CURRENT_DATE - 1, CURRENT_DATE + 2, 'double', 120.00, 'confirmed', 'direct' ),
( 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', CURRENT_DATE, CURRENT_DATE + 3, 'suite', 250.00, 'confirmed', 'booking.com' )
ON CONFLICT DO NOTHING;

INSERT INTO public.daily_prices (hotel_id, date, room_type, price_rule_based, price_ml, price_hybrid, accepted)
VALUES (
  'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
  CURRENT_DATE,
  'double',
  120.00,
  140.00,
  138.00,
  true
) ON CONFLICT DO NOTHING;

COMMIT;

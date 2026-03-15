-- Add price and return columns to influencer_signals table
ALTER TABLE influencer_signals 
  ADD COLUMN IF NOT EXISTS price_at_signal NUMERIC,
  ADD COLUMN IF NOT EXISTS price_current NUMERIC,
  ADD COLUMN IF NOT EXISTS return_pct NUMERIC;

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_KEY || ''

export const supabase = createClient(supabaseUrl, supabaseKey)

export interface StravaActivity {
  id: number
  name: string
  type: string
  start_date: string
  distance: number
  moving_time: number
  elapsed_time: number
  total_elevation_gain: number
  average_speed: number
  max_speed: number
  average_heartrate: number | null
  max_heartrate: number | null
  location_city: string | null
  location_country: string | null
  created_at: string
}
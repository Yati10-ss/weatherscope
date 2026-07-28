import type { LocationResult } from './location';
import type {
  DailySourceType,
  DailyWeatherObservation,
  DailyWeatherUnits,
  UnitSystem,
} from './weather';

export interface SavedLocationInput {
  original_input: string;
  resolved_name: string;
  administrative_area: string | null;
  secondary_administrative_area: string | null;
  country: string | null;
  country_code: string | null;
  latitude: number;
  longitude: number;
  timezone: string;
}

export interface WeatherSearchCreateRequest {
  location: SavedLocationInput;
  start_date: string;
  end_date: string;
  unit_system: UnitSystem;
  note: string | null;
}

export interface WeatherSearchUpdateRequest {
  start_date?: string;
  end_date?: string;
  unit_system?: UnitSystem;
  note?: string | null;
}

export interface WeatherSearchSummary {
  id: number;
  location: SavedLocationInput;
  start_date: string;
  end_date: string;
  total_days: number;
  unit_system: UnitSystem;
  note: string | null;
  provider: string;
  created_at: string;
  updated_at: string;
  retrieved_at: string;
}

export interface WeatherSearchDetail extends WeatherSearchSummary {
  provider_latitude: number;
  provider_longitude: number;
  elevation_m: number | null;
  timezone_abbreviation: string | null;
  utc_offset_seconds: number;
  units: DailyWeatherUnits;
  source_types: DailySourceType[];
  days: DailyWeatherObservation[];
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface WeatherSearchListResponse {
  items: WeatherSearchSummary[];
  pagination: PaginationMeta;
}

export function toSavedLocation(
  location: LocationResult,
  originalInput?: string,
): SavedLocationInput {
  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  return {
    original_input: originalInput?.trim() || location.name || location.display_name,
    resolved_name: location.display_name || location.name,
    administrative_area: location.administrative_area,
    secondary_administrative_area: location.secondary_administrative_area,
    country: location.country,
    country_code: location.country_code,
    latitude: location.latitude,
    longitude: location.longitude,
    timezone: location.timezone || browserTimezone,
  };
}

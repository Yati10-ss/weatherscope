export type UnitSystem = 'metric' | 'imperial';
export type DailySourceType = 'forecast' | 'historical';

export interface CurrentWeatherUnits {
  temperature: string;
  apparent_temperature: string;
  relative_humidity: string;
  precipitation: string;
  wind_speed: string;
  wind_direction: string;
  wind_gusts: string;
}

export interface CurrentWeatherObservation {
  observed_at_local: string;
  interval_seconds: number;
  temperature: number;
  apparent_temperature: number;
  relative_humidity_percent: number;
  is_day: boolean;
  precipitation: number;
  weather_code: number;
  condition: string;
  wind_speed: number;
  wind_direction_degrees: number;
  wind_direction_cardinal: string;
  wind_gusts: number;
}

export interface CurrentWeatherResponse {
  provider: 'Open-Meteo';
  unit_system: UnitSystem;
  requested_latitude: number;
  requested_longitude: number;
  provider_latitude: number;
  provider_longitude: number;
  elevation_m: number | null;
  timezone: string;
  timezone_abbreviation: string | null;
  utc_offset_seconds: number;
  units: CurrentWeatherUnits;
  current: CurrentWeatherObservation;
}

export interface DailyWeatherUnits {
  temperature: string;
  apparent_temperature: string;
  precipitation: string;
  precipitation_probability: string;
  wind_speed: string;
  wind_gusts: string;
  daylight_duration: string;
  sunshine_duration: string;
}

export interface DailyWeatherObservation {
  date: string;
  source_type: DailySourceType;
  weather_code: number;
  condition: string;
  temperature_min: number;
  temperature_max: number;
  temperature_mean: number | null;
  apparent_temperature_min: number | null;
  apparent_temperature_max: number | null;
  precipitation_sum: number;
  precipitation_probability_max: number | null;
  wind_speed_max: number;
  wind_gusts_max: number | null;
  sunrise_local: string | null;
  sunset_local: string | null;
  daylight_duration_seconds: number | null;
  sunshine_duration_seconds: number | null;
}

export interface WeatherRangeResponse {
  provider: 'Open-Meteo';
  unit_system: UnitSystem;
  requested_latitude: number;
  requested_longitude: number;
  provider_latitude: number;
  provider_longitude: number;
  elevation_m: number | null;
  timezone: string;
  timezone_abbreviation: string | null;
  utc_offset_seconds: number;
  start_date: string;
  end_date: string;
  total_days: number;
  source_types: DailySourceType[];
  units: DailyWeatherUnits;
  days: DailyWeatherObservation[];
}

export interface WeatherPreviewRequest {
  latitude: number;
  longitude: number;
  start_date: string;
  end_date: string;
  unit_system: UnitSystem;
  timezone: string | null;
}

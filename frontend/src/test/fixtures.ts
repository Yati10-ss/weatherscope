import type { LocationResult } from '../types/location';
import type { CurrentWeatherResponse, WeatherRangeResponse } from '../types/weather';

export const philadelphia: LocationResult = {
  provider_id: 4560349,
  name: 'Philadelphia',
  display_name: 'Philadelphia, Pennsylvania, United States',
  latitude: 39.95233,
  longitude: -75.16379,
  country: 'United States',
  country_code: 'US',
  administrative_area: 'Pennsylvania',
  secondary_administrative_area: 'Philadelphia County',
  timezone: 'America/New_York',
  elevation_m: 12,
  population: 1603797,
  postcodes: ['19104'],
};

export const currentWeather: CurrentWeatherResponse = {
  provider: 'Open-Meteo',
  unit_system: 'metric',
  requested_latitude: 39.95233,
  requested_longitude: -75.16379,
  provider_latitude: 39.95,
  provider_longitude: -75.16,
  elevation_m: 12,
  timezone: 'America/New_York',
  timezone_abbreviation: 'EDT',
  utc_offset_seconds: -14400,
  units: {
    temperature: '°C', apparent_temperature: '°C', relative_humidity: '%',
    precipitation: 'mm', wind_speed: 'km/h', wind_direction: '°', wind_gusts: 'km/h',
  },
  current: {
    observed_at_local: '2026-07-27T18:00', interval_seconds: 900, temperature: 29.4,
    apparent_temperature: 31.2, relative_humidity_percent: 57, is_day: true,
    precipitation: 0, weather_code: 2, condition: 'Partly cloudy', wind_speed: 11.5,
    wind_direction_degrees: 247, wind_direction_cardinal: 'WSW', wind_gusts: 23,
  },
};

const forecastDates = [
  '2026-07-28',
  '2026-07-29',
  '2026-07-30',
  '2026-07-31',
  '2026-08-01',
];

const days = forecastDates.map((date, index) => ({
  date,
  source_type: 'forecast' as const,
  weather_code: index === 1 ? 61 : 2,
  condition: index === 1 ? 'Slight rain' : 'Partly cloudy',
  temperature_min: 20 + index,
  temperature_max: 29 + index,
  temperature_mean: 25 + index,
  apparent_temperature_min: 21 + index,
  apparent_temperature_max: 31 + index,
  precipitation_sum: index === 1 ? 4.2 : 0,
  precipitation_probability_max: index === 1 ? 70 : 15,
  wind_speed_max: 18,
  wind_gusts_max: 30,
  sunrise_local: '2026-07-28T05:55',
  sunset_local: '2026-07-28T20:17',
  daylight_duration_seconds: 51600,
  sunshine_duration_seconds: 36000,
}));

export const forecast: WeatherRangeResponse = {
  provider: 'Open-Meteo', unit_system: 'metric', requested_latitude: 39.95233,
  requested_longitude: -75.16379, provider_latitude: 39.95, provider_longitude: -75.16,
  elevation_m: 12, timezone: 'America/New_York', timezone_abbreviation: 'EDT',
  utc_offset_seconds: -14400, start_date: '2026-07-28', end_date: '2026-08-01',
  total_days: 5, source_types: ['forecast'],
  units: {
    temperature: '°C', apparent_temperature: '°C', precipitation: 'mm',
    precipitation_probability: '%', wind_speed: 'km/h', wind_gusts: 'km/h',
    daylight_duration: 's', sunshine_duration: 's',
  },
  days,
};

export const savedSearch = {
  id: 7,
  location: {
    original_input: 'Philadelphia',
    resolved_name: 'Philadelphia, Pennsylvania, United States',
    administrative_area: 'Pennsylvania',
    secondary_administrative_area: 'Philadelphia County',
    country: 'United States',
    country_code: 'US',
    latitude: 39.95233,
    longitude: -75.16379,
    timezone: 'America/New_York',
  },
  start_date: '2026-07-28',
  end_date: '2026-08-01',
  total_days: 5,
  unit_system: 'metric' as const,
  note: 'Conference planning',
  provider: 'Open-Meteo',
  created_at: '2026-07-27T12:00:00Z',
  updated_at: '2026-07-27T12:00:00Z',
  retrieved_at: '2026-07-27T12:00:00Z',
};

export const savedSearchDetail = {
  ...savedSearch,
  provider_latitude: 39.95,
  provider_longitude: -75.16,
  elevation_m: 12,
  timezone_abbreviation: 'EDT',
  utc_offset_seconds: -14400,
  units: forecast.units,
  source_types: ['forecast' as const],
  days: forecast.days,
};

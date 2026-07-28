import { buildQuery, requestJson } from './client';
import type {
  CurrentWeatherResponse,
  UnitSystem,
  WeatherPreviewRequest,
  WeatherRangeResponse,
} from '../types/weather';

export function getCurrentWeather(
  latitude: number,
  longitude: number,
  unitSystem: UnitSystem,
): Promise<CurrentWeatherResponse> {
  return requestJson<CurrentWeatherResponse>(
    `/weather/current${buildQuery({ latitude, longitude, unit_system: unitSystem })}`,
  );
}

export function getFiveDayForecast(
  latitude: number,
  longitude: number,
  unitSystem: UnitSystem,
): Promise<WeatherRangeResponse> {
  return requestJson<WeatherRangeResponse>(
    `/weather/forecast${buildQuery({
      latitude,
      longitude,
      days: 5,
      unit_system: unitSystem,
    })}`,
  );
}

export function previewWeather(
  request: WeatherPreviewRequest,
): Promise<WeatherRangeResponse> {
  return requestJson<WeatherRangeResponse>('/weather/preview', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

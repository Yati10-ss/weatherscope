import { API_BASE_URL, buildQuery, requestJson } from './client';
import type {
  WeatherSearchCreateRequest,
  WeatherSearchDetail,
  WeatherSearchListResponse,
  WeatherSearchUpdateRequest,
} from '../types/weatherSearch';

export function createWeatherSearch(
  request: WeatherSearchCreateRequest,
): Promise<WeatherSearchDetail> {
  return requestJson<WeatherSearchDetail>('/weather-searches', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export function listWeatherSearches(
  page = 1,
  pageSize = 10,
  location?: string,
): Promise<WeatherSearchListResponse> {
  return requestJson<WeatherSearchListResponse>(
    `/weather-searches${buildQuery({ page, page_size: pageSize, location })}`,
  );
}

export function getWeatherSearch(searchId: number): Promise<WeatherSearchDetail> {
  return requestJson<WeatherSearchDetail>(`/weather-searches/${searchId}`);
}

export function updateWeatherSearch(
  searchId: number,
  request: WeatherSearchUpdateRequest,
): Promise<WeatherSearchDetail> {
  return requestJson<WeatherSearchDetail>(`/weather-searches/${searchId}`, {
    method: 'PATCH',
    body: JSON.stringify(request),
  });
}

export async function deleteWeatherSearch(searchId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/weather-searches/${searchId}`, {
    method: 'DELETE',
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) {
    let message = `Delete failed with status ${response.status}.`;
    try {
      const body = (await response.json()) as { error?: { message?: string } };
      message = body.error?.message || message;
    } catch {
      // Keep the fallback message.
    }
    throw new Error(message);
  }
}

export async function downloadWeatherSearch(
  format: 'csv' | 'json',
  searchId?: number,
): Promise<void> {
  const path = searchId
    ? `/exports/weather-searches/${searchId}.${format}`
    : `/exports/weather-searches.${format}`;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: format === 'json' ? 'application/json' : 'text/csv' },
  });
  if (!response.ok) {
    throw new Error(`Export failed with status ${response.status}.`);
  }

  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition');
  const match = disposition?.match(/filename="?([^";]+)"?/i);
  const filename = match?.[1] || `weatherscope-export.${format}`;
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

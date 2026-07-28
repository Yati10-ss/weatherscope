import { buildQuery, requestJson } from './client';
import type { LocationSearchResponse } from '../types/location';

export function searchLocations(query: string): Promise<LocationSearchResponse> {
  return requestJson<LocationSearchResponse>(
    `/locations/search${buildQuery({ q: query, count: 5, language: 'en' })}`,
  );
}

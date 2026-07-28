export interface LocationResult {
  provider_id: number | null;
  name: string;
  display_name: string;
  latitude: number;
  longitude: number;
  country: string | null;
  country_code: string | null;
  administrative_area: string | null;
  secondary_administrative_area: string | null;
  timezone: string | null;
  elevation_m: number | null;
  population: number | null;
  postcodes: string[];
}

export interface LocationSearchResponse {
  query: string;
  result_count: number;
  results: LocationResult[];
}

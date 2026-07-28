import type { ApiErrorBody } from '../types/api';

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
export const API_BASE_URL = (
  configuredBaseUrl || 'http://127.0.0.1:8000/api/v1'
).replace(/\/$/, '');

export class ApiClientError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: unknown;

  constructor(
    message: string,
    options: { status: number; code?: string; details?: unknown },
  ) {
    super(message);
    this.name = 'ApiClientError';
    this.status = options.status;
    this.code = options.code ?? 'REQUEST_FAILED';
    this.details = options.details;
  }
}

export function buildQuery(
  values: Record<string, string | number | boolean | null | undefined>,
): string {
  const parameters = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      parameters.set(key, String(value));
    }
  });
  const query = parameters.toString();
  return query ? `?${query}` : '';
}

export async function requestJson<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    });
  } catch (error) {
    throw new ApiClientError(
      'Unable to reach the WeatherScope API. Confirm that the backend is running.',
      { status: 0, code: 'NETWORK_ERROR', details: error },
    );
  }

  if (!response.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      body = null;
    }
    throw new ApiClientError(
      body?.error?.message || `Request failed with status ${response.status}.`,
      {
        status: response.status,
        code: body?.error?.code,
        details: body?.error?.details ?? body?.detail,
      },
    );
  }

  return (await response.json()) as T;
}

export function getErrorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : 'An unexpected error occurred. Please try again.';
}

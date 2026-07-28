import { useState, type FormEvent } from 'react';

import { searchLocations } from '../../api/locationsApi';
import { getErrorMessage } from '../../api/client';
import type { LocationResult } from '../../types/location';
import { ErrorMessage } from '../common/ErrorMessage';
import { LoadingState } from '../common/LoadingState';
import { CurrentLocationButton } from './CurrentLocationButton';

interface LocationSearchProps {
  selectedLocation: LocationResult | null;
  onSelect: (location: LocationResult) => void;
}

export function LocationSearch({ selectedLocation, onSelect }: LocationSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<LocationResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedQuery = query.trim();
    if (normalizedQuery.length < 2) {
      setError('Enter at least two characters for a city, town, landmark, or postal code.');
      setResults([]);
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults([]);
    try {
      const response = await searchLocations(normalizedQuery);
      setResults(response.results);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="panel location-panel" aria-labelledby="location-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Step 1</p>
          <h2 id="location-heading">Choose a location</h2>
          <p>Search by city, town, landmark, or postal code, then select the intended match.</p>
        </div>
      </div>

      <div className="location-entry-grid">
        <form className="search-form" onSubmit={handleSubmit}>
          <label htmlFor="location-query">Location</label>
          <div className="search-form__controls">
            <input
              id="location-query"
              name="location-query"
              type="search"
              value={query}
              maxLength={100}
              placeholder="Example: Philadelphia or 19104"
              autoComplete="off"
              onChange={(event) => setQuery(event.target.value)}
            />
            <button className="button button--primary" disabled={isLoading} type="submit">
              Search
            </button>
          </div>
        </form>
        <div className="location-divider" aria-hidden="true"><span>or</span></div>
        <CurrentLocationButton
          onSelect={(location) => {
            onSelect(location);
            setResults([]);
            setQuery('Current location');
          }}
        />
      </div>

      {isLoading ? <LoadingState label="Searching for matching locations…" /> : null}
      {error ? <ErrorMessage message={error} /> : null}

      {results.length > 0 ? (
        <div className="location-results" aria-live="polite">
          <p className="result-count">Select one of {results.length} matching locations:</p>
          <ul>
            {results.map((location) => {
              const key = location.provider_id ?? `${location.latitude}-${location.longitude}`;
              const isSelected =
                selectedLocation?.latitude === location.latitude &&
                selectedLocation?.longitude === location.longitude;
              return (
                <li key={key}>
                  <button
                    className="location-option"
                    type="button"
                    aria-pressed={isSelected}
                    onClick={() => {
                      onSelect(location);
                      setResults([]);
                      setQuery(location.display_name);
                    }}
                  >
                    <span className="location-option__pin" aria-hidden="true">📍</span>
                    <span>
                      <strong>{location.display_name}</strong>
                      <small>
                        {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
                        {location.timezone ? ` · ${location.timezone}` : ''}
                      </small>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}
    </section>
  );
}

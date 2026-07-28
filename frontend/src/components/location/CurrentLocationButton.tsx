import { useState } from 'react';

import type { LocationResult } from '../../types/location';

interface CurrentLocationButtonProps {
  onSelect: (location: LocationResult) => void;
}

export function CurrentLocationButton({ onSelect }: CurrentLocationButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleClick() {
    if (!navigator.geolocation) {
      setError('This browser does not support location access. Use manual search instead.');
      return;
    }

    setIsLoading(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
        onSelect({
          provider_id: null,
          name: 'Current location',
          display_name: 'Current location',
          latitude: coords.latitude,
          longitude: coords.longitude,
          country: null,
          country_code: null,
          administrative_area: null,
          secondary_administrative_area: null,
          timezone,
          elevation_m: null,
          population: null,
          postcodes: [],
        });
        setIsLoading(false);
      },
      (positionError) => {
        const message =
          positionError.code === positionError.PERMISSION_DENIED
            ? 'Location permission was denied. Use manual search or allow location access.'
            : 'Your current location could not be determined. Try manual search.';
        setError(message);
        setIsLoading(false);
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
    );
  }

  return (
    <div className="current-location-control">
      <button
        className="button button--secondary"
        disabled={isLoading}
        onClick={handleClick}
        type="button"
      >
        {isLoading ? 'Finding location…' : 'Use my current location'}
      </button>
      {error ? <p className="inline-error" role="alert">{error}</p> : null}
    </div>
  );
}

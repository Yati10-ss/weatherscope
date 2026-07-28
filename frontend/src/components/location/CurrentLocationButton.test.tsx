import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import { CurrentLocationButton } from './CurrentLocationButton';

test('uses browser coordinates to select the current location', async () => {
  const onSelect = vi.fn();

  const getCurrentPosition = vi
    .fn()
    .mockImplementation((success: PositionCallback) => {
      const coords: GeolocationCoordinates = {
        latitude: 39.95,
        longitude: -75.16,
        accuracy: 10,
        altitude: null,
        altitudeAccuracy: null,
        heading: null,
        speed: null,
        toJSON() {
          return {
            latitude: this.latitude,
            longitude: this.longitude,
            accuracy: this.accuracy,
            altitude: this.altitude,
            altitudeAccuracy: this.altitudeAccuracy,
            heading: this.heading,
            speed: this.speed,
          };
        },
      };

      const position: GeolocationPosition = {
        coords,
        timestamp: Date.now(),
        toJSON() {
          return {
            coords: coords.toJSON(),
            timestamp: this.timestamp,
          };
        },
      };

      success(position);
    });

  Object.defineProperty(navigator, 'geolocation', {
    configurable: true,
    value: { getCurrentPosition },
  });

  render(<CurrentLocationButton onSelect={onSelect} />);
  fireEvent.click(screen.getByRole('button', { name: 'Use my current location' }));

  await waitFor(() => expect(onSelect).toHaveBeenCalled());
  expect(onSelect.mock.calls[0][0]).toMatchObject({
    name: 'Current location',
    latitude: 39.95,
    longitude: -75.16,
  });
});

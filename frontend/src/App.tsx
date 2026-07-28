import { useEffect, useState } from 'react';

import { getErrorMessage } from './api/client';
import { getCurrentWeather, getFiveDayForecast } from './api/weatherApi';
import { ErrorMessage } from './components/common/ErrorMessage';
import { LoadingState } from './components/common/LoadingState';
import { UnitToggle } from './components/common/UnitToggle';
import { SavedSearchesPanel } from './components/history/SavedSearchesPanel';
import { AboutSection } from './components/layout/AboutSection';
import { Footer } from './components/layout/Footer';
import { Header } from './components/layout/Header';
import { LocationSearch } from './components/location/LocationSearch';
import { LocationMap } from './components/map/LocationMap';
import { CurrentWeatherCard } from './components/weather/CurrentWeatherCard';
import { DateRangePreview } from './components/weather/DateRangePreview';
import { ForecastList } from './components/weather/ForecastList';
import type { LocationResult } from './types/location';
import type {
  CurrentWeatherResponse,
  UnitSystem,
  WeatherRangeResponse,
} from './types/weather';

export default function App() {
  const [selectedLocation, setSelectedLocation] = useState<LocationResult | null>(null);
  const [unitSystem, setUnitSystem] = useState<UnitSystem>('metric');
  const [currentWeather, setCurrentWeather] = useState<CurrentWeatherResponse | null>(null);
  const [forecast, setForecast] = useState<WeatherRangeResponse | null>(null);
  const [isWeatherLoading, setIsWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState<string | null>(null);
  const [reloadCounter, setReloadCounter] = useState(0);
  const [historyRefreshToken, setHistoryRefreshToken] = useState(0);

  useEffect(() => {
    if (!selectedLocation) {
      setCurrentWeather(null);
      setForecast(null);
      return;
    }

    let isActive = true;
    setIsWeatherLoading(true);
    setWeatherError(null);
    setCurrentWeather(null);
    setForecast(null);

    Promise.all([
      getCurrentWeather(selectedLocation.latitude, selectedLocation.longitude, unitSystem),
      getFiveDayForecast(selectedLocation.latitude, selectedLocation.longitude, unitSystem),
    ])
      .then(([currentResponse, forecastResponse]) => {
        if (!isActive) return;
        setCurrentWeather(currentResponse);
        setForecast(forecastResponse);
      })
      .catch((error: unknown) => {
        if (!isActive) return;
        setWeatherError(getErrorMessage(error));
      })
      .finally(() => {
        if (isActive) setIsWeatherLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, [selectedLocation, unitSystem, reloadCounter]);

  return (
    <div id="top">
      <Header />
      <main>
        <section className="hero">
          <div className="container hero__inner">
            <div>
              <p className="eyebrow">Full-stack weather application</p>
              <h1>Make location and date decisions with clearer weather context.</h1>
              <p className="hero__summary">
                Search or detect a location, review live conditions, preview date ranges, and
                manage persisted weather records through complete CRUD and export workflows.
              </p>
            </div>
            <div className="hero__badge" aria-label="Application capabilities">
              <span>Real-Time Weather</span>
              <span>Your Saved Search History</span>
              <span>CSV & JSON Exports</span>
            </div>
          </div>
        </section>

        <div className="container app-layout" id="weather">
          <LocationSearch selectedLocation={selectedLocation} onSelect={setSelectedLocation} />

          {selectedLocation ? (
            <section className="selected-location" aria-live="polite">
              <div>
                <span aria-hidden="true">📍</span>
                <div>
                  <strong>{selectedLocation.display_name}</strong>
                  <small>
                    {selectedLocation.latitude.toFixed(4)}, {selectedLocation.longitude.toFixed(4)}
                    {selectedLocation.timezone ? ` · ${selectedLocation.timezone}` : ''}
                  </small>
                </div>
              </div>
              <UnitToggle
                value={unitSystem}
                disabled={isWeatherLoading}
                onChange={setUnitSystem}
              />
            </section>
          ) : null}

          {!selectedLocation ? (
            <section className="empty-state">
              <span aria-hidden="true">🧭</span>
              <h2>Start with a location</h2>
              <p>Current conditions, forecast, map, and date-range controls will appear here.</p>
            </section>
          ) : null}

          {isWeatherLoading ? <LoadingState label="Retrieving current weather and forecast…" /> : null}
          {weatherError ? (
            <ErrorMessage message={weatherError} onRetry={() => setReloadCounter((count) => count + 1)} />
          ) : null}

          {currentWeather && forecast && selectedLocation ? (
            <div className="weather-dashboard">
              <CurrentWeatherCard weather={currentWeather} />
              <ForecastList forecast={forecast} />
              <LocationMap location={selectedLocation} />
              <DateRangePreview
                location={selectedLocation}
                unitSystem={unitSystem}
                onSaved={() => setHistoryRefreshToken((value) => value + 1)}
              />
            </div>
          ) : null}

          <SavedSearchesPanel refreshToken={historyRefreshToken} />
          <AboutSection />
        </div>
      </main>
      <Footer />
    </div>
  );
}

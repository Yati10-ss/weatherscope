import { useEffect, useState, type FormEvent } from 'react';

import { getErrorMessage } from '../../api/client';
import { createWeatherSearch } from '../../api/weatherSearchesApi';
import { previewWeather } from '../../api/weatherApi';
import type { LocationResult } from '../../types/location';
import type { UnitSystem, WeatherRangeResponse } from '../../types/weather';
import { toSavedLocation, type WeatherSearchDetail } from '../../types/weatherSearch';
import { addDays, dateInputValue } from '../../utils/formatters';
import { ErrorMessage } from '../common/ErrorMessage';
import { LoadingState } from '../common/LoadingState';
import { Toast } from '../common/Toast';
import { DailyWeatherTable } from './DailyWeatherTable';

interface DateRangePreviewProps {
  location: LocationResult;
  unitSystem: UnitSystem;
  onSaved?: (search: WeatherSearchDetail) => void;
}

export function DateRangePreview({ location, unitSystem, onSaved }: DateRangePreviewProps) {
  const today = new Date();
  const [startDate, setStartDate] = useState(dateInputValue(today));
  const [endDate, setEndDate] = useState(dateInputValue(addDays(today, 4)));
  const [note, setNote] = useState('');
  const [preview, setPreview] = useState<WeatherRangeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    setPreview(null);
    setError(null);
    setSuccess(null);
  }, [location.latitude, location.longitude, unitSystem]);

  function validateRange(): boolean {
    if (!startDate || !endDate) {
      setError('Choose both a start date and an end date.');
      return false;
    }
    if (startDate > endDate) {
      setError('The start date must not be later than the end date.');
      return false;
    }
    return true;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!validateRange()) return;

    setIsLoading(true);
    setError(null);
    setSuccess(null);
    setPreview(null);
    try {
      const response = await previewWeather({
        latitude: location.latitude,
        longitude: location.longitude,
        start_date: startDate,
        end_date: endDate,
        unit_system: unitSystem,
        timezone: location.timezone,
      });
      setPreview(response);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSave() {
    if (!preview || !validateRange()) return;

    setIsSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const saved = await createWeatherSearch({
        location: toSavedLocation(location),
        start_date: startDate,
        end_date: endDate,
        unit_system: unitSystem,
        note: note.trim() || null,
      });
      setSuccess(`Saved as record #${saved.id}.`);
      onSaved?.(saved);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <>
      {success ? <Toast message={success} onClose={() => setSuccess(null)} /> : null}

      <section className="panel preview-panel" aria-labelledby="preview-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Step 2</p>
            <h2 id="preview-heading">Preview and save a date range</h2>
            <p>
              Review historical or forecast weather, add an optional note, and save the result
              to the SQLite database.
            </p>
          </div>
        </div>

        <form className="date-form" onSubmit={handleSubmit}>
          <div className="field-group">
            <label htmlFor="start-date">Start date</label>
            <input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
            />
          </div>
          <div className="field-group">
            <label htmlFor="end-date">End date</label>
            <input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
            />
          </div>
          <button className="button button--primary" disabled={isLoading} type="submit">
            Preview weather
          </button>
        </form>

        {isLoading ? <LoadingState label="Retrieving date-range weather…" /> : null}
        {error ? <ErrorMessage message={error} /> : null}

        {preview ? (
          <>
            <DailyWeatherTable weather={preview} />
            <div className="save-search-box">
              <div className="field-group">
                <label htmlFor="search-note">Optional note</label>
                <textarea
                  id="search-note"
                  maxLength={500}
                  value={note}
                  placeholder="Example: Conference travel planning"
                  onChange={(event) => setNote(event.target.value)}
                />
                <small>{note.length}/500 characters</small>
              </div>
              <button
                className="button button--primary"
                disabled={isSaving}
                type="button"
                onClick={() => void handleSave()}
              >
                {isSaving ? 'Saving…' : 'Save search to database'}
              </button>
            </div>
          </>
        ) : null}
      </section>
    </>
  );
}

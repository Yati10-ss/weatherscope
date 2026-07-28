import type { WeatherRangeResponse } from '../../types/weather';
import {
  formatCalendarDate,
  formatDuration,
  formatWeatherValue,
} from '../../utils/formatters';
import { getWeatherVisual } from '../../utils/weatherVisuals';

interface DailyWeatherTableProps {
  weather: WeatherRangeResponse;
}

export function DailyWeatherTable({ weather }: DailyWeatherTableProps) {
  return (
    <div className="preview-results" aria-live="polite">
      <div className="preview-results__summary">
        <div>
          <strong>{weather.total_days} day{weather.total_days === 1 ? '' : 's'} returned</strong>
          <span>
            {formatCalendarDate(weather.start_date)} – {formatCalendarDate(weather.end_date)}
          </span>
        </div>
        <span className="source-pill">
          {weather.source_types
            .map((source) => source[0].toUpperCase() + source.slice(1))
            .join(' + ')}
        </span>
      </div>

      <p className="table-scroll-hint">Swipe or scroll horizontally to view all columns.</p>

      <div
        className="table-wrapper"
        tabIndex={0}
        role="region"
        aria-label="Daily weather results. Scroll horizontally to view all columns."
      >
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Condition</th>
              <th>Low / High</th>
              <th>Precipitation</th>
              <th>Wind</th>
              <th>Sunshine</th>
            </tr>
          </thead>
          <tbody>
            {weather.days.map((day) => {
              const visual = getWeatherVisual(day.weather_code);
              return (
                <tr key={day.date}>
                  <td><time dateTime={day.date}>{formatCalendarDate(day.date)}</time></td>
                  <td><span aria-hidden="true">{visual.icon}</span> {day.condition}</td>
                  <td>
                    {formatWeatherValue(day.temperature_min, weather.units.temperature)} /{' '}
                    {formatWeatherValue(day.temperature_max, weather.units.temperature)}
                  </td>
                  <td>
                    {formatWeatherValue(
                      day.precipitation_sum,
                      weather.units.precipitation,
                    )}
                  </td>
                  <td>
                    {formatWeatherValue(day.wind_speed_max, weather.units.wind_speed)}
                  </td>
                  <td>{formatDuration(day.sunshine_duration_seconds)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import type { CurrentWeatherResponse } from '../../types/weather';
import { formatObservedTime, formatWeatherValue } from '../../utils/formatters';
import { getWeatherVisual } from '../../utils/weatherVisuals';

interface CurrentWeatherCardProps {
  weather: CurrentWeatherResponse;
}

export function CurrentWeatherCard({ weather }: CurrentWeatherCardProps) {
  const { current, units } = weather;
  const visual = getWeatherVisual(current.weather_code, current.is_day);

  return (
    <article className={`current-card current-card--${visual.tone}`} aria-labelledby="current-heading">
      <div className="current-card__topline">
        <div>
          <p className="eyebrow">Current conditions</p>
          <h2 id="current-heading">{current.condition}</h2>
          <p className="muted">Observed {formatObservedTime(current.observed_at_local)} local time</p>
        </div>
        <span className="weather-icon weather-icon--large" role="img" aria-label={current.condition}>
          {visual.icon}
        </span>
      </div>

      <div className="current-card__temperature">
        {formatWeatherValue(current.temperature, units.temperature)}
      </div>
      <p className="feels-like">
        Feels like {formatWeatherValue(current.apparent_temperature, units.apparent_temperature)}
      </p>

      <dl className="weather-metrics">
        <div>
          <dt>Humidity</dt>
          <dd>{current.relative_humidity_percent}{units.relative_humidity}</dd>
        </div>
        <div>
          <dt>Precipitation</dt>
          <dd>{formatWeatherValue(current.precipitation, units.precipitation)}</dd>
        </div>
        <div>
          <dt>Wind</dt>
          <dd>
            {formatWeatherValue(current.wind_speed, units.wind_speed)} {current.wind_direction_cardinal}
          </dd>
        </div>
        <div>
          <dt>Gusts</dt>
          <dd>{formatWeatherValue(current.wind_gusts, units.wind_gusts)}</dd>
        </div>
      </dl>
    </article>
  );
}

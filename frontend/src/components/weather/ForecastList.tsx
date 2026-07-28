import type { WeatherRangeResponse } from '../../types/weather';
import { formatCalendarDate, formatWeatherValue } from '../../utils/formatters';
import { getWeatherVisual } from '../../utils/weatherVisuals';

interface ForecastListProps {
  forecast: WeatherRangeResponse;
}

export function ForecastList({ forecast }: ForecastListProps) {
  return (
    <section className="panel forecast-panel" aria-labelledby="forecast-heading">
      <div className="section-heading section-heading--inline">
        <div>
          <p className="eyebrow">Planning outlook</p>
          <h2 id="forecast-heading">Five-day forecast</h2>
        </div>
        <span className="source-pill">Live API data</span>
      </div>

      <div className="forecast-grid">
        {forecast.days.map((day) => {
          const visual = getWeatherVisual(day.weather_code);
          return (
            <article className="forecast-card" key={day.date}>
              <time dateTime={day.date}>{formatCalendarDate(day.date)}</time>
              <span className="weather-icon" role="img" aria-label={day.condition}>{visual.icon}</span>
              <strong>{day.condition}</strong>
              <p className="forecast-card__temperature">
                <span>{formatWeatherValue(day.temperature_max, forecast.units.temperature)}</span>
                <span>{formatWeatherValue(day.temperature_min, forecast.units.temperature)}</span>
              </p>
              <dl>
                <div>
                  <dt>Rain</dt>
                  <dd>
                    {day.precipitation_probability_max === null
                      ? '—'
                      : `${day.precipitation_probability_max}${forecast.units.precipitation_probability}`}
                  </dd>
                </div>
                <div>
                  <dt>Wind</dt>
                  <dd>{formatWeatherValue(day.wind_speed_max, forecast.units.wind_speed)}</dd>
                </div>
              </dl>
            </article>
          );
        })}
      </div>
    </section>
  );
}

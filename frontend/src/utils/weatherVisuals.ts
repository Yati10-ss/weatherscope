interface WeatherVisual {
  icon: string;
  tone: string;
}

export function getWeatherVisual(code: number, isDay = true): WeatherVisual {
  if (code === 0) return { icon: isDay ? '☀️' : '🌙', tone: 'clear' };
  if ([1, 2].includes(code)) return { icon: isDay ? '🌤️' : '☁️', tone: 'partly' };
  if (code === 3) return { icon: '☁️', tone: 'cloudy' };
  if ([45, 48].includes(code)) return { icon: '🌫️', tone: 'fog' };
  if ([51, 53, 55, 56, 57].includes(code)) return { icon: '🌦️', tone: 'rain' };
  if ([61, 63, 65, 66, 67, 80, 81, 82].includes(code)) {
    return { icon: '🌧️', tone: 'rain' };
  }
  if ([71, 73, 75, 77, 85, 86].includes(code)) return { icon: '🌨️', tone: 'snow' };
  if ([95, 96, 99].includes(code)) return { icon: '⛈️', tone: 'storm' };
  return { icon: '🌡️', tone: 'neutral' };
}

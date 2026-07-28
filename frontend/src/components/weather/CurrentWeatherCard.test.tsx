import { render, screen } from '@testing-library/react';

import { currentWeather } from '../../test/fixtures';
import { CurrentWeatherCard } from './CurrentWeatherCard';

test('renders current condition and core weather metrics', () => {
  render(<CurrentWeatherCard weather={currentWeather} />);

  expect(screen.getByRole('heading', { name: 'Partly cloudy' })).toBeInTheDocument();
  expect(screen.getByText('29.4°C')).toBeInTheDocument();
  expect(screen.getByText(/Feels like 31.2°C/)).toBeInTheDocument();
  expect(screen.getByText('57%')).toBeInTheDocument();
});

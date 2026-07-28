import { render, screen } from '@testing-library/react';

import { forecast } from '../../test/fixtures';
import { ForecastList } from './ForecastList';

test('renders five real forecast-day cards from the response', () => {
  render(<ForecastList forecast={forecast} />);

  expect(screen.getByRole('heading', { name: 'Five-day forecast' })).toBeInTheDocument();
  expect(screen.getAllByRole('article')).toHaveLength(5);
  expect(screen.getByText('70%')).toBeInTheDocument();
});

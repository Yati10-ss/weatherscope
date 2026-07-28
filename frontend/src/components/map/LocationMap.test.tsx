import { render, screen } from '@testing-library/react';

import { philadelphia } from '../../test/fixtures';
import { LocationMap } from './LocationMap';

test('renders an OpenStreetMap view for the selected coordinates', () => {
  render(<LocationMap location={philadelphia} />);

  const frame = screen.getByTitle('Map of Philadelphia, Pennsylvania, United States');
  expect(frame).toHaveAttribute('src', expect.stringContaining('openstreetmap.org'));
  expect(screen.getByRole('link', { name: 'Open full map' })).toHaveAttribute(
    'href',
    expect.stringContaining('mlat=39.95233'),
  );
});

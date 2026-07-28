import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import * as locationsApi from '../../api/locationsApi';
import { philadelphia } from '../../test/fixtures';
import { LocationSearch } from './LocationSearch';

test('searches for a location and returns the selected result', async () => {
  vi.spyOn(locationsApi, 'searchLocations').mockResolvedValue({
    query: 'Philadelphia',
    result_count: 1,
    results: [philadelphia],
  });
  const onSelect = vi.fn();

  render(<LocationSearch selectedLocation={null} onSelect={onSelect} />);
  fireEvent.change(screen.getByLabelText('Location'), { target: { value: 'Philadelphia' } });
  fireEvent.click(screen.getByRole('button', { name: 'Search' }));

  await waitFor(() => {
    expect(screen.getByText('Philadelphia, Pennsylvania, United States')).toBeInTheDocument();
  });
  fireEvent.click(screen.getByRole('button', { name: /Philadelphia, Pennsylvania/ }));
  expect(onSelect).toHaveBeenCalledWith(philadelphia);
});

test('rejects a one-character location before calling the API', () => {
  const searchSpy = vi.spyOn(locationsApi, 'searchLocations');
  render(<LocationSearch selectedLocation={null} onSelect={vi.fn()} />);

  fireEvent.change(screen.getByLabelText('Location'), { target: { value: 'P' } });
  fireEvent.click(screen.getByRole('button', { name: 'Search' }));

  expect(screen.getByRole('alert')).toHaveTextContent('Enter at least two characters');
  expect(searchSpy).not.toHaveBeenCalled();
});

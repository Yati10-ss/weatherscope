import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

import * as searchApi from '../../api/weatherSearchesApi';
import * as weatherApi from '../../api/weatherApi';
import { forecast, philadelphia, savedSearchDetail } from '../../test/fixtures';
import { DateRangePreview } from './DateRangePreview';

test('previews, saves, and shows a fixed success notification', async () => {
  vi.spyOn(weatherApi, 'previewWeather').mockResolvedValue(forecast);
  const createSpy = vi
    .spyOn(searchApi, 'createWeatherSearch')
    .mockResolvedValue(savedSearchDetail);
  const onSaved = vi.fn();

  render(
    <DateRangePreview
      location={philadelphia}
      unitSystem="metric"
      onSaved={onSaved}
    />,
  );

  fireEvent.change(screen.getByLabelText('Start date'), {
    target: { value: '2026-07-28' },
  });
  fireEvent.change(screen.getByLabelText('End date'), {
    target: { value: '2026-08-01' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Preview weather' }));

  await screen.findByText('5 days returned');

  fireEvent.change(screen.getByLabelText('Optional note'), {
    target: { value: 'Conference planning' },
  });
  fireEvent.click(
    screen.getByRole('button', { name: 'Save search to database' }),
  );

  await waitFor(() => expect(createSpy).toHaveBeenCalled());
  expect(createSpy.mock.calls[0][0]).toMatchObject({
    start_date: '2026-07-28',
    end_date: '2026-08-01',
    note: 'Conference planning',
  });
  expect(onSaved).toHaveBeenCalledWith(savedSearchDetail);

  const notification = await screen.findByText('Saved as record #7.');
  expect(notification.closest('.toast')).not.toBeNull();
});

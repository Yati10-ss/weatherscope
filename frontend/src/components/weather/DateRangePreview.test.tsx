import { fireEvent, render, screen } from '@testing-library/react';
import { vi } from 'vitest';

import * as weatherApi from '../../api/weatherApi';
import { philadelphia } from '../../test/fixtures';
import { DateRangePreview } from './DateRangePreview';

test('rejects a reversed date range before requesting the API', () => {
  const previewSpy = vi.spyOn(weatherApi, 'previewWeather');
  render(<DateRangePreview location={philadelphia} unitSystem="metric" />);

  fireEvent.change(screen.getByLabelText('Start date'), { target: { value: '2026-08-10' } });
  fireEvent.change(screen.getByLabelText('End date'), { target: { value: '2026-08-01' } });
  fireEvent.click(screen.getByRole('button', { name: 'Preview weather' }));

  expect(screen.getByRole('alert')).toHaveTextContent(
    'The start date must not be later than the end date.',
  );
  expect(previewSpy).not.toHaveBeenCalled();
});

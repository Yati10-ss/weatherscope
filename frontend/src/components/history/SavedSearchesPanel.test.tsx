import {
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import { vi } from 'vitest';

import * as searchApi from '../../api/weatherSearchesApi';
import { savedSearch, savedSearchDetail } from '../../test/fixtures';
import { SavedSearchesPanel } from './SavedSearchesPanel';

function listResponse(page = 1, totalPages = 1, totalItems = 1) {
  return {
    items: [savedSearch],
    pagination: {
      page,
      page_size: 10,
      total_items: totalItems,
      total_pages: totalPages,
    },
  };
}

function mockSavedSearchList() {
  return vi
    .spyOn(searchApi, 'listWeatherSearches')
    .mockResolvedValue(listResponse());
}

async function expandHistoryPanel() {
  const toggle = await screen.findByRole('button', {
    name: /Saved weather searches/i,
  });

  if (toggle.getAttribute('aria-expanded') === 'false') {
    fireEvent.click(toggle);
  }

  return toggle;
}

test('is collapsed by default and expands when requested', async () => {
  mockSavedSearchList();

  render(<SavedSearchesPanel refreshToken={0} />);

  const toggle = await screen.findByRole('button', {
    name: /Saved weather searches/i,
  });

  await waitFor(() =>
    expect(searchApi.listWeatherSearches).toHaveBeenCalledWith(
      1,
      10,
      undefined,
    ),
  );

  expect(toggle).toHaveAttribute('aria-expanded', 'false');
  expect(
    screen.queryByText(
      'Philadelphia, Pennsylvania, United States',
    ),
  ).not.toBeInTheDocument();

  fireEvent.click(toggle);

  expect(toggle).toHaveAttribute('aria-expanded', 'true');
  expect(
    await screen.findByText(
      'Philadelphia, Pennsylvania, United States',
    ),
  ).toBeInTheDocument();
});

test('expands automatically after a new search is saved', async () => {
  mockSavedSearchList();

  const { rerender } = render(
    <SavedSearchesPanel refreshToken={0} />,
  );

  const toggle = await screen.findByRole('button', {
    name: /Saved weather searches/i,
  });

  expect(toggle).toHaveAttribute('aria-expanded', 'false');

  rerender(<SavedSearchesPanel refreshToken={1} />);

  await waitFor(() => {
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
  });

  expect(
    await screen.findByText(
      'Philadelphia, Pennsylvania, United States',
    ),
  ).toBeInTheDocument();

  await waitFor(() =>
    expect(searchApi.listWeatherSearches).toHaveBeenLastCalledWith(
      1,
      10,
      undefined,
    ),
  );
});

test('opens saved-search details directly below the corresponding record', async () => {
  mockSavedSearchList();
  vi
    .spyOn(searchApi, 'getWeatherSearch')
    .mockResolvedValue(savedSearchDetail);

  render(<SavedSearchesPanel refreshToken={0} />);

  await expandHistoryPanel();

  expect(
    await screen.findByText(
      'Philadelphia, Pennsylvania, United States',
    ),
  ).toBeInTheDocument();

  fireEvent.click(
    screen.getByRole('button', { name: 'View / edit' }),
  );

  const editButton = await screen.findByRole('button', {
    name: 'Edit record',
  });
  const detailPanel = editButton.closest('.detail-panel');
  const historyRecord = detailPanel?.closest('.history-record');

  expect(detailPanel).not.toBeNull();
  expect(historyRecord).not.toBeNull();
  expect(
    historyRecord?.querySelector('.history-card'),
  ).not.toBeNull();
});

test('shows the update confirmation inside the updated record detail panel', async () => {
  mockSavedSearchList();
  vi
    .spyOn(searchApi, 'getWeatherSearch')
    .mockResolvedValue(savedSearchDetail);
  vi
    .spyOn(searchApi, 'updateWeatherSearch')
    .mockResolvedValue({
      ...savedSearchDetail,
      note: 'Updated conference planning',
    });

  render(<SavedSearchesPanel refreshToken={0} />);

  await expandHistoryPanel();

  await screen.findByText(
    'Philadelphia, Pennsylvania, United States',
  );
  fireEvent.click(
    screen.getByRole('button', { name: 'View / edit' }),
  );
  fireEvent.click(
    await screen.findByRole('button', { name: 'Edit record' }),
  );

  fireEvent.change(screen.getByLabelText('Note'), {
    target: { value: 'Updated conference planning' },
  });
  fireEvent.click(
    screen.getByRole('button', { name: 'Save changes' }),
  );

  const message = await screen.findByText(
    'Saved search updated with refreshed weather data.',
  );

  expect(message.closest('.detail-panel')).not.toBeNull();
});

test('loads the next ten-record page through backend pagination', async () => {
  const listSpy = vi
    .spyOn(searchApi, 'listWeatherSearches')
    .mockResolvedValueOnce(listResponse(1, 2, 11))
    .mockResolvedValueOnce(listResponse(2, 2, 11));

  render(<SavedSearchesPanel refreshToken={0} />);

  await expandHistoryPanel();

  expect(
    await screen.findByText('Page 1 of 2'),
  ).toBeInTheDocument();

  fireEvent.click(
    screen.getByRole('button', { name: 'Next' }),
  );

  await waitFor(() =>
    expect(listSpy).toHaveBeenLastCalledWith(2, 10, undefined),
  );

  expect(
    await screen.findByText('Page 2 of 2'),
  ).toBeInTheDocument();
});

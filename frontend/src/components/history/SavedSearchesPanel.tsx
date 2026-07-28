import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from 'react';

import { getErrorMessage } from '../../api/client';
import {
  deleteWeatherSearch,
  downloadWeatherSearch,
  getWeatherSearch,
  listWeatherSearches,
  updateWeatherSearch,
} from '../../api/weatherSearchesApi';
import type {
  PaginationMeta,
  WeatherSearchDetail,
  WeatherSearchSummary,
} from '../../types/weatherSearch';
import { formatCalendarDate } from '../../utils/formatters';
import { ErrorMessage } from '../common/ErrorMessage';
import { LoadingState } from '../common/LoadingState';
import { Toast } from '../common/Toast';
import { DailyWeatherTable } from '../weather/DailyWeatherTable';

interface SavedSearchesPanelProps {
  refreshToken: number;
}

interface RecordStatus {
  searchId: number;
  message: string;
}

const PAGE_SIZE = 10;

const INITIAL_PAGINATION: PaginationMeta = {
  page: 1,
  page_size: PAGE_SIZE,
  total_items: 0,
  total_pages: 0,
};

function toRangeResponse(detail: WeatherSearchDetail) {
  return {
    provider: detail.provider as 'Open-Meteo',
    unit_system: detail.unit_system,
    requested_latitude: detail.location.latitude,
    requested_longitude: detail.location.longitude,
    provider_latitude: detail.provider_latitude,
    provider_longitude: detail.provider_longitude,
    elevation_m: detail.elevation_m,
    timezone: detail.location.timezone,
    timezone_abbreviation: detail.timezone_abbreviation,
    utc_offset_seconds: detail.utc_offset_seconds,
    start_date: detail.start_date,
    end_date: detail.end_date,
    total_days: detail.total_days,
    source_types: detail.source_types,
    units: detail.units,
    days: detail.days,
  };
}

export function SavedSearchesPanel({ refreshToken }: SavedSearchesPanelProps) {
  const [items, setItems] = useState<WeatherSearchSummary[]>([]);
  const [filter, setFilter] = useState('');
  const [appliedFilter, setAppliedFilter] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [pagination, setPagination] =
    useState<PaginationMeta>(INITIAL_PAGINATION);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<WeatherSearchDetail | null>(null);
  const [detailLoadingId, setDetailLoadingId] = useState<number | null>(null);
  const [pendingDelete, setPendingDelete] = useState<number | null>(null);
  const [editing, setEditing] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [note, setNote] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [unitSystem, setUnitSystem] =
    useState<'metric' | 'imperial'>('metric');
  const [recordStatus, setRecordStatus] =
    useState<RecordStatus | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const previousRefreshToken = useRef(refreshToken);

  const load = useCallback(
    async (pageNumber = 1, locationFilter = '') => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await listWeatherSearches(
          pageNumber,
          PAGE_SIZE,
          locationFilter.trim() || undefined,
        );

        setItems(response.items);
        setPagination(response.pagination);
      } catch (requestError) {
        setError(getErrorMessage(requestError));
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    void load(1, '');
  }, [load]);

  useEffect(() => {
    if (previousRefreshToken.current === refreshToken) {
      return;
    }

    previousRefreshToken.current = refreshToken;

    setIsExpanded(true);
    setFilter('');
    setAppliedFilter('');
    setSelected(null);
    setEditing(false);
    setRecordStatus(null);
    setPendingDelete(null);

    void load(1, '');
  }, [refreshToken, load]);

  async function openDetail(searchId: number) {
    setDetailLoadingId(searchId);
    setError(null);
    setRecordStatus(null);

    try {
      const detail = await getWeatherSearch(searchId);
      setSelected(detail);
      setNote(detail.note || '');
      setStartDate(detail.start_date);
      setEndDate(detail.end_date);
      setUnitSystem(detail.unit_system);
      setEditing(false);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setDetailLoadingId(null);
    }
  }

  async function handleExport(
    format: 'csv' | 'json',
    searchId?: number,
  ) {
    setError(null);

    try {
      await downloadWeatherSearch(format, searchId);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    }
  }

  async function confirmDelete(searchId: number) {
    setError(null);

    try {
      await deleteWeatherSearch(searchId);

      if (selected?.id === searchId) {
        setSelected(null);
      }
      if (recordStatus?.searchId === searchId) {
        setRecordStatus(null);
      }

      setPendingDelete(null);
      setToastMessage(`Record #${searchId} deleted.`);

      const nextPage =
        items.length === 1 && pagination.page > 1
          ? pagination.page - 1
          : pagination.page;

      await load(nextPage, appliedFilter);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    }
  }

  async function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;

    if (!startDate || !endDate || startDate > endDate) {
      setError('Choose a valid start and end date.');
      return;
    }

    setIsUpdating(true);
    setError(null);
    setRecordStatus(null);

    try {
      const updated = await updateWeatherSearch(selected.id, {
        note: note.trim() || null,
        start_date: startDate,
        end_date: endDate,
        unit_system: unitSystem,
      });

      setSelected(updated);
      setEditing(false);
      setRecordStatus({
        searchId: updated.id,
        message: 'Saved search updated with refreshed weather data.',
      });

      await load(pagination.page, appliedFilter);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsUpdating(false);
    }
  }

  function closeDetail() {
    setSelected(null);
    setEditing(false);
    setRecordStatus(null);
  }

  function closeOpenRecordState() {
    setSelected(null);
    setEditing(false);
    setRecordStatus(null);
    setPendingDelete(null);
    setDetailLoadingId(null);
  }

  function handleHistoryToggle() {
    if (isExpanded) {
      closeOpenRecordState();
    }

    setIsExpanded((current) => !current);
  }

  function changePage(pageNumber: number) {
    if (
      pageNumber < 1 ||
      pageNumber > pagination.total_pages ||
      pageNumber === pagination.page
    ) {
      return;
    }

    closeOpenRecordState();
    void load(pageNumber, appliedFilter);
  }

  function applyLocationFilter(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const normalizedFilter = filter.trim();
    setAppliedFilter(normalizedFilter);
    closeOpenRecordState();
    void load(1, normalizedFilter);
  }

  function clearLocationFilter() {
    setFilter('');
    setAppliedFilter('');
    closeOpenRecordState();
    void load(1, '');
  }

  const displayedCount =
    isLoading && pagination.total_items === 0
      ? '…'
      : pagination.total_items;

  return (
    <>
      {toastMessage ? (
        <Toast
          message={toastMessage}
          onClose={() => setToastMessage(null)}
        />
      ) : null}

      <section
        className="panel history-panel"
        id="saved-searches"
        aria-labelledby="history-heading"
      >
        <button
          type="button"
          className="history-panel__toggle"
          aria-expanded={isExpanded}
          aria-controls="saved-search-history-content"
          onClick={handleHistoryToggle}
        >
          <span className="history-panel__toggle-title">
            <span className="eyebrow">Persistent CRUD</span>

            <span className="history-panel__title-row">
              <span
                id="history-heading"
                className="history-panel__heading"
                role="heading"
                aria-level={2}
              >
                Saved weather searches
              </span>

              <span
                className="history-count"
                aria-label={`${pagination.total_items} saved searches`}
              >
                {displayedCount}
              </span>
            </span>

            <span className="history-panel__summary">
              Review, update, export, or delete records stored in SQLite.
            </span>
          </span>

          <span className="history-panel__toggle-meta">
            <span>{isExpanded ? 'Collapse' : 'Expand'}</span>

            <span
              className={`history-chevron ${
                isExpanded ? 'history-chevron--open' : ''
              }`}
              aria-hidden="true"
            >
              ▼
            </span>
          </span>
        </button>

        {isExpanded ? (
          <div
            id="saved-search-history-content"
            className="history-panel__content"
          >
            <div className="history-panel__toolbar">
              <p>
                Showing {items.length} of {pagination.total_items} saved
                search{pagination.total_items === 1 ? '' : 'es'}.
                {appliedFilter ? ` Filter: “${appliedFilter}”.` : ''}
              </p>

              <div className="export-group">
                <button
                  className="button button--secondary button--small"
                  type="button"
                  disabled={pagination.total_items === 0}
                  onClick={() => void handleExport('csv')}
                >
                  Export all CSV
                </button>
                <button
                  className="button button--secondary button--small"
                  type="button"
                  disabled={pagination.total_items === 0}
                  onClick={() => void handleExport('json')}
                >
                  Export all JSON
                </button>
              </div>
            </div>

            <form
              className="history-filter"
              onSubmit={applyLocationFilter}
            >
              <label htmlFor="history-filter">
                Filter saved locations
              </label>
              <div>
                <input
                  id="history-filter"
                  value={filter}
                  onChange={(event) => setFilter(event.target.value)}
                  placeholder="Example: Philadelphia"
                />
                <button
                  className="button button--secondary"
                  type="submit"
                >
                  Apply filter
                </button>
                {appliedFilter ? (
                  <button
                    className="button button--ghost"
                    type="button"
                    onClick={clearLocationFilter}
                  >
                    Clear
                  </button>
                ) : null}
              </div>
            </form>

            {error ? (
              <ErrorMessage
                message={error}
                onRetry={() =>
                  void load(pagination.page, appliedFilter)
                }
              />
            ) : null}

            {isLoading ? (
              <LoadingState label="Loading saved searches…" />
            ) : null}

            {!isLoading && items.length === 0 ? (
              <div className="history-empty">
                <strong>
                  {appliedFilter
                    ? 'No matching saved searches.'
                    : 'No saved searches yet.'}
                </strong>
                <span>
                  {appliedFilter
                    ? 'Change or clear the location filter.'
                    : 'Preview and save a date range above.'}
                </span>
              </div>
            ) : null}

            {items.length > 0 ? (
              <div className="history-list">
                {items.map((item) => {
                  const isSelected = selected?.id === item.id;
                  const itemStatus =
                    recordStatus?.searchId === item.id
                      ? recordStatus.message
                      : null;

                  return (
                    <div className="history-record" key={item.id}>
                      <article className="history-card">
                        <div>
                          <span className="history-card__id">
                            Record #{item.id}
                          </span>
                          <h3>{item.location.resolved_name}</h3>
                          <p>
                            {formatCalendarDate(item.start_date)} –{' '}
                            {formatCalendarDate(item.end_date)} ·{' '}
                            {item.total_days} day
                            {item.total_days === 1 ? '' : 's'}
                          </p>
                          {item.note ? <small>{item.note}</small> : null}
                        </div>

                        <div className="history-card__actions">
                          <button
                            className="button button--secondary button--small"
                            type="button"
                            onClick={() => void openDetail(item.id)}
                          >
                            View / edit
                          </button>
                          <button
                            className="button button--secondary button--small"
                            type="button"
                            onClick={() =>
                              void handleExport('csv', item.id)
                            }
                          >
                            CSV
                          </button>
                          <button
                            className="button button--secondary button--small"
                            type="button"
                            onClick={() =>
                              void handleExport('json', item.id)
                            }
                          >
                            JSON
                          </button>

                          {pendingDelete === item.id ? (
                            <span className="delete-confirmation">
                              <button
                                className="button button--danger button--small"
                                type="button"
                                onClick={() =>
                                  void confirmDelete(item.id)
                                }
                              >
                                Confirm delete
                              </button>
                              <button
                                className="button button--ghost button--small"
                                type="button"
                                onClick={() => setPendingDelete(null)}
                              >
                                Cancel
                              </button>
                            </span>
                          ) : (
                            <button
                              className="button button--danger-outline button--small"
                              type="button"
                              onClick={() =>
                                setPendingDelete(item.id)
                              }
                            >
                              Delete
                            </button>
                          )}
                        </div>
                      </article>

                      {detailLoadingId === item.id ? (
                        <LoadingState
                          label={`Loading record #${item.id} details…`}
                        />
                      ) : null}

                      {isSelected && selected ? (
                        <div
                          className="detail-panel"
                          aria-live="polite"
                        >
                          <div className="detail-panel__header">
                            <div>
                              <span>Record #{selected.id}</span>
                              <h3>
                                {selected.location.resolved_name}
                              </h3>
                            </div>
                            <button
                              className="button button--ghost button--small"
                              type="button"
                              onClick={closeDetail}
                            >
                              Close
                            </button>
                          </div>

                          {editing ? (
                            <form
                              className="edit-form"
                              onSubmit={handleUpdate}
                            >
                              <div className="field-group">
                                <label
                                  htmlFor={`edit-start-date-${selected.id}`}
                                >
                                  Start date
                                </label>
                                <input
                                  id={`edit-start-date-${selected.id}`}
                                  type="date"
                                  value={startDate}
                                  onChange={(event) =>
                                    setStartDate(event.target.value)
                                  }
                                />
                              </div>
                              <div className="field-group">
                                <label
                                  htmlFor={`edit-end-date-${selected.id}`}
                                >
                                  End date
                                </label>
                                <input
                                  id={`edit-end-date-${selected.id}`}
                                  type="date"
                                  value={endDate}
                                  onChange={(event) =>
                                    setEndDate(event.target.value)
                                  }
                                />
                              </div>
                              <div className="field-group">
                                <label
                                  htmlFor={`edit-units-${selected.id}`}
                                >
                                  Units
                                </label>
                                <select
                                  id={`edit-units-${selected.id}`}
                                  value={unitSystem}
                                  onChange={(event) =>
                                    setUnitSystem(
                                      event.target.value as
                                        | 'metric'
                                        | 'imperial',
                                    )
                                  }
                                >
                                  <option value="metric">Metric</option>
                                  <option value="imperial">
                                    Imperial
                                  </option>
                                </select>
                              </div>
                              <div className="field-group edit-form__note">
                                <label
                                  htmlFor={`edit-note-${selected.id}`}
                                >
                                  Note
                                </label>
                                <textarea
                                  id={`edit-note-${selected.id}`}
                                  maxLength={500}
                                  value={note}
                                  onChange={(event) =>
                                    setNote(event.target.value)
                                  }
                                />
                              </div>
                              <div className="edit-form__actions">
                                <button
                                  className="button button--primary"
                                  disabled={isUpdating}
                                  type="submit"
                                >
                                  {isUpdating
                                    ? 'Saving changes…'
                                    : 'Save changes'}
                                </button>
                                <button
                                  className="button button--ghost"
                                  disabled={isUpdating}
                                  type="button"
                                  onClick={() => setEditing(false)}
                                >
                                  Cancel
                                </button>
                              </div>
                            </form>
                          ) : (
                            <div className="detail-metadata">
                              <p>
                                <strong>Date range:</strong>{' '}
                                {formatCalendarDate(
                                  selected.start_date,
                                )}{' '}
                                –{' '}
                                {formatCalendarDate(selected.end_date)}
                              </p>
                              <p>
                                <strong>Units:</strong>{' '}
                                {selected.unit_system}
                              </p>
                              <p>
                                <strong>Note:</strong>{' '}
                                {selected.note || 'No note'}
                              </p>
                              <button
                                className="button button--secondary"
                                type="button"
                                onClick={() => {
                                  setRecordStatus(null);
                                  setEditing(true);
                                }}
                              >
                                Edit record
                              </button>
                            </div>
                          )}

                          {itemStatus ? (
                            <p
                              className="success-message detail-status-message"
                              role="status"
                            >
                              {itemStatus}
                            </p>
                          ) : null}

                          <DailyWeatherTable
                            weather={toRangeResponse(selected)}
                          />
                        </div>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            ) : null}

            {pagination.total_pages > 1 ? (
              <nav
                className="history-pagination"
                aria-label="Saved weather search pages"
              >
                <button
                  className="button button--secondary button--small"
                  type="button"
                  disabled={pagination.page <= 1 || isLoading}
                  onClick={() => changePage(pagination.page - 1)}
                >
                  Previous
                </button>

                <span>
                  Page {pagination.page} of {pagination.total_pages}
                </span>

                <button
                  className="button button--secondary button--small"
                  type="button"
                  disabled={
                    pagination.page >= pagination.total_pages ||
                    isLoading
                  }
                  onClick={() => changePage(pagination.page + 1)}
                >
                  Next
                </button>
              </nav>
            ) : null}
          </div>
        ) : null}
      </section>
    </>
  );
}

export function formatWeatherValue(
  value: number | null,
  unit: string,
  digits = 1,
): string {
  if (value === null) {
    return 'Not available';
  }
  const formatted = Number.isInteger(value) ? value.toString() : value.toFixed(digits);
  return `${formatted}${unit}`;
}

export function formatCalendarDate(value: string): string {
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${value}T00:00:00Z`));
}

export function formatObservedTime(value: string): string {
  const normalized = value.includes('T') ? value.replace('T', ' ') : value;
  return normalized;
}

export function dateInputValue(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

export function formatDuration(seconds: number | null): string {
  if (seconds === null) {
    return 'Not available';
  }
  const hours = seconds / 3600;
  return `${hours.toFixed(1)} hr`;
}

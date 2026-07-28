import type { LocationResult } from '../../types/location';

interface LocationMapProps {
  location: LocationResult;
}

function createMapUrl(latitude: number, longitude: number): string {
  const delta = 0.035;
  const bbox = [
    longitude - delta,
    latitude - delta,
    longitude + delta,
    latitude + delta,
  ].join(',');
  const params = new URLSearchParams({
    bbox,
    layer: 'mapnik',
    marker: `${latitude},${longitude}`,
  });
  return `https://www.openstreetmap.org/export/embed.html?${params.toString()}`;
}

export function LocationMap({ location }: LocationMapProps) {
  const externalUrl = `https://www.openstreetmap.org/?mlat=${location.latitude}&mlon=${location.longitude}#map=12/${location.latitude}/${location.longitude}`;
  return (
    <section className="panel map-panel" aria-labelledby="map-heading">
      <div className="section-heading section-heading--inline">
        <div>
          <p className="eyebrow">Location context</p>
          <h2 id="map-heading">Map</h2>
          <p>{location.display_name}</p>
        </div>
        <a className="button button--secondary button-link" href={externalUrl} target="_blank" rel="noreferrer">
          Open full map
        </a>
      </div>
      <iframe
        className="location-map"
        title={`Map of ${location.display_name}`}
        loading="lazy"
        src={createMapUrl(location.latitude, location.longitude)}
      />
      <small className="map-attribution">Map data © OpenStreetMap contributors.</small>
    </section>
  );
}

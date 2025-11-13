"use client";

import Map, { Marker } from "react-map-gl";
import styles from "./AfricanFlameMap.module.css";

export type GridSite = {
  name: string;
  lat: number;
  lon: number;
  glyph: string;
  status: string;
};

type FlameAtlasProps = {
  token: string;
  sites: GridSite[];
};

const INITIAL_VIEW = {
  longitude: 15,
  latitude: 2,
  zoom: 3,
};

export default function FlameAtlas({ token, sites }: FlameAtlasProps) {
  return (
    <Map
      mapboxAccessToken={token}
      initialViewState={INITIAL_VIEW}
      mapStyle="mapbox://styles/mapbox/dark-v11"
      reuseMaps
      attributionControl={false}
      style={{ width: "100%", height: "100%" }}
    >
      {sites.map((site) => (
        <Marker key={site.name} longitude={site.lon} latitude={site.lat} anchor="center">
          <div className={styles.marker}>
            <span>{site.glyph}</span>
            <p>{site.name}</p>
            <small>{site.status}</small>
          </div>
        </Marker>
      ))}
    </Map>
  );
}


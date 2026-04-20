const CLUSTER_LINK_TEXT = "#cluster";

let MapLoaded = false;

document.addEventListener("DOMContentLoaded", (event) => {
    const tabEl = document.querySelector('a[data-bs-toggle="tab"]');
    
    if (document.querySelector("#cluster").classList.contains("active")) {
        loadMap();
    }

    tabEl.addEventListener('shown.bs.tab', event => {
        if (event.target instanceof HTMLAnchorElement) {
            if (event.target.href.includes(CLUSTER_LINK_TEXT) && !MapLoaded) {
                loadMap();
            }
        }
    })
});

const loadMap = () => {
    mapboxgl.accessToken = MAPBOX_API_KEY;
    MapLoaded = true;

    const map = new mapboxgl.Map({
        container: 'map', // container ID
        center: [-71.06776, 42.35816], // starting position [lng, lat]. Note that lat must be set between -90 and 90
        zoom: 9 // starting zoom
    });

    map.on('load', () => {
        map.addSource('clusters-source', {
            'type': 'geojson',
            'data': `${ENDPOINT}/api/get-clusters.geojson`
        });

        map.addLayer({
            'id': 'circle-layer',
            'type': 'circle',
            'source': 'clusters-source',
            'paint': {
                'circle-radius': 6,
                'circle-color': [
                    'interpolate',
                    ['linear'],
                    ['get', 'cluster'],
                    0, '#f80404',
                    30, '#46c2f0',

                ],
                // 'circle-color': '#46c2f0',
                'circle-stroke-width': 2,
                'circle-stroke-color': 'white'
            }
        });
    })
};
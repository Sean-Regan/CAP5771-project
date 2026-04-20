// sets the access token, associating the map with your Mapbox account and its permissions
mapboxgl.accessToken = MAPBOX_API_KEY;

// creates the map, setting the container to the id of the div you added in step 2, and setting the initial center and zoom level of the map
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
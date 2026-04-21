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
        center: [-98.5765, 39.828175], // starting position [lng, lat]. Note that lat must be set between -90 and 90
        zoom: 3 // starting zoom
    });

    map.on('load', () => {
        map.addSource('clusters-source', {
            'type': 'geojson',
            'data': `${ENDPOINT}/api/get-clusters.geojson`
        });

        map.addLayer({
            'id': 'global-layer',
            'type': 'circle',
            'source': 'clusters-source',
            'layout': { 'visibility': 'visible' },
            'paint': {
                'circle-radius': 6,
                'circle-color': [
                    'interpolate',
                    ['linear'],
                    ['get', 'globalCluster'],
                    0, '#f80404',
                    30, '#46c2f0',

                ],
                // 'circle-color': '#46c2f0',
                'circle-stroke-width': 2,
                'circle-stroke-color': 'white'
            }
        });

        map.addLayer({
            'id': 'global-norm-layer',
            'type': 'circle',
            'source': 'clusters-source',
            'layout': { 'visibility': 'none' },
            'paint': {
                'circle-radius': 6,
                'circle-color': [
                    'interpolate',
                    ['linear'],
                    ['get', 'globalClusterNorm'],
                    0, '#f80404',
                    30, '#46c2f0',

                ],
                // 'circle-color': '#46c2f0',
                'circle-stroke-width': 2,
                'circle-stroke-color': 'white'
            }
        });

        map.addLayer({
            'id': 'local-layer',
            'type': 'circle',
            'source': 'clusters-source',
            'layout': { 'visibility': 'none' },
            'paint': {
                'circle-radius': 6,
                'circle-color': [
                    'interpolate',
                    ['linear'],
                    ['get', 'localCluster'],
                    0, '#f80404',
                    30, '#46c2f0',

                ],
                // 'circle-color': '#46c2f0',
                'circle-stroke-width': 2,
                'circle-stroke-color': 'white'
            }
        });
        
        map.addLayer({
            'id': 'local-norm-layer',
            'type': 'circle',
            'source': 'clusters-source',
            'layout': { 'visibility': 'none' },
            'paint': {
                'circle-radius': 6,
                'circle-color': [
                    'interpolate',
                    ['linear'],
                    ['get', 'localClusterNorm'],
                    0, '#f80404',
                    30, '#46c2f0',

                ],
                // 'circle-color': '#46c2f0',
                'circle-stroke-width': 2,
                'circle-stroke-color': 'white'
            }
        });        
    });

    map.on('idle', () => {
        const toggleableLayerIds = ['local-norm-layer', 'local-layer', 'global-norm-layer', 'global-layer'];
        const defaultLayer = 'global-layer';
        for (const id of toggleableLayerIds) {
            const linkId = `${id}`
            
            const undashed = id.replace(/-/g, ' ');
            const linkText = undashed.replace(/\w\S*/g, text => text.charAt(0).toUpperCase() + text.substring(1).toLowerCase());
            
            if (!map.getLayer(id)) {
                return;
            }

            if (document.getElementById(linkId)) {
                continue;
            }

            const link = document.createElement('a');
            link.id = linkId;
            link.href = '#';
            link.textContent = linkText;
            if (id === defaultLayer) {
                link.className = 'active';
            } else {
                link.className = '';
            }

            link.onclick = (e) => {
                const clickedLayer = link.id;
                e.preventDefault();
                e.stopPropagation();

                const otherLayerIds = toggleableLayerIds.filter((val, _) => val !== linkId);
                for (const otherId of otherLayerIds) {
                    const otherElement = document.getElementById(otherId);
                    if (otherElement instanceof HTMLAnchorElement) {
                        otherElement.className = '';
                    }

                    map.setLayoutProperty(otherId, 'visibility', 'none')
                }

                link.className = 'active';
                map.setLayoutProperty(
                    clickedLayer,
                    'visibility',
                    'visible'
                );  
            }

            const layers = document.getElementById('map-overlay');
            layers.appendChild(link);
        }
    });
};
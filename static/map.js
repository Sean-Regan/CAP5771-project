const CLUSTER_LINK_TEXT = "#cluster";

let MapLoaded = false;

let selectedFeature = null;
const card = document.getElementById('map-overlay');

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

const showCard = (feature) => {
    console.log('showing card');
    card.innerHTML = `
        <div class="map-overlay-inner">
            <code>Point Properties</code><hr>
            ${Object.entries(feature.properties)
                .map(([key, value]) => `<li><b>${key}</b>: ${value}</li>`)
                .join('')}
        </div>`;

    card.style.display = 'block';
};

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
            'data': `${ENDPOINT}/api/get-clusters.geojson`,
            'generateId': true
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

        const toggleableLayerIds = ['local-norm-layer', 'local-layer', 'global-layer'];
        
        for (const layer of toggleableLayerIds) {
            map.addInteraction(`click-${layer}`, {
                type: 'click',
                target: { layerId: layer },
                handler: ({ feature }) => {
                    if (selectedFeature) {
                        map.setFeatureState(selectedFeature, { selected: false });
                    }

                    selectedFeature = feature;
                    map.setFeatureState(feature, { selected: true });
                    showCard(feature);
                }
            });

            // Clicking on the map will deselect the selected feature
            map.addInteraction(`map-click-${layer}`, {
                type: 'click',
                handler: () => {
                    if (selectedFeature) {
                        map.setFeatureState(selectedFeature, { selected: false });
                        selectedFeature = null;
                        card.style.display = 'none';
                    }
                }
            });

            // Hovering over a feature will highlight it
            map.addInteraction(`mouseenter-${layer}`, {
                type: 'mouseenter',
                target: { layerId: layer },
                handler: ({ feature }) => {
                    map.setFeatureState(feature, { highlight: true });
                    map.getCanvas().style.cursor = 'pointer';
                }
            });

            // Moving the mouse away from a feature will remove the highlight
            map.addInteraction(`mouseleave-${layer}`, {
                type: 'mouseleave',
                target: { layerId: layer },
                handler: ({ feature }) => {
                    map.setFeatureState(feature, { highlight: false });
                    map.getCanvas().style.cursor = '';
                    return false;
                }
            });
        }
    });

    map.on('idle', () => {
        const toggleableLayerIds = ['local-norm-layer', 'local-layer', 'global-layer'];
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

            const layers = document.getElementById('map-header');
            layers.appendChild(link);
        }
    });
};
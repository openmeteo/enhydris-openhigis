enhydris.openhigis = {};
enhydris.openhigis.map = L.map('openhigis-map');

enhydris.openhigis.map.setUp = function () {
  this.setView([38, 23.5], 7);
  this.setUpControls();
  this.setUpBaseLayers();
  this.setUpOverlayLayers();
};

enhydris.openhigis.map.setUpControls = function () {
  L.control.scale().addTo(this);
  L.control.mousePosition(
    {
      position: 'bottomright',
      emptyString: '',
    },
  ).addTo(this);
};

enhydris.openhigis.map.setUpBaseLayers = function () {
  this.layersControl = L.control.layers(
    enhydris.mapBaseLayers, {},
  ).addTo(this);
  enhydris.mapBaseLayers[enhydris.mapDefaultBaseLayer].addTo(this);
};

enhydris.openhigis.map.setUpOverlayLayers = async function () {
  await this.addStationsLayer();
  this.addOpenhiLayer('Watercourses', 'Υδρογραφικό δίκτυο', '#33CCFF', '⌇', false);
  this.addOpenhiLayer('StandingWaters', 'Λίμνες', '#33CCFF', '■', false);
  this.addOpenhiLayer(
    'StationBasins', 'Λεκάνες ανάντη σταθμών', '#0066FF', '▮', false,
  );
  this.addOpenhiLayer('RiverBasins', 'Λεκάνες απορροής', '#0066FF', '▮', true);
};

enhydris.openhigis.map.addStationsLayer = async function () {
  const url = enhydris.openhigis.ows_url + L.Util.getParamString(
    {
      service: 'WFS',
      version: '1.1.0',
      request: 'GetFeature',
      outputFormat: 'geojson',
      typeName: 'stations',
      maxFeatures: '500',
      srsName: 'EPSG:4326',
    },
    enhydris.openhigis.ows_url,
  );
  const response = await fetch(url);
  const text = await response.text();
  const data = await JSON.parse(text);
  const layer = L.geoJSON(
    data,
    {
      pointToLayer: (feature, latlng) => L.marker(latlng, {}),
      onEachFeature: (feature, aLayer) => {
        const { name } = feature.properties;
        const { id } = feature.properties;
        aLayer.bindPopup(
          `<p>Σταθμός <b>${name}</b></p>`
                    + `<p><a href="/stations/${id}/">Λεπτομέρειες...</a></p>`,
        );
      },
    },
  );
  this.layersControl.addOverlay(layer, 'Σταθμοί');
  layer.addTo(this);
};

/* This is a replacement for BetterWMS's getFeatureInfoUrl() which adds the
 * feature_count parameter. It is used in addOpenhiLayer() below to monkey patch
 * layer.getFeatureInfoUrl().
 */
enhydris.openhigis.map.getFeatureInfoUrl = function (latlng) {
  const map = this._map; /* eslint no-underscore-dangle: "off" */
  const url = this._url; /* eslint no-underscore-dangle: "off" */
  const point = map.latLngToContainerPoint(latlng, map.getZoom());
  const size = map.getSize();

  const params = {
    request: 'GetFeatureInfo',
    service: 'WMS',
    srs: 'EPSG:4326',
    styles: this.wmsParams.styles,
    transparent: this.wmsParams.transparent,
    version: this.wmsParams.version,
    format: this.wmsParams.format,
    bbox: map.getBounds().toBBoxString(),
    height: size.y,
    width: size.x,
    layers: this.wmsParams.layers,
    query_layers: this.wmsParams.layers,
    info_format: 'text/html',
    feature_count: '5',
  };

  params[params.version === '1.3.0' ? 'i' : 'x'] = point.x;
  params[params.version === '1.3.0' ? 'j' : 'y'] = point.y;

  return url + L.Util.getParamString(params, url, true);
};

enhydris.openhigis.map.addOpenhiLayer = function (
  name, legendText, legendSymbolColor, legendSymbol, initiallyVisible,
) {
  const layer = L.tileLayer.betterWms(enhydris.openhigis.ows_url, {
    layers: name,
    format: 'image/png',
    transparent: true,
  });
  layer.getFeatureInfoUrl = enhydris.openhigis.map.getFeatureInfoUrl;
  const legend = `<span style="color: ${legendSymbolColor}; font-size: large">${
    legendSymbol}</span> ${legendText}`;
  this.layersControl.addOverlay(layer, legend);
  if (initiallyVisible) {
    layer.addTo(this);
  }
};

enhydris.openhigis.map.search = function () {
  const searchText = document.getElementById('search_input').value.trim();
  if (searchText === '') {
    return;
  }
  const xhr = new XMLHttpRequest();
  let searchResult = [];
  xhr.onload = function () {
    if (xhr.status < 200 || xhr.status > 299) {
      return;
    }
    searchResult = xhr.responseText.split(' ').map((x) => parseFloat(x));
    enhydris.openhigis.map.zoomTo(searchResult);
  };
  xhr.open('GET', `${enhydris.openhigis.base_url}search/${searchText}`);
  xhr.send();
};

enhydris.openhigis.map.zoomTo = function (searchResult) {
  this.fitBounds([
    [searchResult[1], searchResult[0]],
    [searchResult[3], searchResult[2]],
  ]);
};

enhydris.openhigis.map.setUp();

Object.assign(enhydris.map, {
  create() {
      this.setUpMap();
      this.setupStationsLayer();
      if (enhydris.mapMode === 'many-stations') {
        this.addGeoOverlayLayers();
        document.querySelector('.form-geosearch').addEventListener("submit", enhydris.map.search);
      }
  },

  addGeoOverlayLayers() {
    this.addOpenhiLayer('Watercourses', 'Υδατορεύματα', '#33CCFF', '⌇', false);
    this.addOpenhiLayer('StandingWaters', 'Λίμνες', '#33CCFF', '■', false);
    this.addOpenhiLayer(
      'StationBasins', 'Λεκάνες ανάντη σταθμών', '#0066FF', '▮', false,
    );
    this.addOpenhiLayer('RiverBasins', 'Λεκάνες απορροής', '#0066FF', '▮', false);
    this.addOpenhiLayer('DrainageBasins', 'Υπολεκάνες απορροής', '#0066FF', '▮', false);
  },

  /* This is a replacement for BetterWMS's getFeatureInfoUrl() which adds the
  * feature_count parameter. It is used in addOpenhiLayer() below to monkey patch
  * layer.getFeatureInfoUrl().
  */
  getFeatureInfoUrl(latlng) {
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
  },

  addOpenhiLayer(name, legendText, legendSymbolColor, legendSymbol, initiallyVisible) {
    const layer = L.tileLayer.betterWms(enhydris.openhigis.ows_url, {
      layers: name,
      format: 'image/png',
      transparent: true,
    });
    layer.getFeatureInfoUrl = this.getFeatureInfoUrl;
    const legend = `<span style="color: ${legendSymbolColor}; font-size: large">${
      legendSymbol}</span> ${legendText}`;
    this.layerControl.addOverlay(layer, legend);
    if (initiallyVisible) {
      layer.addTo(this.leafletMap);
    }
  },

  search(event) {
    const searchText = document.querySelector('#geosearch_input').value.trim();
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
      enhydris.map.zoomTo(searchResult);
    };
    xhr.open('GET', enhydris.openhigis.search_url.replace('SEARCH_TERM', searchText));
    xhr.send();
    event.preventDefault();
  },

  zoomTo(searchResult) {
    this.leafletMap.fitBounds([
      [searchResult[1], searchResult[0]],
      [searchResult[3], searchResult[2]],
    ]);
  },
});

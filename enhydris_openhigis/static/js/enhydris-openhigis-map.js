"use strict";

openhigis.map = L.map("openhigis-map");

openhigis.map.setUp = function() {
    this.setView([38, 23.5], 7);
    this.setUpControls();
    this.setUpBaseLayers();
    this.setUpOverlayLayers();
};

openhigis.map.setUpControls = function() {
    L.control.scale().addTo(this);
    L.control.mousePosition(
        {
            "position": "bottomright",
            "emptyString": "",
        }
    ).addTo(this);
};

openhigis.map.setUpBaseLayers = function() {
    this.layersControl = L.control.layers(
        enhydris.mapBaseLayers, {}
    ).addTo(this);
    enhydris.mapBaseLayers[enhydris.mapDefaultBaseLayer].addTo(this);
};

openhigis.map.setUpOverlayLayers = function() {
    this.addOpenhiLayer("Watercourses", "Υδρογραφικό δίκτυο", "#33CCFF", "□", true);
    this.addOpenhiLayer("StandingWaters", "Λίμνες", "#33CCFF", "■", true);
    this.addOpenhiLayer(
        "StationBasins", "Λεκάνες ανάντη σταθμών", "#0066FF", "▮", false
    );
    this.addOpenhiLayer("RiverBasins", "Λεκάνες απορροής", "#0066FF", "▮", true);
};

/* This is a replacement for BetterWMS's getFeatureInfoUrl() which adds the
 * feature_count parameter. It is used in addOpenhiLayer() below to monkey patch
 * layer.getFeatureInfoUrl().
 */
openhigis.map.getFeatureInfoUrl = function (latlng) {
    var point = this._map.latLngToContainerPoint(latlng, this._map.getZoom()),
        size = this._map.getSize(),

    params = {
        request: 'GetFeatureInfo',
        service: 'WMS',
        srs: 'EPSG:4326',
        styles: this.wmsParams.styles,
        transparent: this.wmsParams.transparent,
        version: this.wmsParams.version,
        format: this.wmsParams.format,
        bbox: this._map.getBounds().toBBoxString(),
        height: size.y,
        width: size.x,
        layers: this.wmsParams.layers,
        query_layers: this.wmsParams.layers,
        info_format: 'text/html',
        feature_count: '5',
    };

    params[params.version === '1.3.0' ? 'i' : 'x'] = point.x;
    params[params.version === '1.3.0' ? 'j' : 'y'] = point.y;

    return this._url + L.Util.getParamString(params, this._url, true);
};

openhigis.map.addOpenhiLayer = function(
    name, legendText, legendSymbolColor, legendSymbol, initiallyVisible
) {
    var layer = L.tileLayer.betterWms(openhigis.ows_url, {
        layers: name,
        format: "image/png",
        transparent: true,
    });
    layer.getFeatureInfoUrl = openhigis.map.getFeatureInfoUrl;
    var legend = '<span style="color: ' + legendSymbolColor + '; font-size: large">'
        + legendSymbol + '</span> ' + legendText;
    this.layersControl.addOverlay(layer, legend);
    if (initiallyVisible) {
      layer.addTo(this);
    };
};

openhigis.map.setUp();

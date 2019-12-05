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

openhigis.map.setUpOverlayLayers = async function() {
    await this.addStationsLayer();
    this.addOpenhiLayer("Watercourses", "Υδρογραφικό δίκτυο", "#33CCFF", "⌇", true);
    this.addOpenhiLayer("StandingWaters", "Λίμνες", "#33CCFF", "■", true);
    this.addOpenhiLayer(
        "StationBasins", "Λεκάνες ανάντη σταθμών", "#0066FF", "▮", false
    );
    this.addOpenhiLayer("RiverBasins", "Λεκάνες απορροής", "#0066FF", "▮", true);
};

openhigis.map.addStationsLayer = async function() {
    var url = openhigis.ows_url + L.Util.getParamString(
        {
            service: "WFS",
            version: "1.1.0",
            request: "GetFeature",
            outputFormat: "geojson",
            typeName: "stations",
            maxFeatures: "500",
            srsName: "EPSG:4326",
        },
        openhigis.ows_url,
    );
    var response = await fetch(url);
    var text = await response.text();
    var data = await JSON.parse(text);
    var layer = L.geoJSON(
        data,
        {
            pointToLayer: (feature, latlng) => L.marker(latlng, {}),
            onEachFeature: (feature, layer) => {
                var name = feature.properties.name;
                var id = feature.properties.id;
                layer.bindPopup(
                    "<p>Σταθμός <b>" + name + "</b></p>" +
                    '<p><a href="/stations/' + id + '/">Λεπτομέρειες...</a></p>'
                );
            },
        },
    );
    this.layersControl.addOverlay(layer, "Σταθμοί");
    layer.addTo(this);
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

openhigis.map.search = function() {
    var search_text = document.getElementById("search_input").value.trim();
    if (search_text === "") {
        return;
    }
    var xhr = new XMLHttpRequest();
    var search_result = [];
    xhr.onload = function() {
        if (xhr.status < 200 || xhr.status > 299) {
            return;
        }
        search_result = xhr.responseText.split(" ").map(x => parseFloat(x));
        openhigis.map.zoomTo(search_result);
    };
    xhr.open("GET", openhigis.base_url + "search/" + search_text);
    xhr.send();
    return false;
};

openhigis.map.zoomTo = function(search_result) {
    this.fitBounds([
        [search_result[1], search_result[0]],
        [search_result[3], search_result[2]],
    ]);
}

openhigis.map.setUp();

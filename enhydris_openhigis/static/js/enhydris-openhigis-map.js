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
    this.addRiverBasinDistricts();
};

openhigis.map.addRiverBasinDistricts = function() {
    var layer = L.tileLayer.betterWms(openhigis.ows_url, {
        layers: "RiverBasinDistricts",
        format: "image/png",
        transparent: true,
    });
    this.layersControl.addOverlay(layer, "Υδατικά διαμερίσματα");
};

openhigis.map.setUp();

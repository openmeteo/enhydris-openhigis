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
    this.addOpenhiLayer("RiverBasinDistricts", "Υδατικά διαμερίσματα");
    this.addOpenhiLayer("RiverBasins", "Λεκάνες απορροής");
};

openhigis.map.addOpenhiLayer = function(name, legend) {
    var layer = L.tileLayer.betterWms(openhigis.ows_url, {
        layers: name,
        format: "image/png",
        transparent: true,
    });
    this.layersControl.addOverlay(layer, legend);
};

openhigis.map.setUp();

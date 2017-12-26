BASECOORDS = [48.25,18.450001]
var globalDistance = 50000

function makeMap() {
    var ACCESS_TOKEN = '';
    var MB_ATTR = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
			'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
			'Imagery © <a href="http://mapbox.com">Mapbox</a>';
    var MB_URL = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=' + ACCESS_TOKEN;

    mymap = L.map('llmap',{zoomControl: false}).setView(BASECOORDS, 8);

    L.tileLayer(MB_URL, {attribution: MB_ATTR, id: 'mapbox.streets'}).addTo(mymap);

    //mymap.on('click', onMapClick);
    L.control.zoom({position:'topright'}).addTo(mymap);
}

var personIcon =  new L.Icon({
        iconUrl: './static/images/person.png',
        shadowUrl: '',
        iconSize: [40, 45],
        popupAnchor:  [0,-20]
    });
var homeIcon =  new L.Icon({
        iconUrl: './static/images/home.png',
        shadowUrl: '',
        iconSize: [40, 45],
        popupAnchor:  [0,-20]
    });
var safeHouseIcon =  new L.Icon({
        iconUrl: './static/images/rescue.png',
        shadowUrl: '',
        iconSize: [40, 45],
        popupAnchor:  [0,-20]
    });
var gasIcon =  new L.Icon({
        iconUrl: './static/images/gas.png',
        shadowUrl: '',
        iconSize: [40, 45],
        popupAnchor:  [0,-20]
    });
var superIcon =  new L.Icon({
        iconUrl: './static/images/super.png',
        shadowUrl: '',
        iconSize: [40, 45],
        popupAnchor:  [0,-20]
    });
var layer = L.layerGroup();
var layerRadiuses = L.layerGroup();
var layerRadiusesSmall = L.layerGroup();
var layerElipsa = L.layerGroup();
var layerNearPumps = L.layerGroup();
var layerNearSuper = L.layerGroup();
var layerRoad = L.layerGroup();
var layerRiver = L.layerGroup();
var layerControl = L.layerGroup();
var popup = L.popup();
var personMarker = null;
var homeMarker = null;
var actualPowerPlant = null;
var actualPowerPlantMarker = null;
var layerSafeHouse = L.layerGroup();
var control = null;


function renderData() {
    var radioIcon =  new L.Icon({
        iconUrl: './static/images/radiation.png',
        shadowUrl: '',
        iconSize: [40, 45],
        popupAnchor:  [0,-20]
    });
    $.getJSON("/plants/", function(obj) {
        var markers = obj.data.map(function(arr) {
            return L.marker([arr[0], arr[1]],{icon: radioIcon})
                    .bindPopup(arr[2])
                    .on('click', function(e) {
                        mymap.removeLayer(layerRadiuses);
                        mymap.removeLayer(layerRadiusesSmall);
                        if (actualPowerPlant == arr[2]) 
                        {
                            actualPowerPlant = null;
                            actualPowerPlantMarker.closePopup();
                            actualPowerPlantMarker = null;
                        }
                        else 
                        {
                            actualPowerPlant =  arr[2];
                            actualPowerPlantMarker = this;
                            layerRadiuses = L.layerGroup( [L.circle([arr[0], arr[1]],globalDistance,{color: "orange"}) ]);
                            mymap.addLayer(layerRadiuses);
                            layerRadiusesSmall = L.layerGroup([ L.circle([arr[0], arr[1]],15000,{color: "red"}) ]);
                            mymap.addLayer(layerRadiusesSmall);
                        }
                    })
        });
        mymap.removeLayer(layer);
        layer = L.layerGroup(markers);
        mymap.addLayer(layer);
    })
}


function showWayHome() {
    if (actualPowerPlant)
        $.getJSON("/safehouse/lat="+personMarker.getLatLng().lat + ",lon=" + personMarker.getLatLng().lng
                    + ",lat="+homeMarker.getLatLng().lat + ",lon=" + homeMarker.getLatLng().lng 
                    + ",plant=" + actualPowerPlant + ",distance=" + globalDistance
                    , function(obj) {

                var latlngs = Array();
                var safeMarker = obj.data.map(function(arr) {
                    return L.marker([arr[1], arr[0]],{icon: safeHouseIcon, draggable: true}).bindPopup(arr[2] ? arr[2] : 'Miestny Obecny Urad')
                });

                mymap.removeLayer(layerSafeHouse);
                layerSafeHouse = L.layerGroup(safeMarker);
                mymap.addLayer(layerSafeHouse);

                latlngs.push(personMarker.getLatLng());
                latlngs.push(safeMarker[0].getLatLng());
                latlngs.push(homeMarker.getLatLng());

                if (control)
                    mymap.removeControl(control);

                control = L.Routing.control({
                      waypoints: latlngs,
                      show: false,
                      waypointMode: 'connect',
                      createMarker: function() {}
                    }).addTo(mymap);
        })
    else
        modal.style.display = "block";
}

function showContRivers() {
    if (actualPowerPlant)
        $.getJSON("/rivers/plant="+ actualPowerPlant + ",distance=" + globalDistance, function(obj) {
            if (layerRiver)
                mymap.removeLayer(layerRiver);
            var myStyle = {
                    "color": "#FF0101",
                    "weight": 3,
                    "opacity": 1
                };
            layerRiver = new L.GeoJSON(null,{
                style: myStyle
            }).addTo(mymap);
            layerRiver.addData(obj.data);
        })
    else
        modal.style.display = "block";
}

function showNearPumps() {
    if (actualPowerPlant)
    {
        $.getJSON("/pumps/lat="+personMarker.getLatLng().lat + ",lon=" + personMarker.getLatLng().lng + ",plant="+ actualPowerPlant + ",distance=" + globalDistance, function(obj) {
            var nearPumps = obj.data.map(function(arr) {
                return L.marker([arr[1], arr[0]],{icon: gasIcon}).bindPopup(arr[2] ? arr[2] : 'Genericka benzinka')
            });
            mymap.removeLayer(layerNearPumps);
            layerNearPumps = L.layerGroup(nearPumps);
            mymap.addLayer(layerNearPumps);
        })
        $.getJSON("/supermarkets/lat="+personMarker.getLatLng().lat + ",lon=" + personMarker.getLatLng().lng + ",plant="+ actualPowerPlant + ",distance=" + globalDistance, function(obj) {
            var nearSuper = obj.data.map(function(arr) {
                return L.marker([arr[1], arr[0]],{icon: superIcon}).bindPopup(arr[2] ? arr[2] : 'Genericky obchod')
            });
            mymap.removeLayer(layerNearSuper);
            layerNearSuper = L.layerGroup(nearSuper);
            mymap.addLayer(layerNearSuper);
        })
    }  
    else
        modal.style.display = "block";
}

function clearMap() {
    if (layerRiver)
        mymap.removeLayer(layerRiver);
    if (layerRadiuses)
        mymap.removeLayer(layerRadiuses);
    if (layerRadiusesSmall)
        mymap.removeLayer(layerRadiusesSmall);
    if (layerNearPumps)
        layerNearPumps.clearLayers();
    if (layerNearSuper)
        layerNearSuper.clearLayers();
    actualPowerPlantMarker.closePopup();
    actualPowerPlant = null;
    if (control)
    {
        mymap.removeLayer(layerSafeHouse);
        mymap.removeControl(control);   
    }
}

/* MODAL WINDOW */
// Get the modal
var modal = document.getElementById('myModal');
// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];
// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}
// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}

var slider = document.getElementById("myRange");
var output = document.getElementById("demo");
output.innerHTML = slider.value;

slider.oninput = function() {
  output.innerHTML = this.value;
  globalDistance = slider.value * 1000;
}

$(function() {
    makeMap();
    renderData();
    personMarker = L.marker([48.53924002732588,18.616333007812504],{icon: personIcon, draggable: true}).addTo(mymap);
    homeMarker = L.marker([48.36435993073773,19.259033203125004],{icon: homeIcon, draggable: true}).addTo(mymap);
})

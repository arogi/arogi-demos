function mclpAjaxTrigger(){

  var pointMarkers2;
  var useThisPValue = document.getElementById('myPValue').innerHTML;
  var useThisDistanceValue = document.getElementById('myDistanceValue').innerHTML;

  // update the GeoJSON with the latest parameter values
  // initialize the rest
  answeredGeoJson.properties.pValue = Number(useThisPValue);
  answeredGeoJson.properties.distanceValue = Number(useThisDistanceValue);
  answeredGeoJson.properties.efficacyPercentage = Number(-1);
  answeredGeoJson.properties.demandTotal = Number(-1);
  answeredGeoJson.properties.demandCovered = Number(-1);

  var useTheseMarkers = JSON.stringify(answeredGeoJson);

  var redIcon = L.icon({
      iconUrl: '/images/ff0000.png',
      iconSize:     [10, 10], // size of the icon
      iconAnchor:   [5, 5], // point of the icon which will correspond to marker's location
  });

  var yellowIcon = L.icon({
      iconUrl: '/images/ffffb2.png',
      iconSize:     [2, 2], // size of the icon
      iconAnchor:   [1, 1], // point of the icon which will correspond to marker's location
  });




  $.ajax({
    type: 'POST',
    url: "interface/mclp_interface.py",  // deliver the data to this script... it will answer back with a solution
    data: {useTheseMarkers:useTheseMarkers},
    success: function(answerText)
    {
      // overwrites and displays existing answeredGeoJson...
      // with the response GeoJSON from the server
      answeredGeoJson = JSON.parse(answerText);
      document.getElementById('solutionQuality').innerHTML = ((answeredGeoJson.properties.efficacyPercentage)*100).toFixed(1) + "%";
      // document.getElementById('solutionQuality').innerHTML = answerText;

      // erase existing coverage circles, if they exist
      // the following commented lines are an earlier version... testing to see if the following active lines
      // are a better implementation.

      // anotherCounter = 0;
      // while (anotherCounter < simpleCount) {
      //     if (circleArray[anotherCounter] != undefined) {
      //         map.removeLayer(circleArray[anotherCounter]);
      //         map.removeLayer(redDots[anotherCounter]);
      //     anotherCounter++;
      //   }
      // }

      // Order of operations: remove all the cartography on the map, display the new stuff
      // clear all layers except the map background itself
      map.eachLayer(function (layer3) {
          if (layer3 != backgroundLayer) {
            map.removeLayer(layer3);
          };
      });




      // draw the new coverage circles...
      // and make them a little flashy
      setTimeout(function(){
        $(".myFade").animate({ fillOpacity: 0.2 }, 300, function() {
        });
      }, 100);
      // make an array of new circles
      simpleCount = 0;
      myRadius = (answeredGeoJson.properties.distanceValue * 1000);
      $.each(answeredGeoJson.features, function(i, v) {
          if (v.properties.facilityLocated == 1.0) {
              answerCoordinates = v.geometry.coordinates;
              circleArray[simpleCount] = new L.circle([answerCoordinates[1], answerCoordinates[0]], myRadius, {color: '#ffffff', fillColor: '#ffffff', fillOpacity: 0.9, weight:3, className:"myFade"});
              redDots[simpleCount] = new L.marker([answerCoordinates[1], answerCoordinates[0]], {draggable:'true', icon:redIcon});
              redDots[simpleCount].id = simpleCount;
              simpleCount++;
          }

      });



      //alert("number of circles: " + simpleCount);
      // add the coverage circles to the map
      newSimpleCount = 0;
      while (newSimpleCount < simpleCount) {
        circleArray[newSimpleCount].addTo(map);
        newSimpleCount++;
      }


      // clear the old map points and display the new ones
      // at least one version of these already exist because they are drawn on '$(document).ready'

      if (pointMarkers2 != undefined) {
        map.removeLayer(pointMarkers2);
      };

      pointMarkers = L.geoJson(answeredGeoJson, {
        pointToLayer: function (feature, latlng) {
          // return L.circleMarker(latlng, {radius: 1+(Math.log(feature.properties.pop+10)), fillColor: feature.properties.fillColor, color:"#000000",weight:0,opacity:1,fillOpacity: 0.9 });
          return L.circleMarker(latlng, {radius: 1.5, fillColor: "#ffff99", color:"#ffff99",weight:0,opacity:1,fillOpacity: 1 });
          // return L.marker(latlng, {icon:yellowIcon});
        }
      });
      pointMarkers.addTo(map);

      newSimpleCount = 0;
      while (newSimpleCount < simpleCount) {
        redDots[newSimpleCount].addTo(map);
        newSimpleCount++;
      };


      // enable the ability to drag red dots around, remove old circle marker, and draw a new one
      newSimpleCount = 0;
      while (newSimpleCount < simpleCount) {
        redDots[newSimpleCount].on('dragend', function(e) {
          var myMarker = e.target;
          var myPosition = myMarker.getLatLng();
          // these are the same thing now ----> alert(myMarker.id + ", " + redDots[myMarker.id].id);
          map.removeLayer(circleArray[myMarker.id]);

          setTimeout(function(){
            $(".myFade2").animate({ fillOpacity: 0.2 }, 300, function() {
            });
          }, 100);

          circleArray[myMarker.id] = new L.circle([myPosition.lat, myPosition.lng], myRadius, {color: '#ffffff', fillColor: '#ffffff', fillOpacity: 0.9, weight:3, className:"myFade2"});
          circleArray[myMarker.id].addTo(map);

          // error checking... posts lat/long in solution efficacy area
          // document.getElementById('solutionQuality').innerHTML = myPosition.lng.toFixed(2) + ", " + myPosition.lat.toFixed(2);
        });
        newSimpleCount++;
      };



    },
    error: function()
    {
      //// fail
      // document.getElementById('solutionQuality').innerHTML = answerText;
      document.getElementById('solutionQuality').innerHTML = "( solution failed )";
    }

  });

} // end of parameterAjaxTrigger function


// send data over to pmedian_interface.py
function pmedianAjaxTrigger(){

  var fc4e2aIcon = L.icon({
      iconUrl: '/images/fc4e2a.png',
      iconSize:     [10, 10], // size of the icon
      iconAnchor:   [5, 5], // point of the icon which will correspond to marker's location
  });

  var fd8d3cIcon = L.icon({
      iconUrl: '/images/fd8d3c.png',
      iconSize:     [10, 10], // size of the icon
      iconAnchor:   [5, 5], // point of the icon which will correspond to marker's location
  });

  var feb24cIcon = L.icon({
      iconUrl: '/images/feb24c.png',
      iconSize:     [10, 10], // size of the icon
      iconAnchor:   [5, 5], // point of the icon which will correspond to marker's location
  });

  var fed976Icon = L.icon({
      iconUrl: '/images/fed976.png',
      iconSize:     [10, 10], // size of the icon
      iconAnchor:   [5, 5], // point of the icon which will correspond to marker's location
  });

  var ff0000Icon = L.icon({
      iconUrl: '/images/ff0000.png',
      iconSize:     [10, 10], // size of the icon
      iconAnchor:   [5, 5], // point of the icon which will correspond to marker's location
  });

  var ffffb2Icon = L.icon({
      iconUrl: '/images/ffffb2.png',
      iconSize:     [10, 10], // size of the icon
      iconAnchor:   [5, 5], // point of the icon which will correspond to marker's location
  });

  var ffffffIcon = L.icon({
      iconUrl: '/images/ffffff.png',
      iconSize:     [10, 10], // size of the icon
      iconAnchor:   [5, 5], // point of the icon which will correspond to marker's location
  });


  // pmedianMarkers = [];

  var useThisValueForP = document.getElementById('myPValue').innerHTML;
  answeredGeoJson.properties.pValue = Number(useThisValueForP);
  var useTheseMarkers2 = JSON.stringify(answeredGeoJson);

  $.ajax({
    type: 'POST',
    url: "interface/pmedian_interface.py",  // deliver the data to this script... it will answer back with a solution
    data: {useTheseMarkers:useTheseMarkers2},
    success: function(answerText) {

      // Order of operations: remove all the cartography on the map, display the new stuff
      // clear all layers except the map background itself
      map.eachLayer(function (layer2) {
          if (layer2 != backgroundLayer) {
            map.removeLayer(layer2);
          };
      });

      newAnswer = JSON.parse(answerText);

      var inputArray = [];
      var uniquesArray = [];
      implicitAddress = -1;
      $.each(newAnswer.features, function(i, v) {
          implicitAddress = v.properties.assignedTo;
          inputArray.push(implicitAddress);
      });

      // an array of the unique assignment addresses. these are the hub addresses
      uniquesArray = NoDuplicates(inputArray)


      simpleCount2 = 0;
      littlecounter = 0;
      $.each(newAnswer.features, function(i, v) {

          // if the feature is one of the hubs (its address is in uniquesArray), the make a special marker
          // littlecounter = 0;
          /// test is the address simpleCount2 in the uniquesArray, if so, set a true flag
          // the indexof method was acting wonky, so i did this less-efficient, full-fledged check instead
          isThisAddressAHub = false;
          for (var qq = 0; qq < uniquesArray.length; qq++) {
              if (uniquesArray[qq] == simpleCount2) {
                isThisAddressAHub = true;
                break;
              }
          }

          if (isThisAddressAHub) {

              answerCoordinates2 = v.geometry.coordinates;

              // send SpiderDiagrammer: the address of the hub, a color switcher variable, hubCoordinates, json of all the points
              // the spider diagram will draw both the spokes and the end points

              SpiderDiagrammer(simpleCount2, littlecounter, answerCoordinates2, newAnswer);

              // you can use this to change the spoke colors if you wish
              switch(littlecounter%6) {
                  case 0:
                      hubColor2 = ffffffIcon;
                      break;
                  case 1:
                      hubColor2 = ffffb2Icon;
                      break;
                  case 2:
                      hubColor2 = fc4e2aIcon;
                      break;
                  case 3:
                      hubColor2 = feb24cIcon;
                      break;
                  case 4:
                      hubColor2 = fd8d3cIcon;
                      break;
                  case 5:
                      hubColor2 = fed976Icon;
                      break;
                  default:
                      mhubColor2 = ffffb2Icon;
              };

              pmedianHubs[littlecounter] = new L.marker([answerCoordinates2[1], answerCoordinates2[0]], {draggable:'false', icon:hubColor2});
              pmedianHubs[littlecounter].id = simpleCount2;

              pmedianHubs[littlecounter].addTo(map);
              littlecounter++;
          }
          simpleCount2++;
          isThisAddressAHub = false;
      });

      // document.getElementById('solutionQuality').innerHTML = answerText;

    },
    error: function(){
      //// fail

      // clear all layers except the map background itself
      map.eachLayer(function (layer2) {
          if (layer2 != backgroundLayer) {
            map.removeLayer(layer2);
          };
      });


      document.getElementById('solutionQuality').innerHTML = "(solution failed)";
    }
  });
}

function NoDuplicates(inputArray) {
    var temp = {};
    for (var i = 0; i < inputArray.length; i++)
        temp[inputArray[i]] = true;
    var uniqueArray = [];
    for (var k in temp)
        uniqueArray.push(k);
    return uniqueArray;
}

function SpiderDiagrammer(hubAddress, colorIndicator, hubCoordinates, jsonOfPoints){
    var spokeCounter = 0;
    var mySpokesArray = new Array();
    var mySpoke;


    switch(colorIndicator%6) {
        case 0:
            mySpokeColor = "#ffffff";
            break;
        case 1:
            mySpokeColor = "#ffffb2";
            break;
        case 2:
            mySpokeColor = "#fc4e2a";
            break;
        case 3:
            mySpokeColor = "#feb24c";
            break;
        case 4:
            mySpokeColor = "#fd8d3c";
            break;
        case 5:
            mySpokeColor = "#fed976";
            break;
        default:
            mySpokeColor = "#ffffb2";
    };

    spokeCounter = 0;
    $.each(newAnswer.features, function(i, v) {
      // if the feature is assignted to the hubAddress, then draw the lines
      if (v.properties.assignedTo == hubAddress) {
          spokeEnds = v.geometry.coordinates;
          mySpoke = [[hubCoordinates[1], hubCoordinates[0]],[spokeEnds[1],spokeEnds[0]]];
          mySpokesArray[spokeCounter] = L.polyline(mySpoke);

          //mySpokesArray[spokeCounter].setStyle({color: "#ffffff", weight: 1, opacity: 0.5});
          mySpokesArray[spokeCounter].setStyle({color: mySpokeColor, weight: 1, opacity: 0.5});
          mySpokesArray[spokeCounter].addTo(map);


          pmedianMarkers = new L.circleMarker([spokeEnds[1],spokeEnds[0]], {radius: 2, fillColor: mySpokeColor, color:"#ffffff",weight:0,opacity:1,fillOpacity: 1 });
          pmedianMarkers.addTo(map);
          spokeCounter++;
      }
    });


}

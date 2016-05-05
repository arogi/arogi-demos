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
      iconUrl: '/images/reddot.png',
      iconSize:     [10, 10], // size of the icon
      iconAnchor:   [5, 5], // point of the icon which will correspond to marker's location
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
      anotherCounter = 0;
      while (anotherCounter < simpleCount) {
          if (circleArray[anotherCounter] != undefined) {
              map.removeLayer(circleArray[anotherCounter]);
              map.removeLayer(redDots[anotherCounter]);
          anotherCounter++;
        }
      }

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

  var useThisValueForP = document.getElementById('myPValue').innerHTML;
  var useTheseMarkers = JSON.stringify(answeredGeoJson);

  $.ajax({
    type: 'POST',
    url: "interface/pmedian_interface.py",  // deliver the data to this script... it will answer back with a solution
    data: {useTheseMarkers:useTheseMarkers},
    success: function(answerText) {
      //// you send over the GeoJSON (useTheseMakers) and get a response (answerText)
      // All the cartographic magic happens here... (not coded)
      // for now, here is a placeholder to show the answer

      // Order of operations: remove all the cartography on the map, display the new stuff
      oneMoreCounter = 0;
      while (oneMoreCounter < simpleCount) {
          // presumably if circleArray exists, redDots does too... so...
          if (circleArray[OneMoreCounter] != undefined) {
              map.removeLayer(circleArray[oneMoreCounter]);
              map.removeLayer(redDots[oneMoreCounter]);
          oneMoreCounter++;
        }
      }




      document.getElementById('solutionQuality').innerHTML = answerText;
    },
    error: function(){
      //// fail

      // clear all layers except the map background itself
      map.eachLayer(function (layer2) {
          if (layer2 != backgroundLayer) {
            map.removeLayer(layer2);
          };
      });


      document.getElementById('solutionQuality').innerHTML = simpleCount;
    }
  });
}

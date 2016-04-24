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


  // working animation...
  // document.getElementById('solutionQuality').innerHTML = "<img src=\"ajax-loader.gif\" />";

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
              redDots[simpleCount] = new L.circle([answerCoordinates[1], answerCoordinates[0]], 100, {color: '#ff0000', fillColor: '#ff0000', fillOpacity: 1, weight:3});
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
      }




    },
    error: function()
    {
      //// fail
      document.getElementById('solutionQuality').innerHTML = answerText;
      document.getElementById('solutionQuality').innerHTML = "( solution failed )";
    }

  });

} // end of parameterAjaxTrigger function

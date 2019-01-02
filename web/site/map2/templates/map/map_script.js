function initialize() {
	lInfoBubble = undefined;
{% if Center %}
	var lOptions = {
      zoom: {{Zoom}},
      center: new google.maps.LatLng({{Center.latitude}}, {{Center.longitude}}),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
{% else %}
  {% if Latitude %}
    var lOptions = {
      zoom: {% firstof Zoom 10 %},
      center: new google.maps.LatLng({{Latitude}}, {{Longitude}}),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
  {% else %}
	var lOptions = {
      zoom: {% firstof Zoom 8 %},
      center: new google.maps.LatLng(53.800651, -1.454),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
  {% endif %}
{% endif %}
    lMap = new google.maps.Map(document.getElementById("map_canvas"), lOptions);
	
	
{% if Latitude %}
var lCentrePointMarker = {
    marker: new google.maps.Marker({
      position: new google.maps.LatLng({{Latitude}}, {{Longitude}}),
      title: 'Search From Here', 
      map : lMap,
    }),
  };
{% endif %}
	
	
{% if not Center and not Latitude %}
  function handleNoGeolocation(errorFlag) {
    if (errorFlag == true) {
      initialLocation = new google.maps.LatLng(53.800651, -1.454);
    } else {
      initialLocation = new google.maps.LatLng(53.800651, -1.454);
    }
    lMap.setCenter(initialLocation);
  }

  // Try W3C Geolocation (Preferred)
  if(navigator.geolocation) {
    browserSupportFlag = true;
    navigator.geolocation.getCurrentPosition(function(position) {
      initialLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
      lMap.setCenter(initialLocation);
    }, function() {
      handleNoGeolocation(browserSupportFlag);
    });
  // Try Google Gears Geolocation
  } else if (google.gears) {
    browserSupportFlag = true;
    var geo = google.gears.factory.create('beta.geolocation');
    geo.getCurrentPosition(function(position) {
      initialLocation = new google.maps.LatLng(position.latitude,position.longitude);
      lMap.setCenter(initialLocation);
    }, function() {
      handleNoGeoLocation(browserSupportFlag);
    });
  // Browser doesn't support Geolocation
  } else {
    browserSupportFlag = false;
    handleNoGeolocation(browserSupportFlag);
  }
{% endif %}  

    lBandDetails = new Array({{Bands.count}});

{% for band in Bands %}
lBandDetails.push({
  'id' : '{{band.id}}',
  'nn' : '{{band.name}}',
  'nm' : '{{band.name_for_map_title|safe}}',
  'sl' : '{{band.slug}}',
  'rg' : '{{band.region.name|lower}}',
  'rn' : '{{band.rehearsal_nights}}',
  'lt' : '{{band.latitude}}',  
  'lg' : '{{band.longitude}}',
  'mi' : '{{band.map_icon_name}}'
});
{% endfor %}

{% for band in Bands %}{% if band.latitude and band.longitude %}{% ifchanged band.location %}
  {# // {{band.name}}, {{band.location}}, new marker #}
  var lBand{{band.id}} = {
    html: "<b>{{band.name}}</b><br/>{% if band.rehearsal_night_1 %}Rehearsals {{band.rehearsal_nights}}<br/>{%endif%}<br/>[<a href='/bands/{{band.slug}}/'>Contest&nbsp;Results</a>]",
    section: '{{band.map_icon_name}}',
    region: '{{band.region.name|lower}}',
    marker: new google.maps.Marker({ position: new google.maps.LatLng({{band.latitude}}, {{band.longitude}}), title: '{{band.name_for_map_title|safe}}', map : lMap, {% if band.map_icon_name == "extinct" and not ShowExtinct %} visible: false, {% endif %} icon: '/site_media/map/{{band.map_icon_name}}.png' }),
  };
  lBand{{band.id}}.onClick = function(){
      if (lInfoBubble) { lInfoBubble.close(); }
      lInfoBubble = new InfoBubble({minHeight: 80, maxHeight: 200, minWidth: 300, maxWidth: 300, content: lBand{{band.id}}.html});
      lInfoBubble.open(lMap, lBand{{band.id}}.marker);
    },
  lBandDetails[{{forloop.counter0}}] = lBand{{band.id}};
{% else %}
    {# // {{band.name}}, {{band.location}}, updating previous #}
	var lPosition = {{forloop.counter0}};
	var lUpdatePosition = lPosition - 1; {# // move to previous location and add to that structure #}
	lBandDetails[lUpdatePosition].html = lBandDetails[lUpdatePosition].html + "<br/><hr/>" + "<b>{{band.name}}</b><br/>{% if band.rehearsal_night_1 %}Rehearsals {{band.rehearsal_nights}}<br/>{%endif%}<br/>{%if band.vacancies%}Vacancies: {{band.vacancies}}<br/>[{%endif%}<br/>[<a href='/bands/{{band.slug}}/'>Contest&nbsp;Results</a>]{% if band.website_url %} [<a target='_blank' href='{{band.website}}'>Band&nbsp;Website</a>]{%endif%}";
	lBandDetails[{{forloop.counter0}}] = lBandDetails[lUpdatePosition];
	
	{# // {{band.name}}, {{band.location}}, new marker #}
    var lBand{{band.id}} = {
    html: lBandDetails[lUpdatePosition].html,
    section: '{{band.map_icon_name}}',
    region: '{{band.region.name|lower}}',
    marker: new google.maps.Marker({
      position: new google.maps.LatLng({{band.latitude}}, {{band.longitude}}),
      title: '{{band.name_for_map_title|safe}}', 
      map : lMap,
      icon: '/site_media/map/{{band.map_icon_name}}.png'
    }),
  };
  lBand{{band.id}}.onClick = function(){
      if (lInfoBubble) {
        lInfoBubble.close();
      }
      lInfoBubble = new InfoBubble({minHeight: 80, maxHeight: 200, minWidth: 300, maxWidth: 300, content: lBand{{band.id}}.html});
      lInfoBubble.open(lMap, lBand{{band.id}}.marker);
    },
  lBandDetails[{{forloop.counter0}}] = lBand{{band.id}};
{% endifchanged %}{% endif %}{% endfor %}

    lVenueDetails = new Array({{Venues.count}});
{% for venue in Venues %}
{% if venue.latitude and venue.longitude %}
  var lVenue{{venue.id}} = {
    html: "<b>{{venue.name}}</b><br/>{%if venue.postcode%}Postcode: {{venue.postcode}}<br/>{%endif%}<br/>[<a href='/venues/{{venue.slug}}/'>Contests&nbsp;at&nbsp;this&nbsp;Venue</a>]",
    marker: new google.maps.Marker({
      position: new google.maps.LatLng({{venue.latitude}}, {{venue.longitude}}),
      title: '{{venue.name}}', 
      map : lMap,
      icon: '/site_media/map/venue.png'
    }),
  }
  lVenue{{venue.id}}.onClick = function(){
      if (lInfoBubble) {
        lInfoBubble.close();
      }
      lInfoBubble = new InfoBubble({minHeight: 80, maxHeight: 200, minWidth: 300, maxWidth: 300, content: lVenue{{venue.id}}.html});
      lInfoBubble.open(lMap, lVenue{{venue.id}}.marker);
    },
  lVenueDetails[{{forloop.counter0}}] = lVenue{{venue.id}};
{% endif %}
{% endfor %}

  for (var i=0; i<lBandDetails.length; i++){
    if (lBandDetails[i]) {
	    google.maps.event.addListener(lBandDetails[i].marker, "click", lBandDetails[i].onClick);
    }
  }
  
  for (var i=0; i<lVenueDetails.length; i++){
    if (lVenueDetails[i]) {
	    google.maps.event.addListener(lVenueDetails[i].marker, "click", lVenueDetails[i].onClick);
    }
  }
}

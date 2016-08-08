var map;
var markers = [];
function initMap() {
    var data = main();
    map = new google.maps.Map(document.getElementById("map"), {
        center: data["user"],
        zoom: 15
    });

    // add new pokemon to the map
    var poke_added = false;
    for (var i = 0; i < data["pokemon"].length; ++i){
        var time_left = getTimeDifference(data["pokemon"][i]["exp_time"]);
        if (time_left > 0) {
            addMarker(data, markers, i, time_left);
            poke_added = true;
        }
    }
    notifyIfExpired(poke_added);
}

function notifyIfExpired(poke_added) {
    if (!poke_added) {
        var exp_div = document.createElement("div");
        exp_div.setAttribute('id', 'all-expired');
        exp_div.innerText = "Sorry, all the Pokémon have expired :(";
        insertAfter(exp_div, document.getElementsByTagName("h1")[0]);
    }
}

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

function addMarker(data, markers, json_iter, time_left) {
    var id = data["pokemon"][json_iter]["id"];
    //var img = "https://s3.amazonaws.com/pokecrew-prod/pokemons/previews/000/000/" + id + "/original/data?1468308718";
    var img = "https://skipcdn.net/img/pokemon/small/" + id + ".png";
    var marker = new google.maps.Marker({
        position: data["pokemon"][json_iter],
        map: map,
        icon: img,
        visible: true
    });

    markers.push(marker);
    attachMessage(marker, markers.length-1, time_left);
}

function attachMessage(marker, i, time_left) {
    var infowindow = new google.maps.InfoWindow();

    timer(infowindow, i, time_left);
    marker.addListener('click', function() {
        infowindow.open(marker.get('map'), marker);
    });
    new google.maps.event.trigger(marker, 'click');
}

function timer(infowindow, i, time_left) {
    var timer = time_left, minutes, seconds;

    var setID = setInterval(function () {
        minutes = parseInt(timer / 60, 10)
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        infowindow.setContent(minutes + ":" + seconds);

        if (--timer < 0) {
            delete infowindow;
            clearMarker(markers, i);
            clearInterval(setID);
        }
    }, 1000);
}

function clearMarker(markers, i) {
    markers[i].setMap(null)
    markers[i] = null;
}

function getTimeDifference(exp_time) {
    var seconds = Math.floor((new Date).getTime()/1000);
    return exp_time - seconds;
}

function getTimeSinceEpoch(exp_time) {
    var diff_exp_time = getTimeDifference(exp_time);
    if (diff_exp_time <= 0) {
        return "";
    } else {
        return secondsToMinutes(diff_exp_time);
    }
}

function secondsToMinutes(time) {
    // Minutes and seconds
    var mins = ~~(time / 60);
    var secs = time % 60;

    // Output like "1:01" or "4:03:59" or "123:03:59"
    var ret = "";
    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
    ret += "" + secs;
    return ret;
}

function getURLParams() {
    var query = window.location.search.substring(1);
    return query;
}

function splitURLParams(query) {
    var key_vals = query.split("&");
    return key_vals;
}

function main() {
    var query = getURLParams();
    var vars = splitURLParams(query);
    var data = {
        "user": "",
        "pokemon": []
    };
    for (var i = 0; i < vars.length; ++i) {
        // get key = value pairs in poke variable
        var poke = vars[i].split("=");
        // split apart lat, lon, and expiration time
        var loc = poke[1].split(",");
        if (poke[0].toLowerCase() != "user"){
            data["pokemon"].push({
                "id": parseInt(poke[0]),
                "lat": parseFloat(loc[0]),
                "lng": parseFloat(loc[1]),
                "exp_time": parseInt(loc[2])
            });

        // special case for "user" because they don"t have an exp_time
        } else {
            data["user"] = {
                "lat": parseFloat(loc[0]),
                "lng": parseFloat(loc[1])
            };
        }
    }
    return data;
}

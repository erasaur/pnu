toggleDisplay = function(clicked_elt_id, other_elt_id) {
    var clicked_elt = document.getElementById(clicked_elt_id);
    var other_clicked_elt = document.getElementById(other_elt_id);
    clicked_elt.style.display = "block";
    other_clicked_elt.style.display = "none";
}

var android_elt = document.getElementById("enroll_android");
var ios_elt = document.getElementById("enroll_ios");

android_elt.onclick = function() {toggleDisplay("android_gif", "ios_gif");}
ios_elt.onclick = function() {toggleDisplay("ios_gif", "android_gif");}

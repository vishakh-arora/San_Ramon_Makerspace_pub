// sign in
function onSignIn(googleUser) {
    var auth2 = gapi.auth2.getAuthInstance();
    var id_token = googleUser.getAuthResponse().id_token;
    var session_id = $('#session-id').data().name;
//    alert(session_id);
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'https://lockermatch.com/login', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('Upgrade-Insecure-Requests', '1');
    xhr.withCredentials = true;
    // xhr.onload = function() {
    //   console.log('Signed in as: ' + xhr.responseText);
    // };
    xhr.send('idtoken=' + id_token);
    xhr.onreadystatechange=function() {
        if (xhr.readyState==4) {
                window.location.replace("/");
                //alert(xhr.responseText) ;
 //               res =   xhr_object.responseText ;
 //               act_on_response(res);
        }
    }
    // var profile = googleUser.getBasicProfile();
    // console.log('oren major');
    // console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
    // console.log('Name: ' + profile.getName());
    // console.log('Image URL: ' + profile.getImageUrl());
    // console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
}

// sign out
function signOut() {
  // alert('yaok');
  var auth2 = gapi.auth2.getAuthInstance();
  auth2.signOut().then(function () {
    console.log('User signed out.');
  });
}

function act_on_response(res)
{
    alert(res);
}

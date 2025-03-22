const api_headers = {
  "Accept": "application/json",
  "Content-Type": "application/json"
};

const get_auth_headers = function() {

  var headers = JSON.parse(JSON.stringify(api_headers));
  var sess_token = localStorage.getItem("sess_token");

  headers["session-token"] = "";

  if (sess_token == null) {
    return headers;
  }

  sess_token = JSON.parse(sess_token);

  if (Object.keys(sess_token).indexOf("token") >= 0) {
    headers["session-token"] = sess_token.token;
  }

  return headers;
}

const api_register = async function(username, password) {

  var user = fetch("/api/user?username=" + username + "&password=" + password, {
    method: "POST",
    headers: api_headers
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return user;
};


const api_login = async function(username, password) {

  var sess_token = fetch("/api/session?username=" + username + "&password=" + password, {
    method: "POST",
    headers: api_headers
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return sess_token;
};


const api_ping = async function() {

  var sess_token = fetch("/api/session", {
    method: "PUT",
    headers: get_auth_headers()
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return sess_token;
};


const api_logout = async function() {

  fetch("/api/session", {
    method: "DELETE",
    headers: get_auth_headers()
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
    })

};


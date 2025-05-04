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

const api_statistics = async function() {

  var result = fetch("/api/statistics", {
    method: "GET",
    headers: api_headers
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_methods = async function() {

  var result = fetch("/api/method", {
    method: "GET",
    headers: api_headers
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_workflows = async function() {

  var result = fetch("/api/workflow", {
    method: "GET",
    headers: get_auth_headers()
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_create_workflow = async function(workflow_schema) {

  var result = fetch("/api/workflow/", {
    method: "POST",
    headers: get_auth_headers(),
    body: JSON.stringify(workflow_schema)
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_modify_workflow = async function(workflow_name, workflow_schema) {

  var result = fetch("/api/workflow/" + workflow_name, {
    method: "PUT",
    headers: get_auth_headers(),
    body: JSON.stringify(workflow_schema)
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_datasets = async function() {

  var result = fetch("/api/dataset", {
    method: "GET",
    headers: get_auth_headers()
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_dataset = async function(name) {

  var result = fetch("/api/dataset/"+name, {
    method: "GET",
    headers: get_auth_headers()
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_create_dataset = async function(input_id, dataset_name) {

  const fileInput = document.getElementById(input_id);
  const file      = fileInput.files[0];

  const formData  = new FormData();
  formData.append("dataset", file, dataset_name);  

  const headers = get_auth_headers();
  delete headers["Content-Type"];

  var result = fetch("/api/dataset/" + dataset_name, {
    method:  "POST",
    body:    formData,
    headers: headers
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_get_dataset = async function(dataset_name) {

  var result = fetch("/api/dataset/" + dataset_name, {
    method: "GET",
    headers: get_auth_headers()
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};


const api_requirements = async function(analysis_schema) {

  var result = fetch("/api/analysis/requirements", {
    method: "POST",
    headers: get_auth_headers(),
    body: JSON.stringify(analysis_schema)
  })
  .then(response => response.json())
  .catch(error => {
    return {detail: error};
  })

  return result;
};

const api_analysis = async function() {

  var result = fetch("/api/analysis/", {
    method: "GET",
    headers: get_auth_headers()
  })
    .then(response => response.json())
    .catch(error => {
      return {};
    })

  return result;
};

const api_create_analysis = async function(analysis_schema) {

  var result = fetch("/api/analysis/", {
    method: "POST",
    headers: get_auth_headers(),
    body: JSON.stringify(analysis_schema)
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_modify_analysis = async function(analysis_name, analysis_schema) {

  var result = fetch("/api/analysis/" + analysis_name, {
    method: "PUT",
    headers: get_auth_headers(),
    body: JSON.stringify(analysis_schema)
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};

const api_analyze = async function(analysis_name, analysis_schema) {

  var result = fetch("/api/analysis/" + analysis_name, {
    method: "POST",
    headers: get_auth_headers(),
    body: JSON.stringify(analysis_schema)
  })
    .then(response => response.json())
    .catch(error => {
      console.error(error);
      return {};
    })

  return result;
};


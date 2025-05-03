var app = null;

const global_data = {
  state: {
    router: null,
    
    // Icons 
    // https://www.untitledui.com/free-icons/layout
    icons: {
      dashboard:    "dashboard",
      methods:      "methods",
      datasets:     "datasets",
      workflows:    "workflows",
      analysis:     "analysis",
      run:          "run",
      results:      "results",
      api:          "api",
      expander_out: "expander_out",
      expander_in:  "expander_in"
    },

    error_messages: [],

  }

};

const initialize = async function() {

  console.log("Initializing frontend")

  // Initialize router
  const routes = [
    { path: "/",          component: "page-dashboard" },
    { path: "/results",   component: "page-results" },
    { path: "/methods",   component: "page-methods" },
    { path: "/datasets",  component: "page-datasets" },
    { path: "/workflows", component: "page-workflows" },
    { path: "/analysis",  component: "page-analysis" },
    { path: "/run",       component: "page-run" },
  ];

  const router = new VueRouter({
    routes: routes,
  })

  global_data.state.router = router;

  // Initialize app
  app = new Vue({
    el: "#app",
    template: "<spa></spa>",
    router: router,
    data: {
      shared: global_data.state
    }
  })

  // Get initial data

}

const get_login_status = function() {

  var sess_token = localStorage.getItem("sess_token");

  if (sess_token == null) {
    return false;
  }

  sess_token = JSON.parse(sess_token);
  if (Object.keys(sess_token).indexOf("token") < 0) {
    return false;
  }

  var timestamp = Math.floor((new Date()).getTime() / 1000);

  if (sess_token.expires_at <= timestamp) {
    return false;
  }

  return true;
}

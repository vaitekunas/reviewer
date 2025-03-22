var app = null;

const global_data = {
  state: {
    router: null,
  }
};

const initialize = async function() {

  console.log("Initializing frontend")

  // Initialize router
  const routes = [
    { path: "/",          component: "page-dashboard" },
    { path: "/methods",   component: "page-methods" },
    { path: "/workflows", component: "page-workflows" },
    { path: "/analysis",  component: "page-analysis" },
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

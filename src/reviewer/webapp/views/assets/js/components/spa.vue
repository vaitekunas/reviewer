<name>spa</name>

<template>
  <div class="toplevel">
    <div class="screen">

      <tool-bar :toolbar_title="toolbar_title"
                :toolbar_icon="toolbar_icon"
                :logged_in="logged_in"
                v-on:login="refresh_data"
                v-on:logout="refresh_data">
      </tool-bar>

      <errors :messages="state.error_messages"></errors>

      <div class="content">
        <side-bar :logged_in="logged_in"
                  v-on:select_page="select_page($event)">
        </side-bar>

        <keep-alive>
          <router-view :logged_in="logged_in">

          </router-view
        </keep-alive>
      </div>

    </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state:         global_data.state,
    toolbar_title: "Review Analytics",
    toolbar_icon:  "dashboard",
    loading:       false,
    logged_in:     false
  }

},

computed: {

},

methods: {

  login: async function(){
    var token = await api_login(this.username, this.password);
  },

  refresh_data: async function(){
    this.logged_in = get_login_status();
    this.loading   = false;

    if(this.logged_in){
      this.state.router.push("/");
      this.toolbar_title = "Dashboard";
    }else{
      this.state.router.push("/");
      this.toolbar_title = "Review Analytics";
    }
  },

  select_page: async function(event){
    this.toolbar_title = event.page_title;
    this.toolbar_icon  = event.page_icon;
  },

},

mounted: function(){
    this.refresh_data();
},

props: []
</javascript>

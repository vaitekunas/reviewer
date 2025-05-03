<name>spa</name>

<template>
  <div class="toplevel">
    <div class="screen">

      <tool-bar :toolbar_title="toolbar_title"
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
      this.state.router.push("/analysis");
      this.toolbar_title = "Analyses";
    }else{
      this.state.router.push("/");
      this.toolbar_title = "Review Analytics";
    }
  },

  select_page: async function(page_title){
    this.toolbar_title = page_title;
  },

},

mounted: function(){
    this.refresh_data();
},

props: []
</javascript>

<name>spa</name>

<template>
  <div class="toplevel">
    <div class="screen">

      <load-screen v-if="loading">
      </load-screen>

      <tool-bar class="toolbar"
                :logged_in="logged_in"
                v-on:login="refresh_data"
                v-on:logout="refresh_data">
      </tool-bar>

      <keep-alive>
        <router-view :logged_in="logged_in">

        </router-view
      </keep-alive>

    </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    loading: false,
    logged_in: true
  }

},

computed: {

},

methods: {

  login: async function(){
    var token = await api_login(this.username, this.password);
  },

  refresh_data: async function(created){
    this.logged_in      = get_login_status();
    this.loading = false;

    if(created == undefined){
      this.state.router.push("/");
    }
  },

},

mounted: function(){
    this.logged_in = get_login_status();
},

props: []
</javascript>

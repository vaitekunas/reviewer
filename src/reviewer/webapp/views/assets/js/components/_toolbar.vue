<name>tool-bar</name>

<template>
  <div class="toolbar">

    <div class="toolbar-title">
        {{toolbar_title}}
    </div>

    <div class="running-shield" :class="{active: state.running}">Analysis running</div>

    <avatar v-on:login="$emit('login')"
            v-on:logout="$emit('logout')"></avatar>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    shield_active: false
  }
},

methods: {
},

mounted: async function(){
  var that = this;

  this.methods            = await api_methods();
  this.existing_workflows = await api_workflows();

  socket.on("workflow", async function(data) {
    that.existing_workflows = await api_workflows();
    that.methods = await api_methods();
  });

  socket.on("step", function(data) {
    that.state.running = true;
  });

  socket.on("result", async function(data) {
    that.state.running = false;
  });

},


props: ["toolbar_title", "logged_in"]
</javascript>

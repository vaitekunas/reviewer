<name>tool-bar</name>

<template>
  <div class="toolbar">

    <div class="toolbar-title">
        {{toolbar_title}}
    </div>

    <avatar v-on:login="$emit('login')"
            v-on:logout="$emit('logout')"></avatar>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state
  }
},

methods: {
},

props: ["toolbar_title", "logged_in"]
</javascript>

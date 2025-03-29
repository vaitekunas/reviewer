<name>side-button</name>

<template>
  <div class="side-button" :class="active_classname" v-on:click="navigate">
    <div class="side-button-icon">
      <div><icon :icon="icon"></icon></div>
    </div>
    <div class="side-button-text" :class="{hidden: !expanded}">{{text}}</div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state
  }
},

computed: {
  active_classname: function(){
      var path = this.state.router.currentRoute.path
      if(this.url != undefined && this.url != "" && this.url == path){
        return this.classname + " active";
      }
      return this.classname;
  }

},

methods: {
  navigate: function(){
    if(this.url){
      this.state.router.push(this.url);
    }
    this.$emit("clicked");
  }
},

props: ["icon", "text", "classname", "url", "expanded"]
</javascript>

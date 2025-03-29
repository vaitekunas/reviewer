<name>dashboard-card</name>

<template>
  <div class="dashboard-card" :class="classname" v-on:click="navigate">

    <div class="dashboard-card-background">
      <icon :icon="icon"></icon>
    </div>

    <div class="dashboard-card-title">
      {{title}}
    </div>
    <div class="dashboard-card-count">
      <div>
        {{count}}
      </div>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state
  }
},

methods: {
  navigate: function(){
    if(this.logged_in){
      this.state.router.push(this.url);
    }
  }
},

props: ["title", "count", "classname", "url", "icon", "logged_in"]
</javascript>

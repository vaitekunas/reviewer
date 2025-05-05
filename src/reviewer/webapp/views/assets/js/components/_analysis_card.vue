<name>analysis-card</name>

<template>
  <div class="dataset-wrapper" :class="{expanded: show_details}">

    <div v-if="!show_details" class="dataset" v-on:click="toggle_show_details">
      <div class="dashboard-card-background">
        <icon icon="analysis"></icon>
      </div>

      <div class="dashboard-card-title">
        {{name}}
      </div>

      <div class="workflow-card-count">
        Workflows: {{workflows.length}}
      </div>

    </div>
    
    <div v-else class="workflow-details">
     <div>
       <button class="table-closer" v-on:click="show_details=false">
         <icon icon="close"></icon>
       </button>
       Analysis: <b>{{name}}</b>
     </div>
     <analysis :workflows="workflows"
               :inactive="true">
     </analysis>
     <button v-on:click="load(name)">Load</button>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    show_details: false
  }
},

methods: {
  toggle_show_details: function(){
    this.show_details = !this.show_details;
  },

  load: function(name){
    this.state.router.push({ path: 'run', query: { name: name }});
  }
},

mounted: async function(){
},

props: ["name", "workflows"]
</javascript>

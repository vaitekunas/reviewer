<name>workflow-card</name>

<template>
  <div class="dataset-wrapper" :class="{expanded: show_details}">

    <div v-if="!show_details" class="dataset" v-on:click="toggle_show_details">
      <div class="dashboard-card-background">
        <icon icon="workflows"></icon>
      </div>

      <div class="dashboard-card-title">
        {{name}}
      </div>

      <div class="workflow-card-count">
        Steps: {{steps.length}}
      </div>

    </div>
    
    <div v-else class="workflow-details">
     <div>
       <button class="table-closer" v-on:click="show_details=false">
         <icon icon="close"></icon>
       </button>
       Workflow: <b>{{name}}</b>
     </div>
     <workflow idx=0 
               :methods="methods"
               :config="config"
               :steps="steps"
               :existing_workflows="[]"
               :inactive="true">
     </workflow>
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
  }
},

mounted: async function(){
},

props: ["name", "methods", "config", "steps"]
</javascript>

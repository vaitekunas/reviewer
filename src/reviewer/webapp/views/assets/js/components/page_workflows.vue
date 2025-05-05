<name>page-workflows</name>

<template>
  <div class="content-area">
    <div class="workflow-lists">
      <workflow-card 
          v-for="w in workflows" 
          :name="w.config.name"
          :methods="methods"
          :config="w.config"
          :steps="w.steps">
      </workflow-card>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    methods: [],
    workflows: []
  }
},

methods: {
},

mounted: async function(){
  this.workflows = await api_workflows();
  this.methods = await api_methods();
},

props: []
</javascript>

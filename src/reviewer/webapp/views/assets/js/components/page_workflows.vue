<name>page-workflows</name>

<template>
  <div class="content-area">
    <div v-if="workflows.length > 0" class="workflow-lists">
      <workflow-card 
          v-for="w in workflows" 
          :name="w.config.name"
          :methods="methods"
          :config="w.config"
          :steps="w.steps">
      </workflow-card>
    </div>
    <div v-else class="run-icon-container">
      <icon class="analysis-icon" icon="workflows"></icon>
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

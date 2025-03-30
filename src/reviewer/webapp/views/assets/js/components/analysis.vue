<name>analysis</name>

<template>
  <div class="analysis">

    <div class="analysis-workflows">
      <workflow v-for="w in workflows" 
                :config  = "w.config"
                :steps   = "w.steps"
                :methods = "methods"
                :existing_workflows = "existing_workflows"
                v-on:saved = "update_existing_workflows"
                v-on:changed="$emit('changed')"></workflow>
    </div>

    <add-button title="+ workflow" 
                :choices="existing_workflows"
                :allow_empty="true"
                :from_config="true"
                :group_choices="false"
                v-on:add="add_workflow($event)"
                v-on:add_empty="add_empty_workflow">
    </add-button>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    methods: [],
    existing_workflows: [],
    workflows: []
  }
},


methods: {

  get_empty_workflow: function(){
    return {config: {name:       "New Workflow",
                     sql_filter: ""},
            steps: []}
  },

  add_workflow: function(w){
    this.workflows.push(JSON.parse(JSON.stringify(w)));
  },

  add_empty_workflow: function(){
    this.workflows.push(this.get_empty_workflow());
  },

  get_schema: function(){
    var schema = {config: {},
                  workflows: []};

  },

  update_existing_workflows: async function(){
    this.existing_workflows = await api_workflows();
  },

},

mounted: async function(){
  this.methods            = await api_methods();
  this.existing_workflows = await api_workflows();
},

props: ["workflows"]
</javascript>

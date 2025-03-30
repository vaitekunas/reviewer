<name>workflow</name>

<template>
  <div class="workflow">
    <div class="workflow-steps">

      <workflow-config 
        :config   = "config"
        :steps    = "steps"
        :existing = "existing_workflows"
        v-on:saved="$emit('saved')">
      </workflow-config>

      <step v-for="s in steps" 
            :title="s.name" 
            :config="s.config" 
            :classname="method_types[s.name]"
            v-on:changed="$emit('changed')"
            icon="run"></step>

      <add-button title="+ step" 
                  :choices="methods"
                  :allow_empty="false"
                  :group_choices="true"
                  v-on:add="add_step($event)">
      </add-button>

    </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    method_types: {}
  }
},


methods: {
  update_method_types: function(){
    var that = this;
    this.method_types = {}

    Object.keys(this.methods).forEach(mt => {
      Object.keys(that.methods[mt]).forEach(method => {
        that.method_types[method] = mt;
      });
    });
  },

  add_step: function(step){
    this.steps.push(JSON.parse(JSON.stringify(step)));
  }
},

mounted: function(){
  this.update_method_types();
},

watch: {
  steps: function(new_val){
    this.$emit('changed');
  },

  methods: function(){
    this.update_method_types();
  }
},


props: ["methods", "existing_workflows", "config", "steps"]
</javascript>

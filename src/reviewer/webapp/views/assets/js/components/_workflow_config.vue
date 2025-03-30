<name>workflow-config</name>

<template>
  <div class="workflow-config">
    <input placeholder="Workflow name" v-model="config.name" />
    <input placeholder="Filter rule (optional)" v-model="config.sql_filter" />
    <button v-if="can_save" class="success" v-on:click="save">
      <span v-if="!exists">
        Save workflow
      </span>
      <span v-else>
        Modify existing workflow
      </span>
    </button>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state
  }
},

computed: {
  can_save: function(){
    return this.steps.length > 0 && this.config.name.trim().length > 0;
  },

  exists: function(){
    var name = this.config.name.trim().toLowerCase();
    return this.existing.filter(w => w.config.name.trim().toLowerCase() == name).length > 0;
  }

},

methods: {

  get_schema: function(){
    return {config: JSON.parse(JSON.stringify(this.config)),
            steps:  JSON.parse(JSON.stringify(this.steps))};
  },
  
  save: async function(){
    if(!this.exists){
      var result = await api_create_workflow(this.get_schema());
    }else{
      var result = await api_modify_workflow(this.config.name, this.get_schema());
    }

    this.$emit("saved");
  }
},

props: ["existing", "config", "steps"]
</javascript>

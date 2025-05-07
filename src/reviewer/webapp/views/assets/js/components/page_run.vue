<name>page-run</name>

<template>
  <div class="content-area">

    <div class="run-area">
      <div class="run-settings">
        <card title="Settings" icon="settings">
          <input placeholder="Title" v-model="title"/>
          <div class="run-saver">
            <button v-if="can_save" class="success" v-on:click="save">
              <span v-if="!analysis_exists">
                Save Analysis
              </span>
              <span v-else>
                Modify existing Analysis
              </span>
            </button>
          </div>
        </card>

        <card v-if="workflows == null" title="Analysis" icon="analysis">
          <div class="analysis-chooser">
              <div class="analysis-chooser-container" v-if="analyses.length > 0">
                Select existing analysis:
                <div class="analysis-chooser">
                  <select v-model="selected_analysis">
                    <option v-for="a in analyses" :value="a.config.name">{{a.config.name}}</option>
                  </select>
                  <button v-if="selected_analysis" class="success" v-on:click="use_selected_analysis">Use selected analysis</button>
                </div>

                <div class="separator-or">OR</div>
              </div>
              <button class="success" v-on:click="create">Create new analysis</button>
          </div>
        </card>

        <card title="Dataset" icon="datasets">
          <dataset-chooser 
            :dataset_name="dataset"
            v-on:dataset-choice="update_dataset($event)">
          </dataset-chooser>
        </card>

        <card title="Mapping" icon="mapping">
          <mapping :dataset_info="dataset_info"
                   :required_fields="required_fields"
                   :mapping="mapping">
          </mapping>
        </card>

        <div class="run-buttons">
          <button class="danger" v-on:click="reset">Reset</button>
          <button v-if="can_run" class="success" v-on:click="run">Run Analysis</button>
        </div>
      </div>

      <div class="run-workflow">
        <analysis v-if="workflows != null"
                  :workflows="workflows" 
                  v-on:being_dragged="being_dragged=$event"
                  v-on:changed="update_requirements"></analysis>

        <div v-else class="run-icon-container">
          <icon class="run-icon" icon="run"></icon>
        </div>
      </div>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state:             global_data.state,
    analysis_exists:   false,
    analyses:          [],
    selected_analysis: null,
    title:             "",
    dataset:           null,
    dataset_info:      null,
    required_fields:   {},
    workflows:         null,
    mapping:           {},
    being_dragged:     false
  }
},

computed: {
  can_save: function(){
    return this.title.trim() != "" && this.workflows != null && this.workflows.length > 0;
  },

  can_run: function(){
    return this.title.trim() != "" && this.dataset != null && this.workflows != null && this.workflows.length > 0;
  }
},

methods: {

  get_schema: function(){
    return {config: {name: this.title.trim()},
            workflows: this.workflows}
  },

  update_analysis_exists: function(){
    var name   = this.title.trim().toLowerCase();
    var exists = false;

    if(name != ""){
       exists = this.analyses.filter(a => a.config.name.toLowerCase() == name).length > 0;
    }

    this.analysis_exists = exists;
  },

  use_selected_analysis: function(){
    var schema     = JSON.parse(JSON.stringify(this.analyses.filter(a => a.config.name == this.selected_analysis)[0]));

    this.title     = schema.config.name;
    this.workflows = schema.workflows;

    this.mapping = {};
    this.required_fields = {};
  },

  reset: function(){
    this.title             = "";
    this.selected_analysis = null;
    this.dataset           = null;
    this.dataset_info      = {};
    this.workflows         = null;
    this.mapping           = {};
    this.required_fields   = {};
  },

  create: function(){
    this.workflows = [];
  },

  run: async function(){
    var schema = {dataset_name: this.dataset,
                  mapping: JSON.parse(JSON.stringify(this.mapping)),
                  analysis: JSON.parse(JSON.stringify(this.get_schema()))};

    this.state.running = true;

    var result = await api_analyze(this.title, schema) || {};
    console.log("result received");

    if(Object.keys(result).indexOf("detail") >= 0){
      this.state.error_messages.push(result.detail);
    }

    this.state.running = false;
  },

  save: async function(){
    var schema = JSON.parse(JSON.stringify(this.get_schema()));

    if(!this.analysis_exists){
      result = await api_create_analysis(schema);
    }else{
      console.log("modifying");
      result = await api_modify_analysis(this.title, schema);
    }

    this.analyses = await api_analysis();
    this.update_analysis_exists();

  },

  update_dataset: async function(dataset_name){
    this.dataset      = dataset_name;
    this.dataset_info = await api_get_dataset(dataset_name);
    this.mapping      = {};
  },

  update_requirements: async function(){
    if(this.being_dragged){
      return;
    }

    var that = this;

    var schema          = this.get_schema();
    var requirements    = await api_requirements(schema);

    if(Object.keys(requirements).indexOf("detail") >= 0){
      this.state.error_messages.push(requirements.detail);
      return;
    }

    var required        = requirements.fields.required;
    var required_fields = JSON.parse(JSON.stringify(this.required_fields));
    var mapping         = JSON.parse(JSON.stringify(this.mapping));

    // Remove unnecessary fields
    Object.keys(required_fields).forEach(field => {
      if(Object.keys(required).indexOf(field) < 0){
        delete required_fields[field];
        delete mapping[field];
      }
    });

    // Update requirements
    Object.keys(required).forEach(field => {
        required_fields[field] = required[field];
        if(Object.keys(mapping).indexOf(field) < 0){
          mapping[field] = null;
        }
    });

    // Overwrite
    this.required_fields = required_fields;
    this.mapping = mapping;
  }
},

watch: {

  title: async function(new_val){
    this.update_analysis_exists();
  },

  workflows: async function(new_val){
    if(new_val == null){
      return;
    }

    await this.update_requirements();
  },

  '$route.query.name': function(val){
    if(val !== undefined && val != this.selected_analysis){
      this.selected_analysis = val;
      this.use_selected_analysis();
    }
  }

},

mounted: async function(){
  var that = this;

  this.analyses = await api_analysis();

  socket.on("analysis", async function(data) {
    that.analysis = await api_analysis();
  });

},

props: []
</javascript>

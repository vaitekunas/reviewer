<name>dataset-chooser</name>

<template>
  <div class="dataset-chooser">

    <div v-if="!show_upload">
      <span>Select existing dataset:</span>

      <select v-if="selected_file == null && datasets.length > 0"
              v-model="dataset_name"
              v-on:change="$emit('dataset-choice', dataset_name)">
        <option v-for="d in datasets" 
                :value="d.value">
          {{d.name}}
        </option>
      </select>
      <div v-if="dataset_name">
        Max rows: <input v-model="max_rows" v-on:change="$emit('max-row-choice', max_rows)"/>
      </div>

    </div>
    
    <div v-if="datasets.length > 0 && !show_upload" class="separator-or"> OR </div>

    <button v-if="!show_upload" 
            class="success" 
            v-on:click="dataset_name = null; show_upload = true">
      Upload a new dataset:
    </button>
    
    <div class="dataset-chooser" v-if="show_upload">
      <span v-if="!selected_file">Select file:</span>

      <label v-if="!selected_file" class="dataset-uploader" for="dataset-input">
        <icon icon="upload"></icon>
      </label>
      <input type="file" accept=".csv, .txt" id="dataset-input" v-on:change="select_file"/>

      <button v-if="datasets.length > 0 && !selected_file" class="danger" v-on:click="reset_file">Cancel</button>

      <div v-if="selected_file">
        <input ref="dataset_name" v-model="dataset_name" placeholder="Dataset name"/>
        <button class="danger"  v-on:click="reset_file">Reset</button>
        <button class="success" v-on:click="upload_file">Create new dataset</button>
      </div>

    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    show_upload: false,
    selected_file: null,
    
    datasets: []
  }
},

methods: {

  refresh_data: async function(){
    var datasets = await api_datasets();

    for(d of datasets){
      this.datasets.push({name:  d.name + " (rows: " + d.n_rows +", columns: " + d.n_columns +")",
                          value: d.name});
    }
  },

  select_file: function(){
    var that = this;
    var dinput = document.getElementById("dataset-input");

    if(dinput == null){
      this.selected_file = null;
    }

    this.selected_file = dinput.value;

    this.$nextTick(() => {
      that.$refs.dataset_name.focus();
    });
  },

  reset_file: function(){
    var dinput = document.getElementById("dataset-input");
    dinput.value = null;
    this.selected_file = null;

    this.show_upload = this.datasets.length == 0;
  },

  upload_file: async function(){
    var that = this;
    var result = await api_create_dataset("dataset-input", this.dataset_name);

    if(result != null){
      this.reset_file();
      await this.refresh_data();

      this.$nextTick(() => {
        that.dataset_name = result.name;
        that.$emit('dataset-choice', result.name);
      });
    }
  }

},

mounted: async function(){
  await this.refresh_data();
  if(this.datasets.length == 0){
    this.show_upload = true;
  }
},

props: ["dataset_name", "max_rows"]
</javascript>

<name>dataset</name>

<template>
  <div class="dataset-wrapper">

    <div v-if="!show_head" class="dataset" v-on:click="show_data">
      <div class="dashboard-card-background">
        <icon icon="datasets"></icon>
      </div>

      <div class="dashboard-card-title">
        {{name}}
        <br>
        ({{n_rows}} x {{n_columns}})
      </div>

      <div class="dataset-stats">
        Columns: 
        <ul>
          <li v-for="c in columns">{{c}}</li>
        </ul>
      </div>
    </div>
    
    <div v-else>
      <dataset-table :columns="Object.keys(dataset_head)" 
                     :table_data="dataset_head"
                     v-on:close="show_head=false">
      </dataset-table>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    dataset_head: null,
    show_head: false
  }
},

methods: {
  show_data: async function(){
    if(this.dataset_head == null){
      var data = await api_dataset(this.name);
      this.dataset_head = data.data;
    }
    this.show_head = true;
  }
},

mounted: async function(){
},

props: ["name", "n_rows", "n_columns", "columns"]
</javascript>

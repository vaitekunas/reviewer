<name>page-datasets</name>

<template>
  <div class="content-area">
    <div v-if="datasets.length > 0" class="dataset-lists">
      <dataset 
        v-for="d in datasets" 
        :name="d.name"
        :n_rows="d.n_rows"
        :n_columns="d.n_columns"
        :columns="d.columns">
      </dataset>
    </div>
    <div v-else class="run-icon-container">
      <icon class="analysis-icon" icon="datasets"></icon>
    </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    datasets: []
  }
},

methods: {
},

mounted: async function(){
  this.datasets = await api_datasets();

  var that = this;
  socket.on("dataset", async function(data) {
    that.datasets = await api_datasets();
  });
},

props: []
</javascript>

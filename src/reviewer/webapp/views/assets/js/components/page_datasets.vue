<name>page-datasets</name>

<template>
  <div class="content-area">
    Datasets
    <div v-for="d in datasets">
      {{d.name}}
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
},

props: []
</javascript>

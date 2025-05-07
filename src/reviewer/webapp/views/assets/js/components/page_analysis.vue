<name>page-analysis</name>

<template>
  <div class="content-area">
    <div v-if="analysis.length > 0" class="workflow-lists">
      <analysis-card 
          v-for="a in analysis" 
          :name="a.config.name"
          :workflows="a.workflows">
      </analysis-card>
    </div>
    <div v-else class="run-icon-container">
      <icon class="analysis-icon" icon="analysis"></icon>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    methods: [],
    analysis: [],

  }
},

methods: {
},

mounted: async function(){
  this.analysis = await api_analysis();
  this.methods = await api_methods();

  var that = this;
  socket.on("analysis", async function(data) {
    that.analysis = await api_analysis();
    that.methods  = await api_methods();
  });

},


props: []
</javascript>

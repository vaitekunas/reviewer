<name>page-results</name>

<template>
  <div class="content-area">
    <div v-if="runs.length > 0" class="workflow-lists">
      <result-card
          v-for="r in runs" 
          :run_id="r.run_id"
          :name="r.name"
          :utc_datetime="r.created_at_utc"
          :result_count="r.result_count">
      </result-card>
    </div>
    <div v-else class="run-icon-container">
      <icon class="analysis-icon" icon="results"></icon>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    runs: []
  }
},

methods: {
},

mounted: async function(){
  this.runs = await api_runs();

  var that = this;
  socket.on("result", async function(data) {
    that.runs = await api_runs();
  });
},

props: []
</javascript>

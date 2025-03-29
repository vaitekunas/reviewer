<name>page-dashboard</name>

<template>
  <div class="content-area">

    <div class="dashboard-content">

      <div v-if="!logged_in" class="dashboard-welcome">
        <h1>Welcome</h1>
        This is a customer review analytics 
      </div>

        <div class="dashboard-col">

          <div class="dashboard-row">
            <dashboard-card title="Datasets"  :count="count_datasets"  classname="datasets"  url="/datasets"  :icon="state.icons.datasets"  :logged_in="logged_in"></dashboard-card>
            <dashboard-card title="Methods"   :count="count_methods"   classname="methods"   url="/methods"   :icon="state.icons.methods"   :logged_in="logged_in"></dashboard-card>
            <dashboard-card title="Workflows" :count="count_workflows" classname="workflows" url="/workflows" :icon="state.icons.workflows" :logged_in="logged_in"></dashboard-card>
          </div>

          <div class="dashboard-row">
            <dashboard-card title="Analysis" :count="count_analysis" classname="analysis" url="/analysis" :icon="state.icons.analysis" :logged_in="logged_in"></dashboard-card>
            <dashboard-card title="Runs"     :count="count_runs"     classname="runs"     url="/run"      :icon="state.icons.run"      :logged_in="logged_in"></dashboard-card>
            <dashboard-card title="Results"  :count="count_results"  classname="results"  url="/results"  :icon="state.icons.results"  :logged_in="logged_in"></dashboard-card>
          </div>

        </div>

    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,

    count_datasets : 0,
    count_methods  : 0,
    count_workflows: 0,
    count_analysis : 0,
    count_runs     : 0,
    count_results  : 0,
  }
},

methods: {
},

mounted: async function(){
  result = await api_statistics();

  this.count_datasets  = result.datasets;
  this.count_methods   = result.methods;
  this.count_workflows = result.workflows;
  this.count_analysis  = result.analysis;
  this.count_runs      = result.runs;
  this.count_results   = result.results;

},

props: ["logged_in"]
</javascript>

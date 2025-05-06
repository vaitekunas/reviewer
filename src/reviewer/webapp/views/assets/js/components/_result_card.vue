<name>result-card</name>

<template>
  <div class="dataset-wrapper" :class="{expanded: show_details}">

    <div v-if="!show_details" class="dataset" v-on:click="toggle_show_details">
      <div class="dashboard-card-background">
        <icon icon="results"></icon>
      </div>

      <div class="dashboard-card-title">
        {{name}}
      </div>

      <div class="workflow-card-count">
        Results: {{result_count}}
      </div>

      <div v-if="utc_datetime" class="workflow-card-date">
        {{get_local_date(utc_datetime)}}
      </div>
      <div v-else class="workflow-card-date">&nbsp;</div>

    </div>
    
    <div v-else class="workflow-details">
      <div class="workflow-details-title">
        <button class="table-closer" v-on:click="show_details=false">
          <icon icon="close"></icon>
        </button>
        Results of <b>{{name}}</b> <span v-if="utc_datetime">({{get_local_date(utc_datetime)}})</span>:
      </div>
      <div class="result-entry">
        <result v-for="r in results" :run_id="run_id" :result="r"></result>
      </div>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    show_details: false,
    results: []
  }
},

methods: {
  toggle_show_details: async function(){
    this.get_results();
    this.show_details = !this.show_details;
  },

  get_results: async function(){
    if(this.run_id == undefined || this.results.length > 0){
      return;
    }

    var results = await api_results(this.run_id); 
    this.results = Object.values(results.results).flatMap(Object.values).flatMap(x=>x);
  },

  get_local_date: function(utc_datetime){
    const pad = (num) => num.toString().padStart(2, '0');

    var utc_datetime = utc_datetime.replace(/\.\d+/, '');
    var date = new Date(utc_datetime + 'Z');
    var year = date.getFullYear();
    var month = pad(date.getMonth() + 1); // Months are 0-based
    var day = pad(date.getDate());
    var hours = pad(date.getHours());
    var minutes = pad(date.getMinutes());
    var seconds = pad(date.getSeconds());

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }

},

mounted: async function(){
},

props: ["run_id", "name", "result_count", "utc_datetime"]
</javascript>

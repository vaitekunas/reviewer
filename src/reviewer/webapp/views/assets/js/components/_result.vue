<name>result</name>

<template>
  <div class="result-wrapper" v-on:click="toggle_show_result">
      <div class="result-link" :class="{open: show_result}">
        <icon class="result-icon" :icon="icon"></icon>
        <div>{{result.result_name}}</div>
      </div>
      <div v-if="show_result">
        <img v-if="result_object.result_type == 'figure' "class="result-figure"  :src="result_object.value"/>
        <dataset-table v-else 
                     :columns="Object.keys(result_object.value)" 
                     :table_data="result_object.value"
                     v-on:close="show_results=false">
      </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    show_result: false,
    result_object: null
  }
},

computed: {
  icon: function(){
    if(this.result == undefined){
      return 'n/a';
    }

    return this.result.result_type == 'figure' ? 'image' : 'table';
  }
},

methods: {
  toggle_show_result: async function(){
    if(this.result_object == null){
      this.result_object = await api_result(this.run_id, this.result.result_name);
    }
    this.show_result = !this.show_result;
  }

},


props: ["run_id", "result"]
</javascript>

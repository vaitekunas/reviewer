<name>side-bar</name>

<template>
  <div class="sidebar" :class="{expanded: expanded, hidden: !logged_in}">

    <div class="sidebar-tabs">
      <side-button :icon="state.icons.methods"   text="Methods"   url="/methods"   :expanded="expanded" v-on:clicked="$emit('select_page', 'Methods')"></side-button>
      <side-button :icon="state.icons.datasets"  text="Datasets"  url="/datasets"  :expanded="expanded" v-on:clicked="$emit('select_page', 'Datasets')"></side-button>
      <side-button :icon="state.icons.workflows" text="Workflows" url="/workflows" :expanded="expanded" v-on:clicked="$emit('select_page', 'Workflows')"></side-button>
      <side-button :icon="state.icons.analysis"  text="Analysis"  url="/analysis"  :expanded="expanded" v-on:clicked="$emit('select_page', 'Analysis')"></side-button>
      <side-button :icon="state.icons.results"   text="Results "  url="/results"   :expanded="expanded" v-on:clicked="$emit('select_page', 'Results')"></side-button>
      <side-button :icon="state.icons.run"       text="Run"       url="/run"       :expanded="expanded" v-on:clicked="$emit('select_page', 'Run')"></side-button>
      <side-button :icon="state.icons.dashboard" text="Dashboard" url="/"          :expanded="expanded" v-on:clicked="$emit('select_page', 'Review Analytics')"></side-button>
    </div>
    <div class="sidebar-tabs">
      <side-button :icon="state.icons.api" text="REST API"  url="" v-on:clicked="window.open('/docs','_blank')" :expanded="expanded"></side-button>
      <side-button :icon="expander_icon"  text=""          url="" v-on:clicked="expanded = !expanded" classname="expander"></side-button>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    expanded: false
  }
},

computed: {
  expander_icon: function(){
    if(this.expanded){
      return this.state.icons.expander_in;
      }else{
        return this.state.icons.expander_out;
      }
  }

},

methods: {
},

props: ["logged_in"]
</javascript>

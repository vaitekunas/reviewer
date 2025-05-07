<name>side-bar</name>

<template>
  <div class="sidebar" :class="{expanded: expanded, hidden: !logged_in}">

    <div class="sidebar-tabs">
      <side-button :icon="state.icons.dashboard" text="Dashboard" url="/"          :expanded="expanded" v-on:clicked="$emit('select_page', {page_title: 'Review Analytics', page_icon: state.icons.dashboard})"></side-button>
      <side-button :icon="state.icons.methods"   text="Methods"   url="/methods"   :expanded="expanded" v-on:clicked="$emit('select_page', {page_title: 'Methods', page_icon: state.icons.methods})"></side-button>
      <side-button :icon="state.icons.datasets"  text="Datasets"  url="/datasets"  :expanded="expanded" v-on:clicked="$emit('select_page', {page_title: 'Datasets', page_icon: state.icons.datasets})"></side-button>
      <side-button :icon="state.icons.workflows" text="Workflows" url="/workflows" :expanded="expanded" v-on:clicked="$emit('select_page', {page_title: 'Workflows', page_icon: state.icons.workflows})"></side-button>
      <side-button :icon="state.icons.analysis"  text="Analyses"  url="/analysis"  :expanded="expanded" v-on:clicked="$emit('select_page', {page_title: 'Analyses', page_icon: state.icons.analysis})"></side-button>
      <side-button :icon="state.icons.results"   text="Results "  url="/results"   :expanded="expanded" v-on:clicked="$emit('select_page', {page_title: 'Results', page_icon: state.icons.results})"></side-button>
      <side-button :icon="state.icons.run"       text="Analyze"   url="/run"       :expanded="expanded" v-on:clicked="$emit('select_page', {page_title: 'Analyze', page_icon: state.icons.run})"></side-button>
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

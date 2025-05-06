<name>page-methods</name>

<template>
  <div class="content-area">
    <div class="method-lists">
      <div class="method-list" v-for="(group_methods, group) in methods">
        <div class="method-title">
          {{group}}
        </div>
        <div class="workflow-steps wrappable">
          <div v-for="(method_details, method) in group_methods" class="step-wrapper">
            <div class="step-description">
              {{method_details.description}}
            </div>
            <step idx=0 
                  :title="method_details.name" 
                  :config="method_details.config" 
                  :classname="group"
                  :icon="group+'-method'"
                  alt="text"
                  inactive="true">
            </step>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    methods: {}
  }
},

methods: {

},

mounted: async function(){
  this.methods = await api_methods();
},

props: []
</javascript>

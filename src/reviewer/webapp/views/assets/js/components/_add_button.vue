<name>add-button</name>

<template>
  <div class="step add-button" v-on:click="active = true">
    
    <div v-if="!active">
      {{title}}
    </div>
    <div v-else>

      <select v-if="has_choices && !from_config && !group_choices" v-model="choice"> 
        <option v-for="c in choices" :value="c">{{c}}</option>
      </select>

      <select v-if="has_choices && from_config && !group_choices" v-model="choice"> 
        <option v-for="c in choices" :value="c">{{c.config.name}}</option>
      </select>
      
      <select v-if="has_choices && !from_config && group_choices" v-model="choice"> 
        <optgroup v-for="(g_choices, group) in choices" :label="group">
          <option v-for="(c, cname) in g_choices" :value="c">{{cname}}</option>
        </optgroup>
      </select>
      
      <div>
        <button class="danger" v-on:click="reset">Cancel</button>
        <button v-if="choice" class="success" v-on:click="choose">Add</button>
        <button v-if="allow_empty" class="success" v-on:click="choose_empty">Add empty</button>
      </div>

    </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    activated: false,
    active: false,
    choice: null
  }
},

computed: {
  has_choices: function(){
    return this.choices != null && Object.keys(this.choices).length > 0;
  }
},

methods: {

  reset: function(event){
    event.stopPropagation();
    this.choice = null;
    this.active = false;
    this.activated = false;
  },

  choose: function(event){
    event.stopPropagation();
    this.$emit("add", this.choice);
    this.reset(event);
  },

  choose_empty: function(event){
    event.stopPropagation();
    this.$emit("add_empty");
    this.reset(event);
  }

},

props: ["title", "allow_empty", "from_config", "group_choices", "choices", "callback_id"]
</javascript>

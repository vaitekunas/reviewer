<name>step</name>

<template>
  <div class="step" 
    :class="classname" 
    draggable="true"
    @dragstart="emit_start_drag"
    @drag="emit_drag"
    @dragend="emit_end_drag">

    <div class="closer" v-on:click="$emit('remove')">x</div>
    <div v-if="!configure" v-on:click="configure = true">
      <icon class="step-icon" :icon="icon" v-if="icon"></icon>
      {{title}}
    </div>
    <div class="step-config" v-else>
      <button v-on:click="configure=false">close</button>
      <table>
        <tr class="step-config-head">
          <th>Option</th>
          <th>Value</th>
        </tr>
        <tr v-for="k in Object.keys(config)">
          <td>
            <div class="step-config-key">
            {{k}}
            </div>
          </td>
          <td>
            <input class="step-config-input" v-on:change="$emit('changed')" v-model="config[k]"/>
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    configure: false
  }
},


methods: {

  emit_start_drag: function(event){
    this.$emit("start_drag", event);
  },

  emit_drag: function(event){
    this.$emit("drag", event);
  },

  emit_end_drag: function(event){
    this.$emit("end_drag", event);
  }

},

props: ["idx", "title", "config", "icon", "classname"]
</javascript>

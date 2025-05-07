<name>step</name>

<template>
  <div class="step" 
    :class="classes" 
    v-on:click="configure = true"
    :draggable="!inactive"
    @dragstart="emit_start_drag"
    @drag="emit_drag"
    @dragend="emit_end_drag">

    <div v-if="!inactive" class="closer" v-on:click="$emit('remove')">x</div>

    <div v-if="!configure" >
      <icon class="step-icon" :icon="icon" v-if="icon"></icon>
      {{title}}
    </div>

    <div class="step-config" v-else>
      <button class="close-icon" v-on:click="hide_config">
        <icon icon="close"></icon>
      </button>
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
            <span v-if="is_short(config[k])">
            <input class="step-config-input" 
                   :readonly="inactive"
                   v-on:change="$emit('changed')" 
                   v-model="config[k]"/>
            </span>
            <span v-else>
              <textarea class="step-config-input" 
                     :readonly="inactive"
                     v-on:change="$emit('changed')" 
                     v-model="config[k]"></textarea>
            </span>
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

computed: {
  classes: function(){
    var classes = {};
    classes[this.classname] = true;
    classes["running"] = this.state.running && this.running;

    return classes
  }
},

methods: {

  is_short: function(val){
    return val == null || String(val).trim().length < 30;
  },

  hide_config: function(event){
    event.stopPropagation();
    this.configure = false;
  },

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

props: ["idx", "title", "config", "icon", "classname", "inactive", "running"]
</javascript>

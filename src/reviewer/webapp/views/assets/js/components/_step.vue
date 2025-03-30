<name>step</name>

<template>
  <div class="step" :class="classname">
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
},

props: ["title", "config", "icon", "classname"]
</javascript>

<name>mapping</name>

<template>
  <div class="mapping">
    <div v-if="!dataset_info" class="mapping-warning">
      Please select a dataset
    </div>
    <div v-else-if="Object.keys(required_fields).length == 0">
      No mapping required.
    </div>
    <div v-else>
      <table>
        <tr class="step-config-head">
          <th>Required field</th>
          <th>Mapped field</th>
        </tr>
        <tr v-for="(field_info, field) in required_fields">
          <td class="mapping-requirement" :class="{missing: !mapping[field]}">
            {{field}}
          </td>
          <td class="mapping-requirement-input">
            <select v-if="!field_info.prefix" v-model="mapping[field]">
              <option v-for="col in dataset_info.columns">
                {{col}}
              </option>
            </select>
            <input v-else :placeholder="field" v-model="mapping[field]">
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
  }
},


methods: {
},

props: ["dataset_info", "required_fields", "mapping"]
</javascript>

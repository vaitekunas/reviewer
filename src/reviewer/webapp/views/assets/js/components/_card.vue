<name>card</name>

<template>
  <div class="card" :class="classname">

    <div class="card-title">
      <icon class="card-icon" :icon="icon"></icon>
      {{title}}
    </div>
    <div>
      <slot></slot>
    </div>

  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state
  }
},

methods: {
},

props: ["title", "classname", "icon"]
</javascript>

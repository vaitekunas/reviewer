<name>card</name>

<template>
  <div class="card" >

    <div class="card-title">
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

props: ["title", "class"]
</javascript>

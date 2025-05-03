<name>errors</name>

<template>
  <div class="errors">
    <div class="error" v-for="msg in messages">
      {{msg}}
    </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    last_total: -1
  }
},


methods: {

},

watch: {
  messages: function(){
    var that = this;
    var total = this.messages.length;

    if(total == 0 || total < this.last_total){
      return;
    }

    this.last_total += 1;

    setTimeout(() => {
      if(that.messages.length > 0){
        that.messages.pop();
        that.last_total -= 1;
      }else{
        that.last_total = -1;
      }
    }, 5000);

  }
},

props: ["messages"]
</javascript>

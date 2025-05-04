<name>workflow</name>

<template>
  <div class="workflow" :id="'workflow_' + idx" 
    draggable="true"
    @dragstart="emit_start_drag"
    @drag="emit_drag"
    @dragend="emit_end_drag">

    <div class="dragger" v-on:click="$emit('remove')">
      <icon icon="drag"></icon>
    </div>

    <div class="closer" v-on:click="$emit('remove')">x</div>

    <div class="duplicator" v-on:click="$emit('duplicate')">
      <icon class="step-icon" icon="duplicate">
    </div>

    <div class="workflow-steps">

      <workflow-config 
        :config   = "config"
        :steps    = "steps"
        :existing = "existing_workflows"
        v-on:saved="$emit('saved')">
      </workflow-config>

      <step v-for="(s,i) in steps" 
            :idx="i"
            :title="s.name" 
            :config="s.config" 
            :classname="method_types[s.name]"

            v-on:start_drag="start_drag(i, $event)"
            v-on:drag="drag($event)"
            v-on:end_drag="end_drag(i, $event)"

            v-on:changed="changed"
            v-on:remove="remove_step(i)"

            :icon="method_types[s.name]+'-method'"></step>

      <add-button title="+ step" 
                  :choices="methods"
                  :allow_empty="false"
                  :group_choices="true"
                  v-on:add="add_step($event)">
      </add-button>

    </div>
  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,

    being_dragged: false,
    drag_orig_x: null,
    drag_offset: null,
    drag_idx: null,

    method_types: {}
  }
},


methods: {

  changed: function(){
    if(!this.being_dragged){
      this.$emit('changed');
    }
  },

  update_method_types: function(){
    var that = this;
    this.method_types = {}

    Object.keys(this.methods).forEach(mt => {
      Object.keys(that.methods[mt]).forEach(method => {
        that.method_types[method] = mt;
      });
    });
  },

  add_step: function(step){
    this.steps.push(JSON.parse(JSON.stringify(step)));
  },

  remove_step: function(idx){
    this.steps.splice(idx, 1);
  },

  reset_drag: function(){
    this.drag_idx      = null;
    this.drag_orig_x   = null;
    this.drag_offset   = null;
    this.being_dragged = false;
  },

  start_drag: function(idx, event){
    var dom_steps = document.getElementById("workflow_"+this.idx).getElementsByClassName("step");

    this.drag_idx      = idx;
    this.drag_orig_x   = dom_steps[idx].getBoundingClientRect().x;
    this.drag_offset   = event.x - this.drag_orig_x;
    this.being_dragged = true;
  },

  drag: function(event){
    if(event.x == 0 && event.y == 0){
      return;
    }

    var moved = Math.abs(event.x - this.drag_orig_x - this.drag_offset);

    if(moved < 25){
      return;
    }

    var dom_steps = document.getElementById("workflow_"+this.idx).getElementsByClassName("step");
    var max_i = dom_steps.length-1;

    var src_step       = dom_steps[this.drag_idx].getBoundingClientRect();
    var src_step_start = event.x - this.drag_offset;

    [this.drag_idx-1, this.drag_idx+1].forEach(i => {
        if(i < 0 || i > max_i){
          return;
        }

        var dst_step        = dom_steps[i].getBoundingClientRect();
        var dst_step_start  = dst_step.x;
        var dst_step_end    = dst_step.x + dst_step.width;
        var dst_step_middle = dst_step.x + dst_step.width/2;

        if(i+1 == this.drag_idx && src_step_start < dst_step_middle){
          this.swap_steps(this.drag_idx, i, event);
          return;
        }else if(i-1 == this.drag_idx && src_step_start > dst_step_middle){
          this.swap_steps(this.drag_idx, i, event);
          return;
        }
    })

  },

  swap_steps: function(src, dst, event){

    if(!this.being_dragged){
      return;
    }

    var dom_steps = document.getElementById("workflow_"+this.idx).getElementsByClassName("step");

    var src_step = JSON.parse(JSON.stringify(this.steps[src]));
    var dst_step = JSON.parse(JSON.stringify(this.steps[dst]));

    this.drag_idx      = dst;
    this.drag_orig_x   = dom_steps[dst].getBoundingClientRect().x;

    this.steps.splice(dst, 1, src_step);
    this.steps.splice(src, 1, dst_step);

  },

  end_drag: function(idx, event){
    this.reset_drag();
    this.$emit('changed');
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

mounted: function(){
  this.update_method_types();
},

watch: {
  steps: function(new_val){
    if(!this.being_dragged){
      this.$emit('changed');
    }
  },

  methods: function(){
    this.update_method_types();
  }
},


props: ["idx", "methods", "existing_workflows", "config", "steps"]
</javascript>

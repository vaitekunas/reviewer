<name>analysis</name>

<template>
  <div class="analysis">

    <div class="analysis-workflows">
      <workflow v-for="(w,i) in workflows" 
                :idx     = "i"
                :config  = "w.config"
                :steps   = "w.steps"
                :methods = "methods"
                :existing_workflows = "existing_workflows"
                
                v-on:start_drag="start_drag(i, $event)"
                v-on:drag="drag($event)"
                v-on:end_drag="end_drag(i, $event)"

                v-on:remove="remove_workflow(i)"
                v-on:duplicate="duplicate_workflow(i)"
                v-on:saved = "update_existing_workflows"
                v-on:changed="$emit('changed')"></workflow>
    </div>

    <add-button title="+ workflow" 
                :choices="existing_workflows"
                :allow_empty="true"
                :from_config="true"
                :group_choices="false"
                v-on:add="add_workflow($event)"
                v-on:add_empty="add_empty_workflow">
    </add-button>


  </div>
</template>

<javascript>

data: function(){
  return {
    state: global_data.state,
    methods: [],
    existing_workflows: [],
    workflows: [],

    being_dragged: false,
    drag_orig_y: null,
    drag_offset: null,
    drag_idx: null,
  }
},


methods: {

  get_empty_workflow: function(){
    return {config: {name:       "New Workflow",
                     sql_filter: ""},
            steps: []}
  },

  add_workflow: function(w){
    this.workflows.push(JSON.parse(JSON.stringify(w)));
  },

  add_empty_workflow: function(){
    this.workflows.push(this.get_empty_workflow());
  },

  get_schema: function(){
    var schema = {config: {},
                  workflows: []};

  },

  duplicate_workflow: function(idx){
    var workflow = JSON.parse(JSON.stringify(this.workflows[idx]));
    this.workflows.splice(idx, 0, workflow);
    this.$emit("changed");
  },

  remove_workflow: function(idx){
    this.workflows.splice(idx,1);
    this.$emit("changed");
  },

  update_existing_workflows: async function(){
    this.existing_workflows = await api_workflows();
  },

  reset_drag: function(){
    this.drag_idx      = null;
    this.drag_orig_y   = null;
    this.drag_offset   = null;
    this.being_dragged = false;
  },

  start_drag: function(idx, event){
    var dom_workflows = document.getElementsByClassName("workflow");

    this.drag_idx      = idx;
    this.drag_orig_y   = dom_workflows[idx].getBoundingClientRect().y;
    this.drag_offset   = event.y - this.drag_orig_y;
    this.being_dragged = true;
    this.$emit('being_dragged', this.being_dragged);
  },

  drag: function(event){
    if(event.x == 0 && event.y == 0){
      return;
    }

    var moved = Math.abs(event.y - this.drag_orig_y - this.drag_offset);

    if(moved < 25){
      return;
    }

    var dom_workflows = document.getElementsByClassName("workflow");
    var max_i = dom_workflows.length-1;

    var src_workflow       = dom_workflows[this.drag_idx].getBoundingClientRect();
    var src_workflow_start = event.y - this.drag_offset;

    [this.drag_idx-1, this.drag_idx+1].forEach(i => {
        if(i < 0 || i > max_i){
          return;
        }

        var dst_workflow        = dom_workflows[i].getBoundingClientRect();
        var dst_workflow_start  = dst_workflow.y;
        var dst_workflow_end    = dst_workflow.y + dst_workflow.height;
        var dst_workflow_middle = dst_workflow.y + dst_workflow.height/2;

        if(i+1 == this.drag_idx && src_workflow_start < dst_workflow_middle){
          this.swap_workflows(this.drag_idx, i, event);
          return;
        }else if(i-1 == this.drag_idx && src_workflow_start > dst_workflow_middle){
          this.swap_workflows(this.drag_idx, i, event);
          return;
        }
    })

  },

  swap_workflows: function(src, dst, event){

    if(!this.being_dragged){
      return;
    }

    var dom_workflows = document.getElementsByClassName("workflow");

    var src_workflow = JSON.parse(JSON.stringify(this.workflows[src]));
    var dst_workflow = JSON.parse(JSON.stringify(this.workflows[dst]));

    this.drag_idx      = dst;
    this.drag_orig_y   = dom_workflows[dst].getBoundingClientRect().y;

    this.workflows.splice(dst, 1, src_workflow);
    this.workflows.splice(src, 1, dst_workflow);

  },

  end_drag: function(idx, event){
    this.reset_drag();
    this.$emit('being_dragged', this.being_dragged);
    this.$emit('changed');
  }

},

mounted: async function(){
  this.methods            = await api_methods();
  this.existing_workflows = await api_workflows();
},

props: ["workflows"]
</javascript>

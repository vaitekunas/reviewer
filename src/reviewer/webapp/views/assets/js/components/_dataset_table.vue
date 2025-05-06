<name>dataset-table</name>                                             
                                                                                  
<template>                                                                      
  <div>                                                    
                                                                                
    <table class="stats-table table-desc" :class="{wrappable: wrappable}">                                      
                                                                                
      <thead>                                                                   
        <tr>                                                                    
          <th v-for="(c, i) in columns" class="table-desc-value">
            <div v-if="i == 0" class="stats-table-fcol">
              <button class="table-closer" v-on:click="$emit('close')">
                <icon icon="close"></icon>
              </button>
              <span>
                {{c}}
              </span>
            </div>
            <div v-else>
            {{c}}
            </div>
          </th>                               
        </tr>                                                                   
      </thead>                                                                  
                                                                                
      <tbody>                                                                   
        <tr v-for="idx in table_data[columns[0]].length">
          <td v-for="c in columns">{{table_data[c][idx-1]}}</td>
        </tr>                                                                   
      </tbody>                                   
    </table>                                                                    
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
                                                                                
watch: {                                                                        
                                                                                
},                                                                              
                                                                                
props: ["columns", "table_data", "wrappable"]                                      
</javascript>                   

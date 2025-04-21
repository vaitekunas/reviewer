<name>avatar</name>

<template>
  <div class="avatar-container">
    <div v-if="!is_logged_in" v-on:keydown.enter="log_in" class="avatar">
      <input class="in-username" placeholder = "username" v-model="username"/>
      <input class="in-password" placeholder = "password" type="password" v-model="password" ref="password"/>
      <div class="session_buttons">
        <button v-on:click="log_in">Login</button>
        <div>
          or
        </div>
        <button v-on:click="register" class="alternative">Sign Up</button>
      </div>
    </div>
    <div v-else class="avatar">
      <div class="avatar-greet">
        Hello, <span class="username">{{username}}</span>
      </div>
      <button v-on:click="log_out" class="danger">👋 Logout</button>
    </div>
    <span v-if="login_error" class="error-msg">{{login_error}}</span>
    <span v-else class="error-msg"></span>
  </div>
</template>

<javascript>

data: function(){
  return {
    username: "",
    password: "",
    is_logged_in: false,
    login_error: ""
  }
},

computed: {

  sess_token: function(){
    
    var sess_token_dto = localStorage.getItem("sess_token");
    var sess_token = {username: "stranger", expires_at: 0};

    if(sess_token_dto == null) {
      return sess_token;
    }

    try {
      sess_token_dto = JSON.parse(sess_token_dto);
    }catch(error){
      console.log(error);
      return sess_token;
    }

    if(Object.keys(sess_token_dto).indexOf("username") < 0){
      return sess_token;
    }

    return sess_token_dto;
  }

},

methods: {

  show_error: function(message) {
      this.login_error  = message;

      var that = this;
      setTimeout(() => {
        that.login_error = "";
      }, 2000);
  },

  register: async function(){
    var user = await api_register(this.username, this.password);

    if(user == null || Object.keys(user).indexOf("username") < 0){
      this.show_error("User could not be created");
      return;
    }

    this.log_in();
  },

  log_in: async function(){
    var sess_token = await api_login(this.username, this.password);

    if(sess_token == null || Object.keys(sess_token).indexOf("username") < 0){
      this.show_error("Login failed");
      return;
    }


    if(Object.keys(sess_token).indexOf("username") >= 0){
      localStorage.setItem("sess_token", JSON.stringify(sess_token));
      this.is_logged_in = true;
      this.$emit("login");
    }else{
      this.is_logged_in = false;
      this.$refs.password.focus();
      this.show_error("Login failed");
    }

  },

  log_out: async function(){
    await api_logout();
    localStorage.removeItem("sess_token");

    this.username = "";
    this.password = "";

    this.is_logged_in = false;
    this.$emit("logout");
  }

},

mounted: function(){
  this.is_logged_in = get_login_status();
  this.username = this.is_logged_in ? this.sess_token.username : "";
},

props: []
</javascript>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>Вход</h2>
      <input v-model="email" type="email" placeholder="Email">
      <input v-model="password" type="password" placeholder="Пароль">
      <button @click="login">Войти</button>
      <p class="error" v-if="error">{{ error }}</p>
      <p>Нет аккаунта? <router-link to="/register">Регистрация</router-link></p>
      <router-link to="/">← На главную</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserLogin',
  data() {
    return {
      email: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async login() {
      try {
        const res = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.email, password: this.password })
        })
        const data = await res.json()
        if (res.ok) {
          localStorage.setItem('token', data.access_token)
          localStorage.setItem('user', JSON.stringify({ email: this.email, name: this.email.split('@')[0] }))
          this.$router.push('/')
        } else {
          this.error = data.error || 'Ошибка входа'
        }
      } catch (e) {
        this.error = 'Ошибка соединения'
      }
    }
  }
}
</script>

<style scoped>
.auth-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}
.auth-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  width: 350px;
  text-align: center;
}
input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 5px;
}
button {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.error {
  color: red;
  margin-top: 10px;
}
</style>
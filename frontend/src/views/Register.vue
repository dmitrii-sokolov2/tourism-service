<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>Регистрация</h2>
      <input v-model="name" placeholder="Имя">
      <input v-model="email" type="email" placeholder="Email">
      <input v-model="password" type="password" placeholder="Пароль">
      <button @click="register">Зарегистрироваться</button>
      <p class="error" v-if="error">{{ error }}</p>
      <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
      <router-link to="/">← На главную</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserRegister',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async register() {
      try {
        const res = await fetch('/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: this.name, email: this.email, password: this.password, phone: '' })
        })
        if (res.ok) {
          this.$router.push('/login')
        } else {
          const data = await res.json()
          this.error = data.error || 'Ошибка регистрации'
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
  background: #4CAF50;
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
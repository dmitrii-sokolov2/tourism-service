<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1>👤 Личный кабинет</h1>
      <button class="back-btn" @click="$router.push('/')">← На главную</button>
    </div>

    <div class="profile-content">
      <!-- Профиль -->
      <div class="profile-card">
        <h2>📋 Профиль</h2>
        <div class="profile-info">
          <p><strong>Имя:</strong> {{ user.name }}</p>
          <p><strong>Email:</strong> {{ user.email }}</p>
          <p><strong>Дата регистрации:</strong> {{ user.created_at || 'Не указана' }}</p>
        </div>
      </div>

      <!-- Мои бронирования -->
      <div class="bookings-card">
        <h2>📅 Мои бронирования</h2>
        <div v-if="bookings.length === 0" class="empty-state">
          <p>У вас пока нет бронирований</p>
          <router-link to="/" class="go-home">→ Перейти к турам</router-link>
        </div>
        <div v-else class="bookings-list">
          <div v-for="booking in bookings" :key="booking.id" class="booking-item">
            <div class="booking-info">
              <h3>{{ booking.destination?.name || booking.name }}</h3>
              <p class="country">{{ booking.destination?.country || booking.country }}</p>
              <p><strong>Дата бронирования:</strong> {{ formatDate(booking.booked_at) }}</p>
              <p><strong>Количество человек:</strong> {{ booking.persons || 1 }}</p>
              <p><strong>Отель:</strong> {{ booking.hotel_stars || 3 }}★</p>
              <p><strong>Питание:</strong> {{ getMealText(booking.meal) }}</p>
              <p><strong>Даты:</strong> {{ booking.start_date || '—' }} — {{ booking.end_date || '—' }}</p>
              <p><strong>Цена:</strong> {{ booking.total_price?.toLocaleString() || '—' }} ₽</p>
            </div>
            <button class="cancel-btn" @click="cancelBooking(booking.id)">Отменить</button>
          </div>
        </div>
      </div>

      <!-- Избранное -->
      <div class="favorites-card">
        <h2>⭐ Избранное</h2>
        <div v-if="favorites.length === 0" class="empty-state">
          <p>У вас пока нет избранных туров</p>
          <router-link to="/" class="go-home">→ Перейти к турам</router-link>
        </div>
        <div v-else class="favorites-list">
          <div v-for="fav in favorites" :key="fav.id" class="favorite-item">
            <div class="favorite-info">
              <h3>{{ fav.destination?.name || fav.name }}</h3>
              <p>{{ fav.destination?.country || fav.country }}</p>
              <p><strong>Цена:</strong> {{ fav.price }} ₽</p>
            </div>
            <button class="remove-btn" @click="removeFavorite(fav.id)">❤️ Удалить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfilePage',
  data() {
    return {
      user: {},
      bookings: [],
      favorites: [],
      mealText: {
        none: 'Без питания',
        breakfast: 'Только завтраки',
        half: 'Полупансион',
        full: 'Всё включено'
      }
    }
  },
  async mounted() {
    await this.loadUserProfile()
    await this.loadBookings()
    await this.loadFavorites()
  },
  methods: {
    formatDate(date) {
      if (!date) return '—'
      return new Date(date).toLocaleDateString('ru-RU')
    },
    getMealText(meal) {
      return this.mealText[meal] || 'Без питания'
    },
    async loadUserProfile() {
      const token = localStorage.getItem('token')
      if (!token) {
        this.$router.push('/login')
        return
      }
      
      try {
        const response = await fetch('/api/v1/auth/profile', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          this.user = await response.json()
        }
      } catch (error) {
        console.error('Ошибка загрузки профиля:', error)
      }
    },
    async loadBookings() {
      const token = localStorage.getItem('token')
      try {
        const response = await fetch('/api/v1/users/bookings', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          this.bookings = await response.json()
        }
      } catch (error) {
        console.error('Ошибка загрузки бронирований:', error)
      }
    },
    async loadFavorites() {
      const token = localStorage.getItem('token')
      try {
        const response = await fetch('/api/v1/users/favorites', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          this.favorites = await response.json()
        }
      } catch (error) {
        console.error('Ошибка загрузки избранного:', error)
      }
    },
    async cancelBooking(bookingId) {
      if (!confirm('Вы уверены, что хотите отменить бронирование?')) return
      
      const token = localStorage.getItem('token')
      try {
        const response = await fetch(`/api/v1/bookings/${bookingId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          alert('Бронирование отменено')
          this.loadBookings()
        } else {
          alert('Ошибка при отмене')
        }
      } catch (error) {
        alert('Ошибка соединения')
      }
    },
    async removeFavorite(favId) {
      const token = localStorage.getItem('token')
      try {
        const response = await fetch(`/api/v1/favorites/${favId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          alert('Удалено из избранного')
          this.loadFavorites()
        } else {
          alert('Ошибка при удалении')
        }
      } catch (error) {
        alert('Ошибка соединения')
      }
    }
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 80px 20px 40px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.2);
}

.profile-header h1 {
  color: #ffaa33;
  margin: 0;
}

.back-btn {
  padding: 10px 20px;
  background: rgba(255,255,255,0.2);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.back-btn:hover {
  background: rgba(255,255,255,0.3);
}

.profile-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
}

.profile-card, .bookings-card, .favorites-card {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255,255,255,0.1);
}

.bookings-card, .favorites-card {
  grid-column: span 2;
}

.profile-card h2, .bookings-card h2, .favorites-card h2 {
  color: #ffaa33;
  margin-top: 0;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.2);
  padding-bottom: 10px;
}

.profile-info p {
  margin: 10px 0;
  color: #ddd;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #aaa;
}

.go-home {
  color: #ffaa33;
  text-decoration: none;
}

.bookings-list, .favorites-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.booking-item, .favorite-item {
  background: rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.booking-info h3, .favorite-info h3 {
  margin: 0 0 5px 0;
  color: #ffaa33;
}

.booking-info p, .favorite-info p {
  margin: 5px 0;
  color: #ccc;
  font-size: 14px;
}

.country {
  color: #aaa;
  font-size: 13px;
}

.cancel-btn, .remove-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
}

.cancel-btn {
  background: #dc3545;
  color: white;
}

.cancel-btn:hover {
  background: #c82333;
}

.remove-btn {
  background: #ffaa33;
  color: black;
}

.remove-btn:hover {
  background: #ffbb44;
}

@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
  .bookings-card, .favorites-card {
    grid-column: span 1;
  }
}
</style>
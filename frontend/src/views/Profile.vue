<template>
  <div class="profile-container">
    <!-- Hero секция профиля -->
    <div class="profile-hero">
      <div class="profile-hero-content">
        <div class="avatar-wrapper">
          <div class="avatar">
            <span class="avatar-emoji">👤</span>
            <div class="avatar-status online"></div>
          </div>
          <h1 class="profile-name">{{ user.name || 'Путешественник' }}</h1>
          <p class="profile-email">{{ user.email }}</p>
          <div class="profile-stats">
            <div class="stat">
              <div class="stat-value">{{ bookings.length }}</div>
              <div class="stat-label">Бронирований</div>
            </div>
            <div class="stat">
              <div class="stat-value">{{ favorites.length }}</div>
              <div class="stat-label">В избранном</div>
            </div>
            <div class="stat">
              <div class="stat-value">{{ travelDays }}</div>
              <div class="stat-label">Дней в пути</div>
            </div>
          </div>
        </div>
      </div>
      <div class="profile-bg-pattern"></div>
    </div>

    <!-- Контент профиля -->
    <div class="profile-content">
      <div class="profile-tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'favorites' }" @click="activeTab = 'favorites'">
          ❤️ Избранное
          <span v-if="favorites.length" class="tab-badge">{{ favorites.length }}</span>
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'bookings' }" @click="activeTab = 'bookings'">
          📅 Мои бронирования
          <span v-if="bookings.length" class="tab-badge">{{ bookings.length }}</span>
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'settings' }" @click="activeTab = 'settings'">
          ⚙️ Настройки
        </button>
      </div>

      <!-- Избранное -->
      <div v-if="activeTab === 'favorites'" class="favorites-grid">
        <div v-if="favorites.length === 0" class="empty-state">
          <div class="empty-icon">❤️</div>
          <h3>У вас пока нет избранных туров</h3>
          <p>Добавляйте туры в избранное, чтобы они появились здесь</p>
          <router-link to="/" class="empty-btn">🌍 Перейти к турам</router-link>
        </div>
        <div v-else class="cards-grid">
          <div v-for="fav in favorites" :key="fav.id" class="favorite-card">
            <div class="card-icon">🏝️</div>
            <div class="card-content">
              <h3>{{ fav.destination?.name || fav.name }}</h3>
              <p class="card-country">{{ fav.destination?.country || fav.country }}</p>
              <div class="card-price">{{ fav.price }} ₽</div>
              <div class="card-rating">⭐ {{ fav.rating || 4.5 }}</div>
            </div>
            <button class="remove-fav" @click="removeFavorite(fav.id)">🗑️</button>
          </div>
        </div>
      </div>

      <!-- Бронирования -->
      <div v-if="activeTab === 'bookings'" class="bookings-list">
        <div v-if="bookings.length === 0" class="empty-state">
          <div class="empty-icon">📅</div>
          <h3>У вас пока нет бронирований</h3>
          <p>Забронируйте свой первый тур прямо сейчас!</p>
          <router-link to="/" class="empty-btn">🌍 Перейти к турам</router-link>
        </div>
        <div v-else class="cards-grid">
          <div v-for="booking in bookings" :key="booking.id" class="booking-card">
            <div class="booking-status" :class="getStatusClass(booking.status)">
              {{ getStatusText(booking.status) }}
            </div>
            <div class="card-icon">✈️</div>
            <div class="card-content">
              <h3>{{ booking.destination?.name || booking.name }}</h3>
              <p class="card-country">{{ booking.destination?.country || booking.country }}</p>
              <div class="booking-dates">
                📅 {{ formatDate(booking.start_date) }} — {{ formatDate(booking.end_date) }}
              </div>
              <div class="booking-price">💰 {{ booking.total_price?.toLocaleString() }} ₽</div>
              <div class="booking-hotel">🏨 Отель: {{ booking.hotel_stars || 3 }}★</div>
            </div>
            <button class="cancel-btn" @click="cancelBooking(booking.id)">Отменить</button>
          </div>
        </div>
      </div>

      <!-- Настройки -->
      <div v-if="activeTab === 'settings'" class="settings-panel">
        <div class="settings-card">
          <h3>👤 Личные данные</h3>
          <div class="settings-field">
            <label>Имя</label>
            <input type="text" v-model="editName" placeholder="Ваше имя">
          </div>
          <div class="settings-field">
            <label>Email</label>
            <input type="email" v-model="editEmail" placeholder="Email">
          </div>
          <button class="save-settings" @click="saveSettings">💾 Сохранить изменения</button>
        </div>
        <div class="settings-card">
          <h3>🔔 Уведомления</h3>
          <div class="settings-toggle">
            <label>Получать новости о скидках</label>
            <input type="checkbox" v-model="notifyDiscounts">
          </div>
          <div class="settings-toggle">
            <label>Напоминания о бронированиях</label>
            <input type="checkbox" v-model="notifyReminders">
          </div>
        </div>
      </div>
    </div>

    <button class="logout-btn-bottom" @click="logout">
      🚪 Выйти из аккаунта
    </button>
  </div>
</template>

<script>
export default {
  name: 'ProfilePage',
  data() {
    return {
      user: { name: '', email: '' },
      bookings: [],
      favorites: [],
      activeTab: 'favorites',
      editName: '',
      editEmail: '',
      notifyDiscounts: true,
      notifyReminders: true,
      travelDays: 0
    }
  },
  async mounted() {
    await this.loadUserProfile()
    await this.loadBookings()
    await this.loadFavorites()
    this.calculateTravelDays()
    this.editName = this.user.name
    this.editEmail = this.user.email
  },
  methods: {
    formatDate(date) {
      if (!date) return '—'
      return new Date(date).toLocaleDateString('ru-RU')
    },
    getStatusClass(status) {
      const classes = {
        'active': 'status-active',
        'completed': 'status-completed',
        'cancelled': 'status-cancelled'
      }
      return classes[status] || 'status-active'
    },
    getStatusText(status) {
      const texts = {
        'active': 'Активно',
        'completed': 'Завершён',
        'cancelled': 'Отменён'
      }
      return texts[status] || 'Активно'
    },
    calculateTravelDays() {
      let total = 0
      this.bookings.forEach(booking => {
        if (booking.start_date && booking.end_date) {
          const start = new Date(booking.start_date)
          const end = new Date(booking.end_date)
          const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
          total += days > 0 ? days : 7
        }
      })
      this.travelDays = total
    },
    async loadUserProfile() {
      const token = localStorage.getItem('token')
      if (!token) {
        this.$router.push('/login')
        return
      }
      try {
        const userStr = localStorage.getItem('user')
        if (userStr && userStr !== 'undefined') {
          const user = JSON.parse(userStr)
          this.user = user
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
        } else {
          // Демо-данные для показа
          this.bookings = []
        }
      } catch (error) {
        console.error('Ошибка загрузки бронирований:', error)
        this.bookings = []
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
        } else {
          this.favorites = []
        }
      } catch (error) {
        console.error('Ошибка загрузки избранного:', error)
        this.favorites = []
      }
    },
    async removeFavorite(favId) {
      if (!confirm('Удалить из избранного?')) return
      const token = localStorage.getItem('token')
      try {
        const response = await fetch(`/api/v1/favorites/${favId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          this.favorites = this.favorites.filter(f => f.id !== favId)
          alert('Удалено из избранного')
        }
      } catch (error) {
        alert('Ошибка при удалении')
      }
    },
    async cancelBooking(bookingId) {
      if (!confirm('Отменить бронирование?')) return
      const token = localStorage.getItem('token')
      try {
        const response = await fetch(`/api/v1/bookings/${bookingId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          alert('Бронирование отменено')
          this.loadBookings()
        }
      } catch (error) {
        alert('Ошибка при отмене')
      }
    },
    saveSettings() {
      // Сохраняем настройки в localStorage
      const settings = {
        notifyDiscounts: this.notifyDiscounts,
        notifyReminders: this.notifyReminders
      }
      localStorage.setItem('userSettings', JSON.stringify(settings))
      
      // Обновляем пользователя
      const user = { ...this.user, name: this.editName, email: this.editEmail }
      localStorage.setItem('user', JSON.stringify(user))
      this.user = user
      
      alert('Настройки сохранены!')
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/'
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a2a 0%, #1a1a4a 100%);
  color: white;
}

/* Hero секция */
.profile-hero {
  position: relative;
  padding: 80px 20px 60px;
  text-align: center;
  background: linear-gradient(135deg, rgba(255,170,51,0.1), transparent);
  overflow: hidden;
}

.profile-hero-content {
  position: relative;
  z-index: 2;
}

.avatar-wrapper {
  display: inline-block;
  position: relative;
}

.avatar {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #ffaa33, #ff8844);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 10px 30px rgba(255,170,51,0.3);
}

.avatar-emoji {
  font-size: 48px;
}

.avatar-status {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 18px;
  height: 18px;
  background: #4CAF50;
  border-radius: 50%;
  border: 2px solid #fff;
}

.profile-name {
  font-size: 32px;
  margin-bottom: 8px;
  color: #ffaa33;
}

.profile-email {
  color: rgba(255,255,255,0.7);
  margin-bottom: 30px;
}

.profile-stats {
  display: flex;
  justify-content: center;
  gap: 50px;
}

.stat {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #ffaa33;
}

.stat-label {
  font-size: 12px;
  color: rgba(255,255,255,0.6);
}

.profile-bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(rgba(255,170,51,0.1) 1px, transparent 1px);
  background-size: 30px 30px;
  z-index: 1;
}

/* Табы */
.profile-tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin: 30px 20px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 12px 24px;
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 30px;
  color: white;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-btn:hover {
  background: rgba(255,170,51,0.3);
  transform: translateY(-2px);
}

.tab-btn.active {
  background: #ffaa33;
  color: #1a1a2a;
}

.tab-badge {
  background: rgba(0,0,0,0.5);
  padding: 2px 6px;
  border-radius: 20px;
  font-size: 12px;
}

/* Сетка карточек */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Карточка избранного */
.favorite-card, .booking-card {
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 15px;
  align-items: center;
  position: relative;
  transition: all 0.3s;
  border: 1px solid rgba(255,255,255,0.1);
}

.favorite-card:hover, .booking-card:hover {
  transform: translateY(-5px);
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,170,51,0.3);
}

.card-icon {
  font-size: 40px;
}

.card-content {
  flex: 1;
}

.card-content h3 {
  margin: 0 0 5px;
  color: #ffaa33;
}

.card-country {
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  margin-bottom: 8px;
}

.card-price {
  font-weight: bold;
  font-size: 18px;
  margin-top: 8px;
}

.remove-fav, .cancel-btn {
  background: rgba(244,67,54,0.2);
  border: none;
  padding: 8px 12px;
  border-radius: 30px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.remove-fav:hover, .cancel-btn:hover {
  background: #f44336;
  transform: scale(1.05);
}

/* Специальные стили для карточки бронирования */
.booking-status {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 20px;
  font-weight: bold;
}

.status-active { background: #4CAF50; color: white; }
.status-completed { background: #2196F3; color: white; }
.status-cancelled { background: #f44336; color: white; }

.booking-dates, .booking-price, .booking-hotel {
  font-size: 12px;
  margin: 4px 0;
  color: rgba(255,255,255,0.7);
}

/* Пустое состояние */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  margin-bottom: 10px;
}

.empty-state p {
  color: rgba(255,255,255,0.6);
  margin-bottom: 20px;
}

.empty-btn {
  display: inline-block;
  padding: 12px 24px;
  background: #ffaa33;
  color: #1a1a2a;
  text-decoration: none;
  border-radius: 30px;
  font-weight: bold;
  transition: all 0.3s;
}

.empty-btn:hover {
  transform: scale(1.05);
}

/* Настройки */
.settings-panel {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.settings-card {
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
}

.settings-card h3 {
  color: #ffaa33;
  margin-bottom: 20px;
}

.settings-field {
  margin-bottom: 15px;
}

.settings-field label {
  display: block;
  margin-bottom: 5px;
  font-size: 12px;
  color: rgba(255,255,255,0.7);
}

.settings-field input {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.1);
  color: white;
}

.save-settings {
  width: 100%;
  padding: 12px;
  background: #ffaa33;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.save-settings:hover {
  background: #ffcc44;
  transform: translateY(-2px);
}

.settings-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.settings-toggle input {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

/* Кнопка выхода */
.logout-btn-bottom {
  display: block;
  width: 200px;
  margin: 40px auto;
  padding: 12px 24px;
  background: rgba(244,67,54,0.2);
  border: 1px solid #f44336;
  border-radius: 30px;
  color: #f44336;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn-bottom:hover {
  background: #f44336;
  color: white;
}
</style>
<template>
  <div id="home">
    <div class="filters-toggle" @click="toggleFilters" @mouseenter="showFilters = true">
      <span class="filters-icon"></span>
      <span class="filters-text">Фильтры</span>
    </div>

    <div class="filters-sidebar" :class="{ 'filters-visible': showFilters }" @mouseleave="showFilters = false">
      <h3>Фильтры</h3>
      <div class="filter-group">
        <label>Цена (₽)</label>
        <div class="price-range">
          <input type="number" v-model="priceMin" placeholder="от">
          <span>-</span>
          <input type="number" v-model="priceMax" placeholder="до">
        </div>
      </div>

      <div class="filter-group">
        <label>Длительность (дни)</label>
        <div class="duration-range">
          <input type="number" v-model="durationMin" placeholder="от">
          <span>-</span>
          <input type="number" v-model="durationMax" placeholder="до">
        </div>
      </div>

      <div class="filter-group">
        <label>Страна</label>
        <select v-model="selectedCountry">
          <option value="">Все страны</option>
          <option v-for="country in countries" :key="country" :value="country">{{ country }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Рейтинг</label>
        <div class="rating-buttons">
          <button v-for="star in 5" :key="star" @click="selectedRating = star" :class="{ active: selectedRating === star }" class="filter-btn">{{ star }}★</button>
          <button @click="selectedRating = null" class="filter-clear">Все</button>
        </div>
      </div>

      <div class="filter-group">
        <label>Тип тура</label>
        <div class="type-buttons">
          <button v-for="type in tourTypes" :key="type" @click="selectedType = type" :class="{ active: selectedType === type }" class="filter-btn">{{ type }}</button>
          <button @click="selectedType = null" class="filter-clear">Все</button>
        </div>
      </div>

      <div class="filter-group">
        <label>Отель</label>
        <div class="stars-buttons">
          <button v-for="star in [5,4,3]" :key="star" @click="selectedStars = star" :class="{ active: selectedStars === star }" class="filter-btn">{{ star }}★</button>
          <button @click="selectedStars = null" class="filter-clear">Любой</button>
        </div>
      </div>

      <div class="filter-group">
        <label>Трансфер</label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="hasTransfer"> Трансфер включён
        </label>
      </div>

      <button @click="applyFilters" class="apply-btn">Применить</button>
      <button @click="resetFilters" class="reset-btn">Сбросить</button>
    </div>

    <div class="auth-buttons">
      <button v-if="!isLoggedIn" @click="$router.push('/login')" class="login-btn">Войти</button>
      <button v-if="!isLoggedIn" @click="$router.push('/register')" class="register-btn">Регистрация</button>
      <div v-if="isLoggedIn" class="user-info">
        <span class="user-avatar"></span>
        <span class="user-name">{{ userName }}</span>
        <router-link to="/profile" class="profile-link">👤 Профиль</router-link>
        <a href="#" @click.prevent="logout" class="logout-link">🚪 Выйти</a>
      </div>
    </div>

    <div id="globe-container"></div>
    <div v-if="isAdmin" class="admin-link">
      <router-link to="/admin">Админ-панель</router-link>
    </div>

    <div v-if="showTourCard" class="tour-card-modal" @click.self="closeTourCard">
      <div class="tour-card">
        <button class="close-btn" @click="closeTourCard">✕</button>
        <h2>{{ selectedCity?.name }}</h2>
        <p class="country">{{ selectedCity?.country }}</p>
        
        <div class="tour-details">
          <p><strong>Цена за день:</strong> {{ Math.round(selectedCity?.price / (selectedCity?.duration_days || 7)) }} ₽</p>
          <p><strong>Рейтинг:</strong> {{ selectedCity?.rating || 4.5 }}</p>
          <p><strong>Отель:</strong> {{ selectedCity?.hotel_stars || 3 }}★</p>
          <p><strong>Трансфер:</strong> {{ selectedCity?.transfer ? 'Включён' : 'Не включён' }}</p>
        </div>

        <div class="booking-form">
          <h3>Оформление бронирования</h3>
          
          <div class="form-row">
            <label>Количество человек:</label>
            <input type="number" v-model.number="bookingData.persons" min="1" max="10" @input="calculateTotal">
          </div>

          <div class="form-row">
            <label>Отель:</label>
            <select v-model="bookingData.hotelStars" @change="calculateTotal">
              <option :value="3">3★ (стандарт)</option>
              <option :value="4">4★ (комфорт)</option>
              <option :value="5">5★ (люкс)</option>
            </select>
          </div>

          <div class="form-row">
            <label>Питание:</label>
            <select v-model="bookingData.meal" @change="calculateTotal">
              <option value="none">Без питания</option>
              <option value="breakfast">Только завтраки</option>
              <option value="half">Полупансион</option>
              <option value="full">Всё включено</option>
            </select>
          </div>

          <div class="form-row">
            <label>Дата начала:</label>
            <input type="date" v-model="bookingData.startDate" @change="calculateTotal">
          </div>

          <div class="form-row">
            <label>Дата окончания:</label>
            <input type="date" v-model="bookingData.endDate" @change="calculateTotal">
          </div>

          <div class="total-price">
            <h3>Итоговая цена: <span>{{ totalPrice.toLocaleString() }} ₽</span></h3>
          </div>

          <button class="book-btn" @click="bookTourExtended">Забронировать сейчас</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Globe from 'globe.gl'

export default {
  name: 'HomePage',
  data() {
    return {
      isLoggedIn: false,
      isAdmin: false,
      userName: '',
      globe: null,
      cities: [],
      allCities: [],
      countries: [],
      priceMin: '',
      priceMax: '',
      durationMin: '',
      durationMax: '',
      selectedCountry: '',
      selectedRating: null,
      selectedType: null,
      selectedStars: null,
      hasTransfer: false,
      tourTypes: ['Экскурсионный', 'Пляжный', 'Горнолыжный', 'Гастрономический', 'Приключенческий'],
      showTourCard: false,
      selectedCity: null,
      showFilters: false,
      bookingData: {
        persons: 1,
        hotelStars: 3,
        meal: 'none',
        startDate: '',
        endDate: ''
      },
      totalPrice: 0,
      mealPrices: {
        none: 1.0,
        breakfast: 1.15,
        half: 1.35,
        full: 1.6
      }
    }
  },
  async mounted() {
    this.checkAuth()
    await this.loadCities()
    this.initGlobe()
  },
methods: {
  checkAuth() {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr && userStr !== 'undefined') {
      try {
        const user = JSON.parse(userStr)
        this.isLoggedIn = true
        this.userName = user.name || user.email
        if (user.email === 'admin@mail.com') {
          this.isAdmin = true
        }
      } catch (e) {
        console.error('Ошибка парсинга user:', e)
        this.isLoggedIn = false
      }
    } else {
      this.isLoggedIn = false
    }
  },

  async loadCities() {
    try {
      const response = await fetch('/api/v1/destinations/coordinates')
      const data = await response.json()
      this.allCities = data
      this.cities = data
      this.countries = [...new Set(data.map(c => c.country))]
    } catch (error) {
      console.error('Ошибка загрузки городов:', error)
    }
  },

  initGlobe() {
    this.globe = Globe()
      .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
      .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
      .pointsData(this.cities)
      .pointColor(() => '#ff4444')
      .pointAltitude(0.05)
      .pointRadius(0.8)
      .pointLabel(d => `
        <div style="background:black; color:white; padding:10px; border-radius:8px;">
          <b>${d.name}</b><br>${d.country}<br>${d.price} ₽<br>${d.rating || 4.5}<br>${d.hotel_stars || 3}★
        </div>
      `)
      .onPointClick(d => {
        if (!this.isLoggedIn) {
          alert('Войдите, чтобы забронировать тур')
        } else {
          this.selectedCity = d
          this.showTourCard = true
          this.calculateTotal()
        }
      })
    
    this.globe(document.getElementById('globe-container'))
    
    window.addEventListener('resize', () => {
      this.globe.width(window.innerWidth)
      this.globe.height(window.innerHeight)
    })
  },

  applyFilters() {
    let filtered = [...this.allCities]
    
    if (this.priceMin) filtered = filtered.filter(c => parseInt(c.price) >= parseInt(this.priceMin))
    if (this.priceMax) filtered = filtered.filter(c => parseInt(c.price) <= parseInt(this.priceMax))
    if (this.durationMin) filtered = filtered.filter(c => (c.duration_days || 0) >= parseInt(this.durationMin))
    if (this.durationMax) filtered = filtered.filter(c => (c.duration_days || 0) <= parseInt(this.durationMax))
    if (this.selectedCountry) filtered = filtered.filter(c => c.country === this.selectedCountry)
    if (this.selectedRating) filtered = filtered.filter(c => (c.rating || 4.5) >= this.selectedRating)
    if (this.selectedType) filtered = filtered.filter(c => c.tour_type === this.selectedType)
    if (this.selectedStars) filtered = filtered.filter(c => (c.hotel_stars || 3) >= this.selectedStars)
    if (this.hasTransfer) filtered = filtered.filter(c => c.transfer === true)
    
    this.cities = filtered
    if (this.globe) this.globe.pointsData(this.cities)
  },

  resetFilters() {
    this.priceMin = ''
    this.priceMax = ''
    this.durationMin = ''
    this.durationMax = ''
    this.selectedCountry = ''
    this.selectedRating = null
    this.selectedType = null
    this.selectedStars = null
    this.hasTransfer = false
    this.cities = [...this.allCities]
    if (this.globe) this.globe.pointsData(this.cities)
  },

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.reload()
  },

  closeTourCard() {
    this.showTourCard = false
    this.selectedCity = null
  },

  calculateTotal() {
    if (!this.selectedCity) return
    
    const basePricePerDay = this.selectedCity.price / (this.selectedCity.duration_days || 7)
    const hotelMultiplier = this.bookingData.hotelStars / 3
    const mealMultiplier = this.mealPrices[this.bookingData.meal] || 1
    
    let days = this.selectedCity.duration_days || 7
    if (this.bookingData.startDate && this.bookingData.endDate) {
      const start = new Date(this.bookingData.startDate)
      const end = new Date(this.bookingData.endDate)
      days = Math.max(1, Math.ceil((end - start) / (1000 * 60 * 60 * 24)))
    }
    
    this.totalPrice = Math.round(
      basePricePerDay * days * this.bookingData.persons * hotelMultiplier * mealMultiplier
    )
  },

  async bookTourExtended() {
    if (!this.selectedCity) return
    
    const token = localStorage.getItem('token')
    if (!token) {
      alert(' Войдите, чтобы забронировать тур')
      return
    }
    
    const booking = {
      destination_id: this.selectedCity.id,
      persons: this.bookingData.persons,
      hotel_stars: this.bookingData.hotelStars,
      meal: this.bookingData.meal,
      start_date: this.bookingData.startDate,
      end_date: this.bookingData.endDate,
      total_price: this.totalPrice
    }
    
    try {
      const response = await fetch('/api/book', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(booking)
      })
      
      const data = await response.json()
      
      if (response.ok) {
        alert(` Тур в ${this.selectedCity.name} успешно забронирован!\n💰 Итого: ${this.totalPrice.toLocaleString()} ₽`)
        this.closeTourCard()
      } else {
        alert(`Ошибка: ${data.error || 'Попробуйте позже'}`)
      }
    } catch (error) {
      alert('Ошибка соединения')
    }
  },

  toggleFilters() {
    this.showFilters = !this.showFilters
    }
  }
}
</script>

<style>
#globe-container {
  width: 100vw;
  height: 100vh;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

.filters-toggle {
  position: fixed;
  top: 80px;
  left: 20px;
  z-index: 210;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  padding: 12px 16px;
  border-radius: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(255, 170, 51, 0.5);
  transition: all 0.3s;
}

.filters-toggle:hover {
  background: rgba(255, 170, 51, 0.2);
  transform: scale(1.05);
}

.filters-icon {
  font-size: 18px;
}

.filters-text {
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.filters-sidebar {
  position: fixed;
  top: 80px;
  left: 20px;
  width: 440px;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  padding: 20px;
  z-index: 200;
  color: white;
  border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateX(-120%);
  pointer-events: none;
}

.filters-sidebar.filters-visible {
  opacity: 1;
  transform: translateX(0);
  pointer-events: auto;
}

.filters-sidebar h3 {
  margin: 0 0 20px 0;
  text-align: center;
  color: #ffaa33;
  font-size: 22px;
  font-weight: bold;
}

.filter-group {
  margin-bottom: 20px;
}

.filter-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: bold;
  color: #ddd;
}

.price-range, .duration-range {
  display: flex;
  gap: 10px;
  align-items: center;
}

.price-range input, .duration-range input {
  flex: 1;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.3);
  background: rgba(255,255,255,0.15);
  color: white;
  text-align: center;
}

select {
  width: 100%;
  padding: 8px 10px;
  border-radius: 6px;
  background: rgba(255,255,255,0.15);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  cursor: pointer;
}

.rating-buttons, .type-buttons, .stars-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  background: rgba(255,255,255,0.2);
  color: white;
  transition: all 0.2s;
}

.filter-btn.active {
  background: #ffaa33;
  color: black;
  font-weight: bold;
}

.filter-clear {
  padding: 6px 12px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  background: rgba(255,255,255,0.1);
  color: #aaa;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: white;
}

.apply-btn, .reset-btn {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  transition: all 0.3s;
}

.apply-btn {
  background: #4CAF50;
  color: white;
}

.reset-btn {
  background: #ffaa33;
  color: black;
}

.auth-buttons {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 200;
  display: flex;
  gap: 10px;
}

.auth-buttons button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
}


.login-btn {
  background: #ffaa00;
  color: black;
}

.register-btn {
  background: #4CAF50;
  color: white;
}

.user-info {
  background: rgba(0,0,0,0.7);
  padding: 8px 16px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  gap: 10px;
  backdrop-filter: blur(5px);
}

.user-name {
  font-weight: bold;
  color: #ffaa00;
}

.logout-link {
  color: #ffaa00;
  text-decoration: none;
  padding: 5px 10px;
  background: rgba(0,0,0,0.3);
  border-radius: 5px;
}

.admin-link {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 200;
  background: rgba(0,0,0,0.7);
  padding: 10px 15px;
  border-radius: 8px;
}

.admin-link a {
  color: #ffaa33;
  text-decoration: none;
  font-weight: bold;
}

.tour-card-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.tour-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  padding: 30px;
  border-radius: 20px;
  width: 450px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  position: relative;
  border: 1px solid rgba(255, 170, 51, 0.3);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  background: none;
  border: none;
  color: #ffaa33;
  font-size: 24px;
  cursor: pointer;
}

.tour-card h2 {
  margin: 0 0 5px 0;
  color: #ffaa33;
}

.country {
  color: #aaa;
  margin-bottom: 20px;
  font-size: 14px;
}

.tour-details {
  margin: 20px 0;
  line-height: 1.8;
}

.booking-form {
  margin-top: 20px;
  border-top: 1px solid rgba(255,255,255,0.2);
  padding-top: 15px;
}

.booking-form h3 {
  color: #ffaa33;
  margin-bottom: 15px;
  font-size: 18px;
}

.form-row {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-row label {
  flex: 1;
  font-size: 14px;
}

.form-row input, .form-row select {
  flex: 2;
  padding: 8px;
  border-radius: 6px;
  border: none;
  background: rgba(255,255,255,0.2);
  color: white;
}

.total-price {
  margin: 15px 0;
  text-align: center;
  background: rgba(255,170,51,0.2);
  padding: 10px;
  border-radius: 8px;
}

.total-price span {
  color: #ffaa33;
  font-size: 24px;
  font-weight: bold;
}

.book-btn {
  width: 100%;
  padding: 12px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.book-btn:hover {
  background: #45a049;
  transform: translateY(-2px);
}
.profile-link {
  color: #ffaa33;
  text-decoration: none;
  padding: 10px 20px;
  background: rgba(0,0,0,0.7);
  border-radius: 5px;
  backdrop-filter: blur(5px);
}

.profile-link:hover {
  background: rgba(0,0,0,0.5);
}
</style>
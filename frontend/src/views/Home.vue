<template>
  <div class="tourism-app">
    <div class="hero-section" id="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="gradient-text" id="typewriter"></span>
        </h1>
        <p class="hero-subtitle">Откройте мир путешествий с нами</p>
        
        <div class="timer-section">
          <div class="timer-title">⭐ СУПЕРПРЕДЛОЖЕНИЕ ⭐</div>
          <div class="countdown">
            <div class="countdown-item">
              <span class="countdown-number" id="days">00</span>
              <span>дней</span>
            </div>
            <div class="countdown-item">
              <span class="countdown-number" id="hours">00</span>
              <span>часов</span>
            </div>
            <div class="countdown-item">
              <span class="countdown-number" id="minutes">00</span>
              <span>минут</span>
            </div>
            <div class="countdown-item">
              <span class="countdown-number" id="seconds">00</span>
              <span>секунд</span>
            </div>
          </div>
          <div class="timer-offer">🔥 ЛЮБОЙ ТУР СО СКИДКОЙ 30% 🔥</div>
        </div>

        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-number" data-target="150">0</div>
            <div class="stat-label">Направлений</div>
          </div>
          <div class="stat-item">
            <div class="stat-number" data-target="1200">0</div>
            <div class="stat-label">Счастливых туристов</div>
          </div>
          <div class="stat-item">
            <div class="stat-number" data-target="50">0</div>
            <div class="stat-label">Стран</div>
          </div>
        </div>
      </div>
    </div>
    <div class="game-section">
      <div class="section-header">
        <h2>🎁 СОБЕРИ КОЛЛЕКЦИЮ СУВЕНИРОВ 🎁</h2>
        <p>Кликай на сувениры, чтобы получить секретный промокод!</p>
      </div>
      <div class="souvenirs">
        <div v-for="(item, index) in souvenirs" :key="index" 
             class="souvenir" 
             :class="{ collected: item.collected }"
             @click="collectSouvenir(index)">
          <span class="souvenir-icon">{{ item.icon }}</span>
          <span class="souvenir-name">{{ item.name }}</span>
        </div>
      </div>
      <div v-if="promoCode" class="promo-code">
        🎉 Твой промокод: <strong>{{ promoCode }}</strong> на скидку 15%! 🎉
      </div>
    </div>

      <!-- Глобус с фильтрами -->
<div class="globe-wrapper">
  <div class="globe-section">
    <div class="section-header">
      <h2>🌍 Выберите своё приключение</h2>
      <p>Кликните на любую точку на глобусе, чтобы узнать больше</p>
    </div>
    <div id="globe-container"></div>
  </div>

  <div class="filters-drawer" @mouseenter="showFilters = true" @mouseleave="showFilters = false">
    <div class="filters-tab">
      <span class="tab-icon">🎯</span>
      <span class="tab-text">Фильтры</span>
    </div>
    <div class="filters-panel" :class="{ 'filters-visible': showFilters }">
      <h3>🔍 Фильтры</h3>
      
      <div class="filter-group">
        <label>💰 Цена (₽)</label>
        <div class="price-range">
          <input type="number" v-model="priceMin" placeholder="от">
          <span>-</span>
          <input type="number" v-model="priceMax" placeholder="до">
        </div>
      </div>

      <div class="filter-group">
        <label>📅 Длительность (дни)</label>
        <div class="duration-range">
          <input type="number" v-model="durationMin" placeholder="от">
          <span>-</span>
          <input type="number" v-model="durationMax" placeholder="до">
        </div>
      </div>

      <div class="filter-group">
        <label>🌍 Страна</label>
        <select v-model="selectedCountry">
          <option value="">Все страны</option>
          <option v-for="country in countries" :key="country" :value="country">{{ country }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label>⭐ Рейтинг</label>
        <div class="rating-buttons">
          <button v-for="star in 5" :key="star" @click="selectedRating = star" :class="{ active: selectedRating === star }" class="filter-btn">{{ star }}★</button>
          <button @click="selectedRating = null" class="filter-clear">Все</button>
        </div>
      </div>

      <div class="filter-group">
        <label>🏖️ Тип тура</label>
        <div class="type-buttons">
          <button v-for="type in tourTypes" :key="type" @click="selectedType = type" :class="{ active: selectedType === type }" class="filter-btn">{{ type }}</button>
          <button @click="selectedType = null" class="filter-clear">Все</button>
        </div>
      </div>

      <div class="filter-group">
        <label>🏨 Отель</label>
        <div class="stars-buttons">
          <button v-for="star in [5,4,3]" :key="star" @click="selectedStars = star" :class="{ active: selectedStars === star }" class="filter-btn">{{ star }}★</button>
          <button @click="selectedStars = null" class="filter-clear">Любой</button>
        </div>
      </div>

      <div class="filter-group">
        <label>🚗 Трансфер</label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="hasTransfer"> Трансфер включён
        </label>
      </div>

      <button @click="applyFilters" class="apply-btn">✅ Применить</button>
      <button @click="resetFilters" class="reset-btn">🔄 Сбросить</button>
    </div>
  </div>
</div>

    <!-- Кнопки авторизации -->
    <div class="auth-buttons">
      <button v-if="!isLoggedIn" @click="$router.push('/login')" class="btn-login">
        🔐 Войти
      </button>
      <button v-if="!isLoggedIn" @click="$router.push('/register')" class="btn-register">
        📝 Регистрация
      </button>
      <div v-if="isLoggedIn" class="user-info-glass">
        <span class="user-avatar">👤</span>
        <span class="user-name">{{ userName }}</span>
        <router-link to="/profile" class="profile-link">Мой профиль</router-link>
        <a href="#" @click.prevent="logout" class="logout-link">Выйти</a>
      </div>
    </div>

    <div v-if="isAdmin" class="admin-link-glass">
      <router-link to="/admin">🛠️ Админ-панель</router-link>
    </div>

    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand">
          <h3>TravelEasy</h3>
          <p>Путешествия, которые меняют жизнь</p>
        </div>
        <div class="footer-links">
          <a href="#">О нас</a>
          <a href="#">Контакты</a>
          <a href="#">Помощь</a>
          <a href="#">Политика конфиденциальности</a>
        </div>
        <div class="footer-social">
          <a href="#" class="social-icon">📘</a>
          <a href="#" class="social-icon">📷</a>
          <a href="#" class="social-icon">🎵</a>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2026 TravelEasy — Все права защищены</p>
      </div>
    </footer>

    <!-- Модальное окно -->
    <div v-if="showTourCard" class="tour-card-modal" @click.self="closeTourCard">
      <div class="tour-card glass-card">
        <button class="close-btn" @click="closeTourCard">✕</button>
        <div class="tour-card-icon">🏝️</div>
        <h2>{{ selectedCity?.name }}</h2>
        <p class="country">{{ selectedCity?.country }}</p>
        <div class="tour-details">
          <div class="detail-item"><span class="detail-icon">💰</span><span>Цена за день: {{ Math.round(selectedCity?.price / (selectedCity?.duration_days || 7)) }} ₽</span></div>
          <div class="detail-item"><span class="detail-icon">⭐</span><span>Рейтинг: {{ selectedCity?.rating || 4.5 }}</span></div>
          <div class="detail-item"><span class="detail-icon">🏨</span><span>Отель: {{ selectedCity?.hotel_stars || 3 }}★</span></div>
          <div class="detail-item"><span class="detail-icon">🚗</span><span>Трансфер: {{ selectedCity?.transfer ? '✅ Включён' : '❌ Не включён' }}</span></div>
        </div>
        <div class="booking-form">
              <h3>📅 Забронировать</h3>
              
              <div class="form-row">
                <label>👥 Человек:</label>
                <input type="number" v-model.number="bookingData.persons" min="1" max="10" @input="calculateTotal">
              </div>

              <div class="form-row">
                <label>🏨 Категория отеля:</label>
                <select v-model="bookingData.hotelStars" @change="calculateTotal">
                  <option :value="3">🌟 Стандарт (3★)</option>
                  <option :value="4">🌟🌟 Комфорт (4★)</option>
                  <option :value="5">🌟🌟🌟 Люкс (5★)</option>
                </select>
              </div>

              <div class="form-row">
                <label>🍽️ Питание:</label>
                <select v-model="bookingData.meal" @change="calculateTotal">
                  <option value="none">Без питания</option>
                  <option value="breakfast">Завтраки</option>
                  <option value="half">Полупансион</option>
                  <option value="full">Всё включено</option>
                </select>
              </div>

              <div class="form-row">
                <label>📅 Дата начала:</label>
                <input type="date" v-model="bookingData.startDate" @change="calculateTotal">
              </div>

              <div class="form-row">
                <label>📅 Дата окончания:</label>
                <input type="date" v-model="bookingData.endDate" @change="calculateTotal">
              </div>

              <div class="promo-section">
                <div class="promo-header" @click="showPromoInput = !showPromoInput">
                  <span class="promo-icon">🎟️</span>
                  <span class="promo-label">Есть промокод?</span>
                  <span class="promo-toggle">{{ showPromoInput ? '▲' : '▼' }}</span>
                </div>
                <div class="promo-input" :class="{ 'promo-visible': showPromoInput }">
                  <input type="text" v-model="promoInput" placeholder="Введите промокод" @keyup.enter="applyPromoCode">
                  <button @click="applyPromoCode" class="apply-promo-btn">Применить</button>
                </div>
                <div v-if="promoMessage" class="promo-message" :class="{ 'promo-success': promoSuccess, 'promo-error': !promoSuccess }">
                  {{ promoMessage }}
                </div>
              </div>

              <div class="price-breakdown">
                <div class="price-row">
                  <span>💰 Базовая стоимость:</span>
                  <span>{{ totalPrice.toLocaleString() }} ₽</span>
                </div>
                <div v-if="discountAmount > 0" class="price-row discount-row">
                  <span>🎉 Скидка ({{ discountPercent }}%):</span>
                  <span>- {{ discountAmount.toLocaleString() }} ₽</span>
                </div>
                <div class="price-row total-row">
                  <span>💎 Итого:</span>
                  <span class="final-price">{{ finalPrice.toLocaleString() }} ₽</span>
                </div>
                <div v-if="savedAmount > 0" class="saved-badge">
                  💰 Вы сэкономили {{ savedAmount.toLocaleString() }} ₽!
                </div>
              </div>

              <button class="book-btn" @click="bookTourExtended">✅ Забронировать сейчас</button>
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
      showFilters: false,
      tourTypes: ['Экскурсионный', 'Пляжный', 'Горнолыжный', 'Гастрономический', 'Приключенческий'],
      showTourCard: false,
      showPromoInput: false,
      promoInput: '',
      promoMessage: '',
      promoSuccess: false,
      discountPercent: 0,
      discountAmount: 0,
      finalPrice: 0,
      savedAmount: 0,
      validPromoCodes: {
        'TRAVEL2026': 15,
        'WELCOME': 10,
        'SUMMER': 20,
        'TOURIST': 5
      },
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
      },
      souvenirs: [
        { icon: '🗿', name: 'Статуэтка', collected: false },
        { icon: '🍕', name: 'Магнит', collected: false },
        { icon: '🎭', name: 'Маска', collected: false },
        { icon: '🐪', name: 'Верблюд', collected: false }
      ],
      promoCode: ''
    }
  },
  async mounted() {
    this.checkAuth()
    await this.loadCities()
    this.initGlobe()
    this.animateNumbers()
    this.startCountdown()
    this.typewriterEffect()
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
          if (user.email === 'admin@mail.com') this.isAdmin = true
        } catch (e) { console.error(e) }
      }
    },

    animateNumbers() {
      const numbers = document.querySelectorAll('.stat-number')
      numbers.forEach(num => {
        const target = parseInt(num.getAttribute('data-target'))
        let current = 0
        const increment = target / 30
        const updateNumber = () => {
          current += increment
          if (current < target) {
            num.textContent = Math.floor(current)
            requestAnimationFrame(updateNumber)
          } else {
            num.textContent = target
          }
        }
        setTimeout(updateNumber, 100)
      })
    },

    async loadCities() {
      try {
        const response = await fetch('/api/v1/destinations/coordinates')
        const data = await response.json()
        this.allCities = data
        this.cities = data
        this.countries = [...new Set(data.map(c => c.country))]
      } catch (error) { console.error(error) }
    },

    initGlobe() {
      this.globe = Globe()
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
        .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
        .pointsData(this.cities)
        .pointColor(() => '#ff4444')
        .pointAltitude(0.03)  // уменьшено с 0.05
        .pointRadius(0.6)     // уменьшено с 0.8
        .pointLabel(d => `<div style="background:black; color:white; padding:8px; border-radius:6px;"><b>${d.name}</b><br>${d.country}<br>💰 ${d.price} ₽<br>⭐ ${d.rating || 4.5}</div>`)
        .onPointClick(d => {
          if (!this.isLoggedIn) alert('🔐 Войдите, чтобы забронировать тур')
          else { this.selectedCity = d; this.showTourCard = true; this.calculateTotal() }
        })
      this.globe(document.getElementById('globe-container'))
      window.addEventListener('resize', () => { this.globe.width(window.innerWidth); this.globe.height(window.innerHeight) })
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
      this.totalPrice = Math.round(basePricePerDay * days * this.bookingData.persons * hotelMultiplier * mealMultiplier)
      
      if (this.discountPercent > 0) {
        this.discountAmount = Math.round(this.totalPrice * this.discountPercent / 100)
        this.finalPrice = this.totalPrice - this.discountAmount
        this.savedAmount = this.discountAmount
      } else {
        this.discountAmount = 0
        this.finalPrice = this.totalPrice
        this.savedAmount = 0
      }
},

    async bookTourExtended() {
      if (!this.selectedCity) return
      const token = localStorage.getItem('token')
      if (!token) { alert('🔐 Войдите, чтобы забронировать тур'); return }
      
      const booking = {
        destination_id: this.selectedCity.id,
        persons: this.bookingData.persons,
        hotel_stars: this.bookingData.hotelStars,
        meal: this.bookingData.meal,
        start_date: this.bookingData.startDate,
        end_date: this.bookingData.endDate,
        original_price: this.totalPrice,
        discount_percent: this.discountPercent,
        final_price: this.finalPrice
      }
      
      try {
        const response = await fetch('/api/book', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify(booking) })
        const data = await response.json()
        if (response.ok) {
          alert(`✅ Тур в ${this.selectedCity.name} успешно забронирован!\n💰 Исходная цена: ${this.totalPrice.toLocaleString()} ₽\n🎉 Скидка: ${this.discountPercent}%\n💎 Итого: ${this.finalPrice.toLocaleString()} ₽`)
          this.closeTourCard()
        } else {
          alert(`❌ Ошибка: ${data.error || 'Попробуйте позже'}`)
        }
      } catch (error) { alert('❌ Ошибка соединения') }
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

    collectSouvenir(index) {
      if (!this.souvenirs[index].collected) {
        this.souvenirs[index].collected = true
        if (this.souvenirs.every(s => s.collected)) {
          this.promoCode = 'TRAVEL2026'
          alert('🎉 Поздравляю! Ты собрал все сувениры!\nТвой промокод: TRAVEL2026 на скидку 15%!')
        }
      }
    },

    startCountdown() {
      const targetDate = new Date()
      targetDate.setDate(targetDate.getDate() + 3)
      targetDate.setHours(0, 0, 0, 0)
      const updateCountdown = () => {
        const now = new Date()
        const diff = targetDate - now
        if (diff <= 0) {
          document.getElementById('days').innerHTML = '00'
          document.getElementById('hours').innerHTML = '00'
          document.getElementById('minutes').innerHTML = '00'
          document.getElementById('seconds').innerHTML = '00'
          return
        }
        document.getElementById('days').innerHTML = Math.floor(diff / 86400000).toString().padStart(2, '0')
        document.getElementById('hours').innerHTML = Math.floor((diff % 86400000) / 3600000).toString().padStart(2, '0')
        document.getElementById('minutes').innerHTML = Math.floor((diff % 3600000) / 60000).toString().padStart(2, '0')
        document.getElementById('seconds').innerHTML = Math.floor((diff % 60000) / 1000).toString().padStart(2, '0')
      }
      updateCountdown()
      setInterval(updateCountdown, 1000)
    },

    typewriterEffect() {
      const text = 'TravelEasy'
      const element = document.getElementById('typewriter')
      let i = 0
      const typing = setInterval(() => {
        if (i < text.length) {
          element.innerHTML += text.charAt(i)
          i++
        } else {
          clearInterval(typing)
        }
      }, 150)
    },

    closeTourCard() { this.showTourCard = false; this.selectedCity = null },
    logout() { localStorage.removeItem('token'); localStorage.removeItem('user'); window.location.reload() 
    },
    applyPromoCode() {
      const code = this.promoInput.trim().toUpperCase()
      if (this.validPromoCodes[code]) {
        this.discountPercent = this.validPromoCodes[code]
        this.discountAmount = Math.round(this.totalPrice * this.discountPercent / 100)
        this.finalPrice = this.totalPrice - this.discountAmount
        this.savedAmount = this.discountAmount
        this.promoSuccess = true
        this.promoMessage = `✅ Промокод применён! Скидка ${this.discountPercent}%`
        const promoSection = document.querySelector('.promo-section')
        if (promoSection) {
          promoSection.classList.add('promo-flash')
          setTimeout(() => promoSection.classList.remove('promo-flash'), 500)
        }
      } else {
        this.promoSuccess = false
        this.promoMessage = 'Неверный промокод.'
        this.discountPercent = 0
        this.discountAmount = 0
        this.finalPrice = this.totalPrice
        this.savedAmount = 0
      }
      setTimeout(() => { this.promoMessage = '' }, 3000)
    }
  } 
}
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }
.tourism-app { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0a0a2a 0%, #1a1a4a 100%); min-height: 100vh; color: white; overflow-x: hidden; }

.hero-section { min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; position: relative; z-index: 1; }
.gradient-text { font-size: 72px; background: linear-gradient(135deg, #fff, #ffaa33); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; letter-spacing: -2px; }
.hero-subtitle { font-size: 24px; color: rgba(255,255,255,0.8); margin: 20px 0 40px; }

.timer-section { background: rgba(0,0,0,0.5); backdrop-filter: blur(10px); border-radius: 20px; padding: 20px; margin: 30px auto; max-width: 500px; border: 1px solid #ffaa33; }
.timer-title { color: #ffaa33; font-weight: bold; margin-bottom: 15px; }
.countdown { display: flex; justify-content: center; gap: 20px; }
.countdown-number { display: block; font-size: 32px; font-weight: bold; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 10px; min-width: 60px; }
.timer-offer { margin-top: 15px; color: #ffaa33; font-weight: bold; animation: pulse 1s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.6; } }

.hero-stats { display: flex; justify-content: center; gap: 60px; margin-top: 40px; flex-wrap: wrap; }
.stat-number { font-size: 42px; font-weight: bold; color: #ffaa33; }
.stat-label { font-size: 14px; color: rgba(255,255,255,0.7); }

.filters-drawer { position: fixed; top: 100px; left: 0; z-index: 250; display: flex; align-items: stretch; }
.filters-tab { background: rgba(0,0,0,0.8); backdrop-filter: blur(8px); padding: 16px 8px; border-radius: 0 20px 20px 0; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 8px; border: 1px solid rgba(255,170,51,0.3); border-left: none; height: 120px; justify-content: center; }
.tab-icon { font-size: 24px; }
.tab-text { font-size: 14px; font-weight: bold; color: white; writing-mode: vertical-rl; text-orientation: mixed; }
.filters-panel { position: relative; left: 0; width: 480px; background: rgba(0,0,0,0.95); backdrop-filter: blur(12px); border-radius: 0 16px 16px 0; padding: 20px; color: white; transition: all 0.3s ease; opacity: 0; transform: translateX(-100%); pointer-events: none; border-right: 3px solid #ffaa33; }
.filters-panel.filters-visible { opacity: 1; transform: translateX(0); pointer-events: auto; }
.filter-group { margin-bottom: 20px; }
.filter-group label { display: block; margin-bottom: 8px; font-size: 14px; font-weight: bold; color: #ddd; }
.price-range, .duration-range { display: flex; gap: 10px; align-items: center; }
.price-range input, .duration-range input { flex: 1; padding: 8px 10px; border-radius: 6px; background: rgba(255,255,255,0.15); color: white; text-align: center; }
select { width: 100%; padding: 8px 10px; border-radius: 6px; background: rgba(255,255,255,0.15); color: white; }
.rating-buttons, .type-buttons, .stars-buttons { display: flex; flex-wrap: wrap; gap: 8px; }
.filter-btn { padding: 6px 12px; border-radius: 20px; background: rgba(255,255,255,0.2); color: white; cursor: pointer; }
.filter-btn.active { background: #ffaa33; color: black; }
.filter-clear { padding: 6px 12px; border-radius: 20px; background: rgba(255,255,255,0.1); color: #aaa; cursor: pointer; }
.checkbox-label { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.apply-btn, .reset-btn { width: 100%; padding: 10px; margin-top: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; }
.apply-btn { background: #4CAF50; color: white; }
.reset-btn { background: #ffaa33; color: black; }

.game-section { padding: 60px 20px; text-align: center; background: rgba(0,0,0,0.3); margin: 40px 0; }
.section-header h2 { font-size: 36px; margin-bottom: 15px; background: linear-gradient(135deg, #fff, #ffaa33); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.souvenirs { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; margin: 30px 0; }
.souvenir { text-align: center; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 15px; cursor: pointer; transition: all 0.3s; }
.souvenir:hover { transform: scale(1.1); background: rgba(255,170,51,0.3); }
.souvenir.collected { opacity: 0.5; filter: grayscale(1); cursor: default; }
.souvenir-icon { font-size: 48px; display: block; }
.promo-code { background: linear-gradient(135deg, #ffaa33, #ff8844); color: #1a1a2a; padding: 15px; border-radius: 30px; font-weight: bold; margin-top: 20px; display: inline-block; }

.globe-section { padding: 60px 20px; position: relative; z-index: 1; }
#globe-container { width: 100%; height: 600px; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.3); }

.auth-buttons { position: fixed; top: 20px; right: 20px; z-index: 200; display: flex; gap: 12px; }
.btn-login, .btn-register { padding: 10px 24px; border-radius: 30px; font-weight: 600; cursor: pointer; border: none; backdrop-filter: blur(10px); font-size: 14px; }
.btn-login { background: rgba(255,255,255,0.2); color: white; }
.btn-register { background: #ffaa33; color: #1a1a2a; }
.user-info-glass { background: rgba(0,0,0,0.5); backdrop-filter: blur(10px); padding: 8px 16px; border-radius: 40px; display: flex; align-items: center; gap: 12px; }
.profile-link, .logout-link { color: #ffaa33; text-decoration: none; font-size: 14px; padding: 4px 12px; border-radius: 20px; }
.admin-link-glass { position: fixed; bottom: 20px; left: 20px; z-index: 200; background: rgba(0,0,0,0.5); padding: 8px 16px; border-radius: 30px; }
.admin-link-glass a { color: #ffaa33; text-decoration: none; }

.footer { background: rgba(0,0,0,0.6); backdrop-filter: blur(10px); padding: 40px 20px 20px; margin-top: 40px; }
.footer-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 30px; }
.footer-brand h3 { color: #ffaa33; }
.footer-links { display: flex; gap: 20px; flex-wrap: wrap; }
.footer-links a, .footer-social a { color: rgba(255,255,255,0.7); text-decoration: none; }
.footer-links a:hover, .footer-social a:hover { color: #ffaa33; }
.footer-bottom { text-align: center; padding-top: 30px; margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 12px; }

.tour-card-modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(8px); z-index: 1000; display: flex; justify-content: center; align-items: center; }
.glass-card { background: rgba(20,20,40,0.95); backdrop-filter: blur(20px); border-radius: 30px; border: 1px solid rgba(255,170,51,0.3); }
.tour-card { padding: 30px; width: 500px; max-width: 90%; max-height: 90%; overflow-y: auto; position: relative; }
.close-btn { position: absolute; top: 15px; right: 20px; background: none; border: none; color: #ffaa33; font-size: 28px; cursor: pointer; }
.detail-item { display: flex; gap: 10px; margin: 10px 0; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 10px; }
.booking-form h3 { margin: 20px 0 15px; color: #ffaa33; }
.form-row { margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; gap: 15px; }
.form-row input, .form-row select { flex: 2; padding: 10px; border-radius: 10px; border: none; background: rgba(255,255,255,0.1); color: white; }
.total-price { display: flex; justify-content: space-between; background: rgba(255,170,51,0.2); padding: 15px; border-radius: 15px; margin: 15px 0; }
.total-price .price { color: #ffaa33; font-size: 24px; font-weight: bold; }
.book-btn { width: 100%; padding: 12px; background: linear-gradient(135deg, #ffaa33, #ff8844); border: none; border-radius: 30px; font-weight: bold; cursor: pointer; transition: transform 0.3s; }
.book-btn:hover { transform: scale(1.02); }
/* Промокод секция */
.promo-section {
  margin: 15px 0;
  border-top: 1px dashed rgba(255,170,51,0.3);
  padding-top: 12px;
}

.promo-header {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  background: rgba(255,170,51,0.1);
  border-radius: 10px;
  transition: all 0.3s;
}

.promo-header:hover {
  background: rgba(255,170,51,0.2);
}

.promo-icon { font-size: 18px; }
.promo-label { flex: 1; font-size: 14px; color: #ffaa33; }
.promo-toggle { font-size: 12px; color: #ffaa33; }

.promo-input {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.promo-input.promo-visible {
  max-height: 80px;
}

.promo-input input {
  flex: 2;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255,170,51,0.5);
  background: rgba(255,255,255,0.1);
  color: white;
}

.apply-promo-btn {
  flex: 1;
  padding: 8px 12px;
  background: #ffaa33;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.apply-promo-btn:hover {
  background: #ffcc44;
  transform: scale(1.02);
}

.promo-message {
  margin-top: 8px;
  font-size: 12px;
  text-align: center;
  padding: 5px;
  border-radius: 8px;
}

.promo-success {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.promo-error {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

/* Разбивка цены */
.price-breakdown {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 12px;
  margin: 15px 0;
}

.price-row {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  font-size: 14px;
}

.discount-row {
  color: #4CAF50;
}

.total-row {
  border-top: 1px solid rgba(255,255,255,0.2);
  padding-top: 8px;
  margin-top: 8px;
  font-size: 16px;
  font-weight: bold;
}

.final-price {
  color: #ffaa33;
  font-size: 20px;
}

.saved-badge {
  background: rgba(76, 175, 80, 0.2);
  text-align: center;
  padding: 6px;
  border-radius: 20px;
  font-size: 12px;
  color: #4CAF50;
  margin-top: 8px;
}

/* Анимация промокода */
@keyframes promoFlash {
  0% { background: rgba(255,170,51,0); }
  50% { background: rgba(255,170,51,0.4); }
  100% { background: rgba(255,170,51,0); }
}

.promo-flash {
  animation: promoFlash 0.5s ease;
}
/* Контейнер для глобуса и фильтров */
.globe-wrapper {
  position: relative;
  margin: 40px 20px;
}

/* Фильтры привязаны к глобусу */
.filters-drawer {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
  display: flex;
  align-items: stretch;
}

.filters-tab {
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  padding: 16px 8px;
  border-radius: 15px 0 0 15px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(255, 170, 51, 0.4);
  border-right: none;
  height: 100px;
  justify-content: center;
  transition: all 0.3s;
}

.filters-tab:hover {
  background: rgba(0, 0, 0, 0.95);
  transform: scale(1.02);
}

.tab-icon {
  font-size: 22px;
}

.tab-text {
  font-size: 12px;
  font-weight: bold;
  color: white;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  letter-spacing: 2px;
}

.filters-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 480px;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(16px);
  border-radius: 16px 0 0 16px;
  padding: 20px;
  color: white;
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateX(100%);
  pointer-events: none;
  border-left: 3px solid #ffaa33;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
}

.filters-panel.filters-visible {
  opacity: 1;
  transform: translateX(0);
  pointer-events: auto;
}

@media (max-width: 768px) {
  .filters-panel {
    width: 260px;
    padding: 15px;
  }
  .filters-tab {
    height: 80px;
    padding: 12px 6px;
  }
  .tab-icon {
    font-size: 18px;
  }
  .tab-text {
    font-size: 10px;
  }
}
</style>

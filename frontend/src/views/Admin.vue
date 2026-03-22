<template>
  <div class="admin-panel">
    <h2>🛠️ Админ-панель</h2>
    <p>Управление направлениями</p>
    
    <div class="admin-section">
      <h3>➕ Добавить новое направление</h3>
      
      <div class="form-group">
        <input v-model="form.name" placeholder="Название города">
        <input v-model="form.country" placeholder="Страна">
        <input v-model="form.price" type="number" placeholder="Цена (в евро)">
        <input v-model="form.duration_days" type="number" placeholder="Длительность (дни)">
        <input v-model="form.latitude" type="number" step="any" placeholder="Широта">
        <input v-model="form.longitude" type="number" step="any" placeholder="Долгота">
        <input v-model="form.rating" type="number" step="0.1" placeholder="Рейтинг (1-5)">
        
        <select v-model="form.tour_type">
          <option value="Экскурсионный">Экскурсионный</option>
          <option value="Пляжный">Пляжный</option>
          <option value="Горнолыжный">Горнолыжный</option>
          <option value="Гастрономический">Гастрономический</option>
          <option value="Приключенческий">Приключенческий</option>
        </select>
        
        <select v-model="form.hotel_stars">
          <option value="3">3★</option>
          <option value="4">4★</option>
          <option value="5">5★</option>
        </select>
        
        <label class="checkbox">
          <input type="checkbox" v-model="form.transfer"> Трансфер включён
        </label>
        
        <button @click="saveDestination" class="save-btn">💾 Сохранить</button>
      </div>
      
      <h3>📋 Существующие направления</h3>
      <div v-for="city in cities" :key="city.id" class="city-item">
        <strong>{{ city.name }}</strong> ({{ city.country }}) - {{ city.price }} ₽
        <span class="city-badge">⭐ {{ city.rating || 4.5 }} | 🏨 {{ city.hotel_stars || 3 }}★</span>
        <button @click="editCity(city)" class="edit-btn">✏️</button>
      </div>
      
      <router-link to="/" class="back-link">← Вернуться на главную</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminPage',
  data() {
    return {
      cities: [],
      form: {
        id: null,
        name: '',
        country: '',
        price: '',
        duration_days: '',
        latitude: '',
        longitude: '',
        rating: 4.5,
        tour_type: 'Экскурсионный',
        hotel_stars: 3,
        transfer: false
      }
    }
  },
  async mounted() {
    await this.loadCities()
  },
  methods: {
    async loadCities() {
      try {
        const res = await fetch('/api/destinations/coordinates')
        this.cities = await res.json()
      } catch (error) {
        console.error('Ошибка загрузки:', error)
      }
    },
    editCity(city) {
      this.form = { 
        ...city, 
        price: parseInt(city.price) / 50,
        id: city.id
      }
    },
    async saveDestination() {
      alert('Функция сохранения в разработке. Для добавления городов используйте pgAdmin.')
    }
  }
}
</script>

<style scoped>
.admin-panel {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #1a1a2e;
  color: white;
  padding: 80px 20px 20px;
  overflow-y: auto;
  z-index: 1000;
}

.admin-panel h2 {
  color: #ffaa33;
  margin-bottom: 10px;
}

.admin-section {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 30px;
  background: rgba(255,255,255,0.1);
  padding: 20px;
  border-radius: 12px;
}

input, select {
  padding: 10px;
  border-radius: 6px;
  border: none;
  background: rgba(255,255,255,0.9);
  font-size: 14px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #ddd;
}

.save-btn {
  padding: 12px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
}

.save-btn:hover {
  background: #45a049;
}

.city-item {
  background: rgba(255,255,255,0.1);
  padding: 12px;
  margin: 8px 0;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.city-badge {
  font-size: 12px;
  background: rgba(255,170,51,0.3);
  padding: 4px 8px;
  border-radius: 12px;
}

.edit-btn {
  background: #ffaa33;
  color: black;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.back-link {
  display: inline-block;
  margin-top: 20px;
  color: #ffaa33;
  text-decoration: none;
}
</style>
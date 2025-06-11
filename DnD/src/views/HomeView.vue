<template>
  <div class="home">
    <div class="home-content">
      <!-- Leva strana -->
      <div class="left-side">
        <div class="content">
          <h1>Create D&D characters and enjoy the game!</h1>
          <p>Create your D&D 5E character quickly and easily with automatic stat calculation and simple option selection. <a href="/register" class="register-link">Register</a> now and start creating your characters!</p>
        </div>
      </div>
      
      <!-- Desna strana -->
      <div class="right-side">
        <div class="carousel-container">
          <ImageCarousel />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ImageCarousel from '@/components/ImageCarousel.vue';

export default {
  name: 'HomeView',
  components: {
    ImageCarousel
  },
  setup() {
    return {};
  }
};
</script>

<style scoped>
.home {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.home-content {
  display: flex;
  gap: 40px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  align-items: center;
  flex-wrap: wrap;
}

.left-side {
  flex: 1;
  min-width: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.right-side {
  flex: 0.8;
  min-width: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.content {
  text-align: center;
  color: gold;
  background-color: rgba(0, 0, 0, 0.4);
  padding: 2.5rem;
  border-radius: 50px;
  width: 100%;
  max-width: 600px;
}

.carousel-container {
  width: 100%;
  max-width: 500px;
}

h1 {
  font-size: clamp(1.5rem, 4vw, 3rem);
  margin-bottom: 20px;
}

p {
  font-size: clamp(1rem, 2vw, 1.5rem);
  margin-bottom: 20px;
}

.register-link {
  color: gold;
  text-decoration: none;
  border-bottom: 1px dashed gold;
  transition: all 0.3s ease;
  font-weight: bold;
}

.register-link:hover {
  color: #ffd700;
  border-bottom: 1px solid gold;
  text-shadow: 0 0 5px rgba(218, 165, 32, 0.5);
}

@media (max-width: 768px) {
  .home-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .left-side, .right-side {
    width: 100%;
  }
  
  .content {
    padding: 1.5rem;
  }
}
</style>
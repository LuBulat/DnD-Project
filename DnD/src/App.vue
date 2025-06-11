<template>
  <div class="app-container">
    <header>
      <nav class="navbar">
        <!-- Levi deo - linkovi -->
        <div class="navbar-left">
          <RouterLink to="/races" class="nav-link">Races</RouterLink>
          <RouterLink to="/classes" class="nav-link">Classes</RouterLink>
          <RouterLink to="/spells" class="nav-link">Spells</RouterLink>
          <RouterLink to="/backgrounds" class="nav-link">Backgrounds</RouterLink>
        </div>
        
        <!-- Srednji deo - logo -->
        <div class="navbar-center">
          <RouterLink to="/">
            <img alt="Vue logo" class="logo" src="@/assets/logo2.png"/>
          </RouterLink>
        </div>
        
        <!-- Desni deo - login i dashboard (ako je ulogovan) -->
        <div class="navbar-right">
          <LoginButton />
          <RouterLink v-if="isLoggedIn" to="/dashboard" class="dashboard-link">
            <img alt="D20 dice" class="d20" src="@/assets/d20.png"/>
          </RouterLink>
        </div>
      </nav>
    </header>
    <RouterView />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import LoginButton from "@/components/LoginButton.vue";

const isLoggedIn = ref(false);
const route = useRoute();

// Provera da li je korisnik ulogovan
const checkLoginStatus = () => {
  isLoggedIn.value = localStorage.getItem('isLoggedIn') === 'true';
};

// Inicijalna provera
onMounted(() => {
  checkLoginStatus();
});

// Praćenje promene rute
watch(route, () => {
  checkLoginStatus();
});

// Osvežavanje statusa nakon logina/logouta
const handleLoginStatusChange = () => {
  checkLoginStatus();
};

// Dodajemo event listener na window objekat
onMounted(() => {
  window.addEventListener('login-status-changed', handleLoginStatusChange);
});
</script>

<style scoped>
.app-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  width: 100%;
}

header {
  width: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0.5rem 1rem;
  max-width: 1800px;
  margin: 0 auto;
  position: relative;
}

.navbar-left {
  display: flex;
  gap: 1rem;
  text-align: left;
  flex: 1;
  justify-content: flex-start;
}

.navbar-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
}

.navbar-right {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex: 1;
  justify-content: flex-end;
}

.nav-link {
  font-size: clamp(1rem, 2vw, 2rem);
  text-decoration: none;
  color: silver;
  transition: all 0.3s ease;
  padding: 0.5rem;
  white-space: nowrap;
}

.nav-link:hover {
  color: gold;
}

.nav-link.router-link-active {
  color: gold;
}

.logo {
  width: clamp(40px, 5vw, 50px);
  height: clamp(40px, 5vw, 50px);
  transition: all 1s ease;
  display: block;
}

.d20 {
  width: clamp(60px, 8vw, 100px);
  height: clamp(24px, 4vw, 40px);
  transition: all 1s ease;
}

.logo:hover, .d20:hover {
  filter: drop-shadow(0 0 8px gold);
}

.dashboard-link {
  display: flex;
  align-items: center;
  margin-left: 10px;
}

/* Media queries za bolju responzivnost */
@media screen and (max-width: 1200px) {
  .navbar {
    padding: 0.5rem;
  }
  
  .navbar-left {
    justify-content: center;
  }
  
  .navbar-right {
    justify-content: center;
  }
}

@media screen and (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .navbar-center {
    position: relative;
    left: 0;
    transform: none;
    order: 1;
  }
  
  .navbar-left {
    order: 2;
    width: 100%;
    justify-content: center;
  }
  
  .navbar-right {
    order: 3;
    width: 100%;
    justify-content: center;
  }
  
  .nav-link {
    font-size: clamp(0.9rem, 1.5vw, 1.5rem);
  }
}

/* Add styles for the router view to take up 90% of the page */
:deep(.router-view) {
  flex: 1;
  height: 90vh;
  overflow-y: auto;
}
</style>
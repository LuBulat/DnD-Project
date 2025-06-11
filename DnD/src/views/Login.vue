<template>
  <!-- Notification -->
  <Transition name="slide-fade">
    <div v-if="showNotification" :class="['notification', notificationType]">
      {{ notificationMessage }}
    </div>
  </Transition>

  <div class="form-container">
    <form @submit.prevent="login" novalidate>
      <div class="input-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="input-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const BASE_URL = "http://localhost:5000";  // Globalna promenljiva za API URL

const username = ref("");
const password = ref("");
const router = useRouter();

const isLoggedIn = ref(localStorage.getItem("isLoggedIn") === "true");

// Za notifikacije
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('success')

// Funkcija za prikazivanje uspešne notifikacije
const showSuccessNotification = (message) => {
  notificationMessage.value = message
  notificationType.value = 'success'
  showNotification.value = true
  setTimeout(() => {
    showNotification.value = false
  }, 3000)
}

// Funkcija za prikazivanje error notifikacije
const showErrorNotification = (message) => {
  notificationMessage.value = message
  notificationType.value = 'error'
  showNotification.value = true
  setTimeout(() => {
    showNotification.value = false
  }, 3000)
}

const login = async () => {
  // Provera obaveznih polja
  let isValid = true

  // Provera username polja
  if (!username.value.trim()) {
    const usernameInput = document.getElementById('username')
    usernameInput.classList.add('invalid-input')
    setTimeout(() => {
      usernameInput.classList.remove('invalid-input')
    }, 3000)
    isValid = false
    showErrorNotification('Please enter a username')
    return
  }

  // Provera password polja
  if (!password.value.trim()) {
    const passwordInput = document.getElementById('password')
    passwordInput.classList.add('invalid-input')
    setTimeout(() => {
      passwordInput.classList.remove('invalid-input')
    }, 3000)
    isValid = false
    showErrorNotification('Please enter a password')
    return
  }

  // Ako neko polje nije validno, prekini izvršavanje funkcije
  if (!isValid) return

  try {
    const response = await axios.post(
      `${BASE_URL}/api/login`,
      {
        username: username.value,
        password: password.value,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (response.status === 200) {
      const token = response.data.access_token;
      console.log("Received token:", token);
      
      // Sačuvaj token bez modifikacija
      localStorage.setItem("token", token);
      localStorage.setItem("isLoggedIn", "true");
      
      // Konfiguriši axios default autorization header za buduće zahteve
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      isLoggedIn.value = true;
      showSuccessNotification("Login successful!");
      setTimeout(() => {
        router.push("/dashboard");  // Preusmerenje na dashboard
      }, 2000);
    }
  } catch (error) {
    console.error("Login error:", error);
    
    // Prikazujemo različite poruke u zavisnosti od greške
    if (error.response) {
      // Ako server vraća odgovor sa status kodom van 2xx
      if (error.response.status === 401) {
        showErrorNotification("Username and password do not match");
      } else if (error.response.status === 404) {
        showErrorNotification("User not found");
      } else {
        // Ostale greške
        showErrorNotification("Login failed: " + (error.response.data.message || "Server error"));
      }
    } else if (error.request) {
      // Zahtev je poslat ali nema odgovora
      showErrorNotification("No response from server. Please try again later");
    } else {
      // Greška pri pripremi zahteva
      showErrorNotification("Error sending request");
    }
  }
};
</script>
  
<style scoped>
  @import "@/assets/form.css";
</style>
<template>
  <!-- Notification -->
  <Transition name="slide-fade">
    <div v-if="showNotification" :class="['notification', notificationType]">
      {{ notificationMessage }}
    </div>
  </Transition>

  <div class="form-container">
    <form @submit.prevent="register" novalidate>
      <div class="input-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="input-group">
        <label for="email">Email</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <div class="input-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Register</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../axios'
import { useRouter } from 'vue-router'

const username = ref('')
const email = ref('')
const password = ref('')
const router = useRouter()

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

const register = async () => {
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

  // Provera email polja
  if (!email.value.trim()) {
    const emailInput = document.getElementById('email')
    emailInput.classList.add('invalid-input')
    setTimeout(() => {
      emailInput.classList.remove('invalid-input')
    }, 3000)
    isValid = false
    showErrorNotification('Please enter an email address')
    return
  }

  // Provera da li je email u ispravnom formatu
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value.trim())) {
    const emailInput = document.getElementById('email')
    emailInput.classList.add('invalid-input')
    setTimeout(() => {
      emailInput.classList.remove('invalid-input')
    }, 3000)
    isValid = false
    showErrorNotification('Please enter a valid email address')
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
    const response = await api.post('/register', {
      username: username.value,
      email: email.value,
      password: password.value
    })

    if (response.status === 200) {
      showSuccessNotification('Registration successful!')
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    }
  } catch (error) {
    console.error(error)
    // Prikazujemo različite poruke u zavisnosti od greške
    if (error.response) {
      // Ako server vraća odgovor sa status kodom van 2xx
      if (error.response.status === 409) {
        // Kod 409 obično označava konflikt - korisničko ime ili email već postoji
        if (error.response.data && error.response.data.message) {
          showErrorNotification(error.response.data.message)
        } else if (error.response.data && error.response.data.includes('username')) {
          showErrorNotification('Username already taken')
        } else if (error.response.data && error.response.data.includes('email')) {
          showErrorNotification('Email already registered')
        } else {
          showErrorNotification('Username or email already exists')
        }
      } else {
        // Ostale greške
        showErrorNotification('Registration failed: ' + (error.response.data.message || 'Server error'))
      }
    } else if (error.request) {
      // Zahtev je poslat ali nema odgovora
      showErrorNotification('No response from server. Please try again later')
    } else {
      // Greška pri pripremi zahteva
      showErrorNotification('Error sending request')
    }
  }
}
</script>

<style scoped>
  @import "@/assets/form.css";
</style>
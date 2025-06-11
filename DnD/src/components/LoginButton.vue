<template>
  <div>
    <!-- Notification -->
    <Transition name="slide-fade">
      <div v-if="showNotification" :class="['notification', notificationType]">
        {{ notificationMessage }}
      </div>
    </Transition>

    <!-- Logout Confirmation Modal -->
    <div class="modal" v-if="showLogoutModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Confirm Logout</h3>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to logout?</p>
        </div>
        <div class="modal-buttons">
          <button class="cancel-btn" @click="showLogoutModal = false">Cancel</button>
          <button class="delete-btn" @click="confirmLogout">Logout</button>
        </div>
      </div>
    </div>

    <button v-if="!isLoggedIn && !isOnLoginPage" @click="goToLogin">Login</button>
    <button v-else-if="!isLoggedIn && isOnLoginPage" @click="goToRegister">Register</button>
    <button v-else @click="showLogoutConfirmation">Logout</button>
  </div>
</template>

<script>
import api from '../axios';

export default {
  name: "LoginButton",
  data() {
    return {
      isLoggedIn: false,
      isOnLoginPage: false,
      showLogoutModal: false,
      // Za notifikacije
      showNotification: false,
      notificationMessage: '',
      notificationType: 'success',
    };
  },
  async created() {
    await this.checkSession();
    this.checkIfOnLoginPage();
  },
  methods: {
    // Funkcija za prikazivanje uspešne notifikacije
    showSuccessNotification(message) {
      this.notificationMessage = message;
      this.notificationType = 'success';
      this.showNotification = true;
      setTimeout(() => {
        this.showNotification = false;
      }, 3000);
    },
    
    // Funkcija za prikazivanje error notifikacije
    showErrorNotification(message) {
      this.notificationMessage = message;
      this.notificationType = 'error';
      this.showNotification = true;
      setTimeout(() => {
        this.showNotification = false;
      }, 3000);
    },

    async checkSession() {
      const token = localStorage.getItem("token");
      
      console.log("Token from localStorage:", token);

      if (!token) {
        this.isLoggedIn = false;
        return;
      }
      
      try {
        const response = await api.get("/check_session");

        if (response.status === 200 && response.data.loggedIn) {
          this.isLoggedIn = true;
        } else {
          this.isLoggedIn = false;
        }
      } catch (error) {
        console.log("Error in checkSession:", error);
        if (error.response) {
          console.log("Status:", error.response.status);
          console.log("Data:", error.response.data);
        }
        // If token is invalid, clear it
        if (error.response && (error.response.status === 401 || error.response.status === 422)) {
          localStorage.removeItem("token");
          localStorage.setItem("isLoggedIn", "false");
        }
        this.isLoggedIn = false;
      }
    },

    checkIfOnLoginPage() {
      this.isOnLoginPage = this.$route.path === '/login';
    },

    goToLogin() {
      this.$router.push("/login");
    },

    goToRegister() {
      this.$router.push("/register");
    },

    showLogoutConfirmation() {
      this.showLogoutModal = true;
    },

    async confirmLogout() {
      this.showLogoutModal = false;
      try {
        await api.post("/logout");
      } catch (error) {
        console.log("Logout error:", error);
      } finally {
        localStorage.removeItem("token");
        localStorage.setItem("isLoggedIn", "false");
        this.isLoggedIn = false;
        this.showSuccessNotification("Logout successful!");
        setTimeout(() => {
          this.$router.push("/login");
        }, 2000);
      }
    },

    async logout() {
      try {
        await api.post("/logout");
      } catch (error) {
        console.log("Logout error:", error);
      } finally {
        localStorage.removeItem("token");
        localStorage.setItem("isLoggedIn", "false");
        this.isLoggedIn = false;
        this.showSuccessNotification("Logout successful!");
        setTimeout(() => {
          this.$router.push("/login");
        }, 2000);
      }
    },
  },
  watch: {
    '$route'(to, from) {
      this.checkSession();
      this.checkIfOnLoginPage();
    },
  },
};
</script>

<style scoped>
button {
  border: none;
  font-size: 2rem;
  margin: 5px;
  color: silver;
  transition: all 0.3s ease;
  background-color: transparent;
}

button:hover {
  background-color: rgb(0, 0, 0, 0);
  color: gold;
}

/* Stilovi za notifikacije */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 8px;
  color: white;
  font-size: 1.2rem;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  text-align: center;
}

.notification.success {
  background: linear-gradient(to right, #2ecc71, #27ae60);
  border: 2px solid #27ae60;
}

.notification.error {
  background: linear-gradient(to right, #e74c3c, #c0392b);
  border: 2px solid #c0392b;
}

/* Animacije za notifikacije */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(30px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(30px);
  opacity: 0;
}

/* Stilovi za modal */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
  backdrop-filter: blur(4px);
}

.modal-content {
  max-width: 500px;
  width: 90%;
  background: linear-gradient(to bottom, #2c2c2c, #1a1a1a);
  border: 2px solid gold;
  border-radius: 8px;
  box-shadow: 0 0 30px rgba(218, 165, 32, 0.6);
  overflow: hidden;
  animation: modalAppear 0.3s ease-out forwards;
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  background: linear-gradient(to right, rgba(218, 165, 32, 0.3), rgba(218, 165, 32, 0.1));
  padding: 15px 20px;
  border-bottom: 1px solid gold;
  text-align: center;
}

.modal-header h3 {
  color: gold;
  font-size: 2rem;
  text-shadow: 0 0 5px rgba(218, 165, 32, 0.5);
  margin: 0;
}

.modal-body {
  padding: 20px;
  margin-bottom: 0;
  text-align: center;
}

.modal-body p {
  color: silver;
  font-size: 1.5rem;
  line-height: 1.5;
  margin: 0;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 0 20px 20px 20px;
}

.cancel-btn, .delete-btn {
  transition: all 0.3s ease;
  cursor: pointer;
}

.cancel-btn {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.2), rgba(192, 192, 192, 0.1));
  color: gold;
  border: 2px solid silver;
  padding: 8px 15px;
  border-radius: 4px;
  font-size: 1.2rem;
  margin-right: 10px;
}

.cancel-btn:hover {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.3), rgba(192, 192, 192, 0.2));
  box-shadow: 0 0 20px gold;
  transform: translateY(-2px);
}

.delete-btn {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.2), rgba(192, 192, 192, 0.1));
  color: gold;
  border: 2px solid silver;
  padding: 8px 15px;
  border-radius: 4px;
  font-size: 1.2rem;
}

.delete-btn:hover {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.3), rgba(192, 192, 192, 0.2));
  box-shadow: 0 0 20px gold;
  transform: translateY(-2px);
}
</style>
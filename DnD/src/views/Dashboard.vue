<template>
  <div class="dashboard">
    <h1 class="welcome-title">Welcome, {{ username }}!</h1>
    
    <div class="item-button-container">
      <div class="description-container" v-if="characters.length > 0">
        <h2>Your Characters</h2>
        <div class="character-list">
          <div class="character-item" v-for="character in characters" :key="character.id">
            <span class="character-name" @click="openCharacterSheet(character.id)">{{ formatName(character.name) }}</span>
            <button class="delete-btn" @click="confirmDelete(character)">Delete</button>
          </div>
        </div>
        
        <div class="buttons-container">
          <button class="create-btn" @click="createNewCharacter">Create New Character</button>
          <button class="edit-profile-btn" @click="showEditProfileModal = true">Edit Profile</button>
          <button class="delete-account-btn" @click="confirmDeleteAccount">Delete Account</button>
        </div>
      </div>
      
      <div class="description-container" v-else>
        <p>You don't have any characters yet.</p>
        
        <div class="buttons-container">
          <button class="create-btn" @click="createNewCharacter">Create New Character</button>
          <button class="edit-profile-btn" @click="showEditProfileModal = true">Edit Profile</button>
          <button class="delete-account-btn" @click="confirmDeleteAccount">Delete Account</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal" v-if="showDeleteModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Confirm Delete</h3>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete this character?</p>
        </div>
        <div class="modal-buttons">
          <button class="cancel-btn" @click="showDeleteModal = false">Cancel</button>
          <button class="delete-btn" @click="deleteCharacter">Delete</button>
        </div>
      </div>
    </div>
    
    <!-- Delete Account Confirmation Modal -->
    <div class="modal" v-if="showDeleteAccountModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Delete Account</h3>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete your account? This action cannot be undone and will delete all your characters.</p>
        </div>
        <div class="modal-buttons">
          <button class="cancel-btn" @click="showDeleteAccountModal = false">Cancel</button>
          <button class="delete-btn" @click="deleteAccount">Delete Permanently</button>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div class="modal" v-if="showEditProfileModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Edit Profile</h3>
        </div>
        <div class="modal-body">
          <div class="edit-section">
            <h4>Change Username</h4>
            <div class="form-group">
              <label for="new-username">New Username:</label>
              <input type="text" id="new-username" v-model="newUsername" />
            </div>
            <div class="error-message" v-if="usernameError">{{ usernameError }}</div>
            <button class="update-btn" @click="updateUsername">Update Username</button>
            <div class="success-message" v-if="usernameSuccess">{{ usernameSuccess }}</div>
          </div>
          
          <div class="edit-section">
            <h4>Change Password</h4>
            <div class="form-group">
              <label for="current-password">Current Password:</label>
              <input type="password" id="current-password" v-model="currentPassword" />
            </div>
            <div class="form-group">
              <label for="new-password">New Password:</label>
              <input type="password" id="new-password" v-model="newPassword" />
            </div>
            <div class="form-group">
              <label for="confirm-password">Confirm New Password:</label>
              <input type="password" id="confirm-password" v-model="confirmPassword" />
            </div>
            <div class="error-message" v-if="passwordError">{{ passwordError }}</div>
            <button class="update-btn" @click="updatePassword">Update Password</button>
            <div class="success-message" v-if="passwordSuccess">{{ passwordSuccess }}</div>
          </div>
        </div>
        <div class="modal-buttons">
          <button class="close-btn" @click="closeEditProfileModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const username = ref('')
const characters = ref([])
const showDeleteModal = ref(false)
const characterToDelete = ref(null)
const showDeleteAccountModal = ref(false)
const showEditProfileModal = ref(false)

// Edit profile variables
const newUsername = ref('')
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const usernameError = ref('')
const passwordError = ref('')
const usernameSuccess = ref('')
const passwordSuccess = ref('')

// Format name to have first letter of each word capitalized
const formatName = (name) => {
  return name.split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

// Navigate to character sheet
const openCharacterSheet = (characterId) => {
  router.push(`/character/${characterId}`)
}

// Create a new character
const createNewCharacter = () => {
  router.push('/characterSheet')
}

// Fetch dashboard data
const fetchDashboardData = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/dashboard', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    username.value = response.data.username
    characters.value = response.data.characters
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
  }
}

// Confirm delete dialog
const confirmDelete = (character) => {
  characterToDelete.value = character
  showDeleteModal.value = true
}

// Delete character
const deleteCharacter = async () => {
  if (!characterToDelete.value) return

  try {
    await axios.delete(`http://localhost:5000/api/characters/${characterToDelete.value.id}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    // Remove character from the list
    characters.value = characters.value.filter(char => char.id !== characterToDelete.value.id)
    
    // Close modal and reset
    showDeleteModal.value = false
    characterToDelete.value = null
  } catch (error) {
    console.error('Error deleting character:', error)
  }
}

// Confirm delete account dialog
const confirmDeleteAccount = () => {
  showDeleteAccountModal.value = true
}

// Delete account
const deleteAccount = async () => {
  try {
    // Get user ID from the JWT token identity using the check_session endpoint
    const response = await axios.get('http://localhost:5000/api/check_session', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    // Call the delete user endpoint with the user ID
    await axios.delete(`http://localhost:5000/api/users/${response.data.user_id || ''}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    // Clear local storage
    localStorage.removeItem('token')
    localStorage.removeItem('isLoggedIn')
    
    // Redirect to login page
    router.push('/login')
  } catch (error) {
    console.error('Error deleting account:', error)
  }
}

// Close edit profile modal and reset fields
const closeEditProfileModal = () => {
  showEditProfileModal.value = false
  newUsername.value = ''
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  usernameError.value = ''
  passwordError.value = ''
  usernameSuccess.value = ''
  passwordSuccess.value = ''
}

// Update username
const updateUsername = async () => {
  usernameError.value = ''
  usernameSuccess.value = ''
  
  if (!newUsername.value.trim()) {
    usernameError.value = 'Username cannot be empty'
    return
  }
  
  try {
    const response = await axios.put('http://localhost:5000/api/update-username', 
      { username: newUsername.value },
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )
    
    usernameSuccess.value = 'Username updated successfully'
    username.value = newUsername.value
    setTimeout(() => {
      usernameSuccess.value = ''
    }, 3000)
  } catch (error) {
    if (error.response && error.response.data.message) {
      usernameError.value = error.response.data.message
    } else {
      usernameError.value = 'Failed to update username'
    }
    console.error('Error updating username:', error)
  }
}

// Update password
const updatePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''
  
  if (!currentPassword.value) {
    passwordError.value = 'Current password is required'
    return
  }
  
  if (!newPassword.value) {
    passwordError.value = 'New password is required'
    return
  }
  
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'New passwords do not match'
    return
  }
  
  try {
    const response = await axios.put('http://localhost:5000/api/update-password', 
      {
        currentPassword: currentPassword.value,
        newPassword: newPassword.value
      },
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )
    
    passwordSuccess.value = 'Password updated successfully'
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    setTimeout(() => {
      passwordSuccess.value = ''
    }, 3000)
  } catch (error) {
    if (error.response && error.response.data.message) {
      passwordError.value = error.response.data.message
    } else {
      passwordError.value = 'Failed to update password'
    }
    console.error('Error updating password:', error)
  }
}

// Fetch data when component mounts
onMounted(fetchDashboardData)
</script>

<style scoped>
.description-container {
  background-color: rgba(0, 0, 0, 0.5);
  border: 1px solid silver;
  border-radius: 8px;
  overflow: hidden;
  margin: 20px 0px;
  padding: 20px 40px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
}

.welcome-title {
  color: gold;
  font-size: 2.6rem;
  font-weight: bold;
  margin-bottom: 2rem;
  text-shadow: 0 0 5px rgba(218, 165, 32, 0.5);
  text-align: center;
}

.item-button-container {
  width: 60%;
  margin: 0 auto;
  text-align: center;
  padding: 10px 20px;
}

.character-list {
  background-color: rgba(0, 0, 0, 0.5);
  border: 1px solid silver;
  border-radius: 8px;
  overflow: hidden;
  margin: 20px 0px;
}

.character-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid silver;
  background-color: rgba(192, 192, 192, 0.1);
  transition: background-color 0.3s ease;
}

.character-item:last-child {
  border-bottom: none;
}

.character-item:hover {
  background-color: rgba(218, 165, 32, 0.2);
}

.character-name {
  font-size: 1.5rem;
  color: silver;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 5px 10px;
  border-radius: 4px;
}

.character-name:hover {
  color: gold;
  text-shadow: 0 0 5px rgba(218, 165, 32, 0.5);
}

.delete-btn {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.2), rgba(192, 192, 192, 0.1));
  color: gold;
  border: 2px solid silver;
  padding: 8px 15px;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-size: 1.2rem;
}

.delete-btn:hover {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.3), rgba(192, 192, 192, 0.2));
  box-shadow: 0 0 20px gold;
  transform: translateY(-2px);
}

.cancel-btn, .close-btn {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.2), rgba(192, 192, 192, 0.1));
  color: gold;
  border: 2px solid silver;
  padding: 8px 15px;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-size: 1.2rem;
  margin-right: 10px;
}

.cancel-btn:hover, .close-btn:hover {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.3), rgba(192, 192, 192, 0.2));
  box-shadow: 0 0 20px gold;
  transform: translateY(-2px);
}

.buttons-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(192, 192, 192, 0.3);
}

/* Zajednički stilovi za sva tri dugmeta */
.create-btn, .edit-profile-btn, .delete-account-btn {
  padding: 12px 24px;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-size: 1.3rem;
  font-weight: bold;
  color: white;
  text-align: center;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Hover efekti zajednički za sva dugmad */
.create-btn:hover, .edit-profile-btn:hover, .delete-account-btn:hover {
  box-shadow: 0 0 20px;
  transform: translateY(-3px);
}

/* Specifične boje za svako dugme */
.create-btn {
  background: linear-gradient(to right, rgba(218, 165, 32, 0.3), rgba(218, 165, 32, 0.2));
  border: 2px solid gold;
  /* text-transform: uppercase; */
  letter-spacing: 1px;
}

.create-btn:hover {
  background: linear-gradient(to right, rgba(218, 165, 32, 0.5), rgba(218, 165, 32, 0.4));
  box-shadow: 0 0 20px gold;
}

.edit-profile-btn {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.2), rgba(192, 192, 192, 0.1));
  color: gold;
  border: 2px solid silver;
}

.edit-profile-btn:hover {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.3), rgba(192, 192, 192, 0.2));
  box-shadow: 0 0 20px gold;
}

.delete-account-btn {
  background: linear-gradient(to right, rgba(139, 0, 0, 0.3), rgba(139, 0, 0, 0.2));
  color: #ff6b6b;
  border: 2px solid #800000;
}

.delete-account-btn:hover {
  background: linear-gradient(to right, rgba(139, 0, 0, 0.5), rgba(139, 0, 0, 0.4));
  box-shadow: 0 0 20px #ff6b6b;
}

.update-btn {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.2), rgba(192, 192, 192, 0.1));
  color: gold;
  border: 2px solid silver;
  padding: 8px 15px;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-size: 1.1rem;
  margin-top: 10px;
}

.update-btn:hover {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.3), rgba(192, 192, 192, 0.2));
  box-shadow: 0 0 20px gold;
  transform: translateY(-2px);
}

.error-message {
  color: #ff6b6b;
  font-size: 0.9rem;
  margin-top: 5px;
}

.success-message {
  color: #66ff66;
  font-size: 0.9rem;
  margin-top: 10px;
}

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
  z-index: 1000;
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
}

.modal-header h3 {
  color: gold;
  font-size: 2rem;
  text-shadow: 0 0 5px rgba(218, 165, 32, 0.5);
  margin: 0;
}

.modal-body {
  padding: 20px;
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

h2 {
  color: gold;
  margin-top: 10px;
  font-size: 2.3rem;
  text-shadow: 0 0 5px rgba(218, 165, 32, 0.5);
}

p {
  color: silver;
  font-size: 1.5rem;
  margin: 0;
}

/* Edit profile styles */
.edit-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(192, 192, 192, 0.3);
}

.edit-section:last-child {
  border-bottom: none;
}

.edit-section h4 {
  color: gold;
  font-size: 1.5rem;
  margin-bottom: 15px;
  text-shadow: 0 0 3px rgba(218, 165, 32, 0.4);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  color: silver;
  margin-bottom: 5px;
  font-size: 1.1rem;
}

.form-group input {
  width: 100%;
  padding: 10px;
  background-color: rgba(0, 0, 0, 0.3);
  border: 1px solid silver;
  border-radius: 4px;
  color: white;
  font-size: 1rem;
}
</style>
  
<template>
  <div v-if="show" class="confirmation-dialog-overlay">
    <div class="confirmation-dialog">
      <div class="confirmation-content">
        <div class="section-title">{{ title }}</div>
        <p>{{ message }}</p>
        <div class="confirmation-buttons">
          <button class="confirm-btn" @click="confirm">{{ confirmText }}</button>
          <button class="cancel-btn" @click="cancel">{{ cancelText }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmationDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Confirmation'
    },
    message: {
      type: String,
      required: true
    },
    confirmText: {
      type: String,
      default: 'Yes'
    },
    cancelText: {
      type: String,
      default: 'No'
    }
  },
  methods: {
    confirm() {
      this.$emit('confirm');
    },
    cancel() {
      this.$emit('cancel');
    }
  }
}
</script>

<style scoped>
.confirmation-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.confirmation-dialog {
  width: 90%;
  max-width: 450px;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  animation: dialogAppear 0.3s ease-out;
  border: 1px solid #ccc;
  border-top: 4px solid #4CAF50;
}

.section-title {
  font-size: 1.4rem;
  color: #333;
  text-align: center;
  margin-bottom: 15px;
  font-weight: bold;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.confirmation-content p {
  color: #333;
  font-size: 1.2em;
  text-align: center;
  margin-bottom: 20px;
  line-height: 1.5;
}

.confirmation-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.confirmation-buttons button {
  padding: 10px 25px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1.1em;
  min-width: 100px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.confirm-btn {
  background-color: #4CAF50;
  color: white;
  border: 1px solid #3d8b40;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
  border: 1px solid #d32f2f;
}

.confirm-btn:hover, .cancel-btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.confirm-btn:active, .cancel-btn:active {
  opacity: 1;
  transform: translateY(0);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

@keyframes dialogAppear {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 600px) {
  .confirmation-dialog {
    width: 95%;
    padding: 15px;
  }
  
  .confirmation-buttons {
    flex-direction: column;
    gap: 10px;
  }
  
  .confirmation-buttons button {
    width: 100%;
  }
}
</style> 
<template>
  <div class="half-elf-modal-overlay">
    <div class="half-elf-modal">
      <h2>Choose 2 abilities to increase by 1</h2>
      <div class="abilities-grid">
        <div v-for="ability in abilities" :key="ability.name" 
             class="ability-item"
             :class="{ 'selected': selectedAbilities.includes(ability.name) }"
             @click="toggleAbility(ability.name)">
          <span class="ability-name">{{ ability.name }}</span>
        </div>
      </div>
      <div class="modal-footer">
        <button class="confirm-btn" 
                @click="confirmSelection" 
                :disabled="selectedAbilities.length !== 2">
          Confirm Selection
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HalfElfAbilityScore',
  props: {
    abilities: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      selectedAbilities: []
    }
  },
  methods: {
    toggleAbility(abilityName) {
      const index = this.selectedAbilities.indexOf(abilityName);
      if (index === -1) {
        // Ako već nije izabran i imamo manje od 2 izabrana
        if (this.selectedAbilities.length < 2) {
          this.selectedAbilities.push(abilityName);
        }
      } else {
        // Ako je već izabran, ukloni ga
        this.selectedAbilities.splice(index, 1);
      }
    },
    confirmSelection() {
      if (this.selectedAbilities.length === 2) {
        this.$emit('abilities-selected', this.selectedAbilities);
      }
    }
  }
}
</script>

<style scoped>
.half-elf-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.half-elf-modal {
  background-color: white;
  padding: 20px;
  border: 3px solid #222;
  border-radius: 12px;
  min-width: 400px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.half-elf-modal h2 {
  font-size: 1.3em;
  font-weight: bold;
  text-transform: uppercase;
  color: #333;
  margin-bottom: 5px;
  padding-bottom: 4px;
  border-bottom: 2px solid #000;
  text-align: center;
}

.abilities-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin: 20px 0;
  padding: 20px;
  background: linear-gradient(to bottom, #f8f8f8, #f0f0f0);
  border-radius: 12px;
  border: 2px solid #222;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.ability-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.ability-item:hover {
  border-color: #555;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.ability-item.selected {
  background-color: #e0e0e0;
  border-color: #000;
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1);
}

.ability-name {
  font-weight: bold;
  font-size: 1.1em;
  color: #333;
  text-align: left;
  min-width: 120px;
}

.ability-score {
  font-weight: bold;
  font-size: 1.2em;
  color: #555;
  background-color: #f8f8f8;
  border-radius: 4px;
  padding: 2px 10px;
  border: 1px solid #e0e0e0;
}

.modal-footer {
  text-align: center;
  margin-top: 20px;
}

.confirm-btn {
  padding: 10px 25px;
  background: linear-gradient(to bottom, #fff, #f5f5f5);
  color: #333;
  border: 2px solid #666;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.confirm-btn:disabled {
  opacity: 0.5;
  background: #f0f0f0;
}

.confirm-btn:hover:not(:disabled) {
  background: linear-gradient(to bottom, #f5f5f5, #e8e8e8);
  color: #000;
  border-color: #000;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.confirm-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
}
</style> 
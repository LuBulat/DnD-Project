<template>
  <div class="ability-score-method-container">
    <div class="ability-score-method">
        <div class="section-title">Ability Score Method</div>
      <div class="ability-score-instructions">
        <p>Determine the ability scores for your character before proceeding further.</p>
      </div>
        <div class="methods-container">
          <label class="method-option" :class="{ 'selected-method': abilityScoreMethod === 'standard' }">
          <input type="radio" :checked="abilityScoreMethod === 'standard'" @change="abilityScoreMethod = 'standard'" value="standard" name="score-method">
            <span class="method-label">Standard Array</span>
          </label>
          <label class="method-option" :class="{ 'selected-method': abilityScoreMethod === 'pointbuy' }">
          <input type="radio" :checked="abilityScoreMethod === 'pointbuy'" @change="abilityScoreMethod = 'pointbuy'" value="pointbuy" name="score-method">
            <span class="method-label">Point Buy</span>
          </label>
          <label class="method-option" :class="{ 'selected-method': abilityScoreMethod === 'roll' }">
          <input type="radio" :checked="abilityScoreMethod === 'roll'" @change="abilityScoreMethod = 'roll'" value="roll" name="score-method">
            <span class="method-label">Roll / Custom</span>
          </label>
        </div>

        <!-- Standard Array Interface -->
        <div v-if="abilityScoreMethod === 'standard'" class="standard-array-container">
          <div class="standard-array-info">
            <span class="standard-array-label">Standard Array</span>
            <span class="standard-array-values">15, 14, 13, 12, 10, 8</span>
          </div>
          <div class="standard-array-assignments">
            <div v-for="ability in abilities" :key="ability.name" class="standard-array-ability">
              <span class="ability-name">{{ ability.name }}</span>
              <div class="standard-array-controls">
              <select
                :value="standardArrayPending[ability.name] === null ? 'null' : standardArrayPending[ability.name]"
                @change="onUpdateStandardArrayPending({ ability: ability.name, value: $event.target.value === 'null' ? null : Number($event.target.value) })"
                class="styled-standard-dropdown"
              >
                <option v-if="standardArrayPending[ability.name] === null" value="null">--</option>
                <option v-for="value in getAvailableStandardArrayValuesPending(ability.name)" :key="value" :value="value">
                  {{ value }}
                </option>
              </select>
              </div>
            </div>
          </div>
          <div class="reset-button-container" style="display: flex; gap: 10px; justify-content: flex-end;">
          <button @click="resetStandardArrayPending" class="reset-standard-array-btn">Reset</button>
          <button @click="confirmAbilityScoreApplication('standard')" class="reset-standard-array-btn" :disabled="!areAllStandardValuesAssigned">Apply</button>
        </div>
        <div v-if="!areAllStandardValuesAssigned" class="standard-array-warning">
          Choose value for all abilitys before applying changes.
          </div>
        </div>

        <!-- Point Buy Interface -->
        <div v-if="abilityScoreMethod === 'pointbuy'" class="point-buy-container">
          <div class="point-buy-info">
            <span class="points-spent-label">Points Spent:</span>
            <span class="points-spent-value" :class="{ 'points-exceeded': pointBuyPointsSpent > totalPointBuyPoints }">{{ pointBuyPointsSpent }}</span>
            <span class="points-total">/</span>
            <span class="points-total-value">{{ totalPointBuyPoints }}</span>
          </div>
          <div class="point-buy-assignments">
            <div v-for="ability in abilities" :key="ability.name" class="point-buy-ability">
              <span class="ability-name">{{ ability.name }}</span>
              <div class="point-buy-controls">
              <button class="point-buy-btn" @click="decreasePointBuyPending(ability.name)" :disabled="pointBuyPending[ability.name] <= 8">-</button>
                <span class="point-buy-value">{{ pointBuyPending[ability.name] }}</span>
              <button class="point-buy-btn" @click="increasePointBuyPending(ability.name)" :disabled="pointBuyPending[ability.name] >= 15 || pointBuyPointsSpent + getPointCost(pointBuyPending[ability.name] + 1) - getPointCost(pointBuyPending[ability.name]) > totalPointBuyPoints">+</button>
                <span class="point-cost">
                  ({{ getPointCost(pointBuyPending[ability.name]) }} pts)
                </span>
              </div>
            </div>
          </div>
          <div class="reset-button-container" style="display: flex; gap: 10px; justify-content: flex-end;">
          <button @click="resetPointBuyPending" class="reset-point-buy-btn">Reset</button>
          <button @click="confirmAbilityScoreApplication('pointbuy')" class="reset-point-buy-btn" :disabled="pointBuyPointsSpent < totalPointBuyPoints">Apply</button>
        </div>
        <div v-if="pointBuyPointsSpent < totalPointBuyPoints" class="point-buy-warning">
          Spend all available points. ({{ totalPointBuyPoints - pointBuyPointsSpent }} unused)
          </div>
        </div>

        <!-- Custom Interface -->
        <div v-if="abilityScoreMethod === 'roll'" class="roll-container">
          <div class="roll-info">
            <span class="roll-label">Custom</span>
            <span class="roll-description">Values from 1 to 20</span>
          </div>
          <div class="roll-assignments">
            <div v-for="ability in abilities" :key="ability.name" class="roll-ability">
              <span class="ability-name">{{ ability.name }}</span>
              <div class="roll-controls">
              <button class="roll-btn" @click="decreaseRollPending(ability.name)" :disabled="rollPending[ability.name] <= 1">-</button>
                <span class="roll-value">{{ rollPending[ability.name] }}</span>
              <button class="roll-btn" @click="increaseRollPending(ability.name)" :disabled="rollPending[ability.name] >= 20">+</button>
              </div>
            </div>
          </div>
          <div class="roll-button-container" style="display: flex; gap: 10px; justify-content: flex-end;">
          <button @click="resetRollPending" class="reset-roll-btn">Reset</button>
          <button @click="confirmAbilityScoreApplication('roll')" class="reset-roll-btn">Apply</button>
        </div>
      </div>
      
      <!-- Confirmation Dialog -->
      <div v-if="showConfirmationDialog" class="confirmation-dialog">
        <div class="confirmation-content">
          <p>Are you sure, you want to apply these changes? You can't go back.</p>
          <div class="confirmation-buttons">
            <button @click="applyConfirmedChanges">Yes</button>
            <button @click="cancelConfirmation">No</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AbilityScoreMethod',
  props: {
    abilities: { type: Array, required: true },
    character: { type: Object, required: true }
  },
  data() {
    return {
      abilityScoreMethod: 'standard',
      showAbilityScoreMethod: true,
      standardArrayValues: [15, 14, 13, 12, 10, 8],
      standardArrayPending: {
        Strength: null,
        Dexterity: null,
        Constitution: null,
        Intelligence: null,
        Wisdom: null,
        Charisma: null
      },
      totalPointBuyPoints: 27,
      pointBuyPending: {
        Strength: 8,
        Dexterity: 8,
        Constitution: 8,
        Intelligence: 8,
        Wisdom: 8,
        Charisma: 8
      },
      pointCosts: {
        8: 0,
        9: 1,
        10: 2,
        11: 3,
        12: 4,
        13: 5,
        14: 7,
        15: 9
      },
      rollPending: {
        Strength: 10,
        Dexterity: 10,
        Constitution: 10,
        Intelligence: 10,
        Wisdom: 10,
        Charisma: 10
      },
      showConfirmationDialog: false,
      pendingMethod: null
    }
  },
  computed: {
    isAnyValueSelected() {
      return Object.values(this.standardArrayPending).some(value => value !== null);
    },
    pointBuyPointsSpent() {
      return Object.values(this.pointBuyPending).reduce((total, value) => total + this.getPointCost(value), 0);
    },
    areAllStandardValuesAssigned() {
      return Object.values(this.standardArrayPending).every(value => value !== null);
    }
  },
  methods: {
    // Helpers
    getPointCost(value) {
      return this.pointCosts[value] || 0;
    },
    
    // Standard Array Methods
    getAvailableStandardArrayValuesPending(abilityName) {
      return this.standardArrayValues.filter(value => 
        !Object.values(this.standardArrayPending).includes(value) || 
        this.standardArrayPending[abilityName] === value
      );
    },
    
    resetStandardArrayPending() {
      for (const ability in this.standardArrayPending) {
        this.standardArrayPending[ability] = null;
      }
    },
    
    onUpdateStandardArrayPending({ ability, value }) {
      // Provera da li je vrednost "null" (string) ili null
      if (value === "null" || value === null) {
        this.updateAbilityValue('standard', 'assign', ability, null);
      } else {
        // Ako je vrednost validna, pozovi updateAbilityValue
        this.updateAbilityValue('standard', 'assign', ability, value);
      }
    },
    
    // Point Buy Methods
    increasePointBuyPending(abilityName) {
      this.updateAbilityValue('pointbuy', 'increase', abilityName);
    },
    
    decreasePointBuyPending(abilityName) {
      this.updateAbilityValue('pointbuy', 'decrease', abilityName);
    },
    
    resetPointBuyPending() {
      this.updateAbilityValue('pointbuy', 'reset');
    },
    
    // Roll Methods
    increaseRollPending(abilityName) {
      this.updateAbilityValue('roll', 'increase', abilityName);
    },
    
    decreaseRollPending(abilityName) {
      this.updateAbilityValue('roll', 'decrease', abilityName);
    },
    
    resetRollPending() {
      this.updateAbilityValue('roll', 'reset');
    },
    
    // Confirmation Dialog
    confirmAbilityScoreApplication(method) {
      this.pendingMethod = method;
      this.showConfirmationDialog = true;
    },
    
    applyConfirmedChanges() {
      if (this.pendingMethod === 'standard') {
        this.applyStandardArrayToCharacter();
      } else if (this.pendingMethod === 'pointbuy') {
        this.applyPointBuyToCharacter();
      } else if (this.pendingMethod === 'roll') {
        this.applyRollToCharacter();
      }
      
      this.showConfirmationDialog = false;
      this.showAbilityScoreMethod = false; // Sakrivamo ability score modal nakon što je korisnik potvrdio izbor
      
      // Emit event to parent to update character abilities
      this.$emit('abilities-confirmed', this.pendingMethod);
    },
    
    cancelConfirmation() {
      this.showConfirmationDialog = false;
    },
    
    // Apply methods
    applyStandardArrayToCharacter() {
      this.updateAbilityValue('standard', 'apply');
    },
    
    applyPointBuyToCharacter() {
      this.updateAbilityValue('pointbuy', 'apply');
    },
    
    applyRollToCharacter() {
      this.updateAbilityValue('roll', 'apply');
    },
    
    // Universal ability value update method
    updateAbilityValue(method, action, abilityName, amount = 1) {
      const methodMap = {
        'standard': 'standardArrayPending',
        'pointbuy': 'pointBuyPending',
        'roll': 'rollPending'
      };
      
      const propName = methodMap[method];
      if (!propName) return; // Nepodržana metoda
      
      switch (action) {
        case 'increase':
          // Povećaj vrednost ako je moguće
          if (method === 'pointbuy') {
            // Point buy ima složena pravila
            const currentValue = this[propName][abilityName];
            const newValue = currentValue + amount;
            
            // Provera ograničenja
            if (newValue > 15) return;
            
            // Proveri dostupne poene
            const currentCost = this.getPointCost(currentValue);
            const newCost = this.getPointCost(newValue);
            const pointDifference = newCost - currentCost;
            
            if (this.pointBuyPointsSpent + pointDifference > this.totalPointBuyPoints) return;
            
            // Primeni novu vrednost
            this[propName][abilityName] = newValue;
          }
          else if (method === 'roll') {
            // Roll ima jednostavna pravila
            const currentValue = this[propName][abilityName];
            const newValue = currentValue + amount;
            
            // Ograničenje: 1-20
            if (newValue > 20) return;
            
            // Primeni novu vrednost
            this[propName][abilityName] = newValue;
          }
          break;
        
        case 'decrease':
          // Smanji vrednost ako je moguće
          if (method === 'pointbuy') {
            // Point buy ima svoj minimum
            const currentValue = this[propName][abilityName];
            const newValue = currentValue - amount;
            
            // Ograničenje: najmanje 8
            if (newValue < 8) return;
            
            // Primeni novu vrednost
            this[propName][abilityName] = newValue;
          }
          else if (method === 'roll') {
            // Roll ima svoj minimum
            const currentValue = this[propName][abilityName];
            const newValue = currentValue - amount;
            
            // Ograničenje: najmanje 1
            if (newValue < 1) return;
            
            // Primeni novu vrednost
            this[propName][abilityName] = newValue;
          }
          break;
        
        case 'reset':
          // Resetuj vrednosti na početne
          if (method === 'standard') {
            // Resetuj sve vrednosti na null
            for (const ability in this[propName]) {
              this[propName][ability] = null;
            }
          }
          else if (method === 'pointbuy') {
            // Resetuj sve vrednosti na 8
            for (const ability in this[propName]) {
              this[propName][ability] = 8;
            }
          }
          else if (method === 'roll') {
            // Resetuj sve vrednosti na 10
            for (const ability in this[propName]) {
              this[propName][ability] = 10;
            }
          }
          break;
        
        case 'apply':
          // Primeni pending vrednosti na character
          for (const ability in this[propName]) {
            if (method === 'standard' && this[propName][ability] !== null || 
                method !== 'standard') {
              // Postavi ability score u character objektu
              this.$emit('update-ability-score', {
                ability: ability,
                value: this[propName][ability]
              });
            }
          }
          break;
        
        case 'assign':
          // Poseban slučaj za Standard Array - dodeljuje vrednost ability-ju
          if (method === 'standard' && amount !== undefined) {
            // Prvo ukloni vrednost ako je već dodeljena negde
            for (const ab in this[propName]) {
              if (this[propName][ab] === amount) {
                this[propName][ab] = null;
              }
            }
            
            // Dodeli novu vrednost
            this[propName][abilityName] = amount;
          }
          break;
      }
    }
  }
}
</script>

<style scoped>
  .section-title {
    font-size: 1.3em;
    font-weight: bold;
    text-transform: uppercase;
    color: #333;
    margin-bottom: 5px;
    padding-bottom: 4px;
    border-bottom: 2px solid #000;  
    text-align: center;
  }

  .ability-score-method {
    background-color: white;
    border: 3px solid #222;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.07);
    padding: 15px;
    width: 100%;
    box-sizing: border-box;
  }

  .methods-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .method-option {
    position: relative;
    display: block;
    padding: 8px 12px;
    background-color: #f8f8f8;
    border: 2px solid #222;
    border-radius: 8px;
    transition: background-color 0.2s;
    text-align: center;
    font-size: 1.2em;
  }

  .method-option:hover {
    background-color: #e0e0e0;
  }
  
  .selected-method {
    background-color: #e0e0e0;
    border-color: #000;
    box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1);
  }

  .method-label {
    font-weight: bold;
    color: #333;
    display: block;
  }

  .method-option input[type="radio"] {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
    margin: 0;
    padding: 0;
  }
  
  .ability-score-instructions {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px 15px;
    margin-bottom: 15px;
    text-align: center;
  }
  
  .ability-score-instructions p {
    margin: 0;
    font-size: 1.2em;
    color: #333;
    font-weight: 500;
  }
  
  .standard-array-container {
    margin-top: 15px;
    padding: 20px;
    background: linear-gradient(to bottom, #f8f8f8, #f0f0f0);
    border-radius: 12px;
    border: 2px solid #222;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  }
  
  .standard-array-assignments {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .standard-array-info {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 18px;
    background-color: #fff;
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .standard-array-label {
    font-weight: bold;
    font-size: 1.1em;
    margin-right: 10px;
    color: #333;
  }

  .standard-array-values {
    font-weight: bold;
    font-size: 1.2em;
    color: #555;
    background-color: #f8f8f8;
    border-radius: 4px;
    padding: 2px 10px;
    border: 1px solid #e0e0e0;
  }

  .standard-array-ability {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: white;
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
  }
  
  .standard-array-ability:hover {
    border-color: #555;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  }
  
  .standard-array-ability .ability-name {
    font-weight: bold;
    font-size: 1.1em;
    color: #333;
    text-align: left;
    min-width: 120px;
  }
  
  .standard-array-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .styled-standard-dropdown {
    width: 80px;
    padding: 2.6px 8px;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: linear-gradient(to bottom, #fff, #f5f5f5);
    color: #333;
    font-weight: bold;
    font-size: 1.2em;
    text-align: center;
    transition: all 0.2s ease;
    appearance: menulist;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .styled-standard-dropdown:hover {
    border-color: #888;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
  }
  
  .styled-standard-dropdown:focus {
    outline: none;
    border-color: #4CAF50;
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
  }
  
  .styled-standard-dropdown option {
    background-color: white;
    color: #333;
    padding: 8px;
  }
  
  .styled-standard-dropdown option:disabled {
    color: #aaa;
    background-color: #f0f0f0;
  }
  
  .reset-button-container {
    display: flex;
    justify-content: center;
    margin-top: 10px;
    position: relative;
  }
  
  .reset-standard-array-btn, .reset-point-buy-btn, .reset-roll-btn {
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
  
  .reset-standard-array-btn:hover, .reset-point-buy-btn:hover, .reset-roll-btn:hover {
    background: linear-gradient(to bottom, #f5f5f5, #e8e8e8);
    color: #000;
    border-color: #000;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
  }
  
  .reset-standard-array-btn:active, .reset-point-buy-btn:active, .reset-roll-btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
  }

  .point-buy-container {
    margin-top: 15px;
    padding: 20px;
    background: linear-gradient(to bottom, #f8f8f8, #f0f0f0);
    border-radius: 12px;
    border: 2px solid #222;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  }

  .point-buy-info {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 18px;
    background-color: #fff;
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .points-spent-label {
    font-weight: bold;
    font-size: 1.1em;
    margin-right: 10px;
    color: #333;
  }

  .points-spent-value {
    font-weight: bold;
    font-size: 1.3em;
    background-color: #f8f8f8;
    border-radius: 4px;
    padding: 2px 10px;
    margin-right: 5px;
    min-width: 30px;
    text-align: center;
    border: 1px solid #e0e0e0;
  }

  .points-total {
    font-weight: bold;
    font-size: 1.2em;
    color: #555;
    margin-right: 5px;
  }
  
  .points-total-value {
    font-weight: bold;
    font-size: 1.3em;
    color: #333;
    background-color: #f8f8f8;
    border-radius: 4px;
    padding: 2px 10px;
    min-width: 30px;
    text-align: center;
    border: 1px solid #e0e0e0;
  }

  .points-exceeded {
    color: #f44336;
    animation: pulse 1s infinite;
  }

  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
  }

  .point-buy-assignments {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }

  .point-buy-ability {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: white;
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
  }

  .point-buy-ability:hover {
    border-color: #555;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  }

  .point-buy-ability .ability-name {
    font-weight: bold;
    font-size: 1.1em;
    color: #333;
    text-align: left;
    min-width: 120px;
  }

  .point-buy-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .point-buy-btn {
    width: 30px;
    height: 30px;
    font-size: 1.4em;
    font-weight: bold;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: linear-gradient(to bottom, #fff, #f5f5f5);
    color: #333;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .point-buy-btn:not(:disabled):hover {
    background: linear-gradient(to bottom, #f5f5f5, #e8e8e8);
    border-color: #aaa;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
    transform: translateY(-1px);
  }

  .point-buy-btn:not(:disabled):active {
    background: linear-gradient(to bottom, #e8e8e8, #e0e0e0);
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }

  .point-buy-btn:disabled {
    opacity: 0.5;
    background: #f0f0f0;
  }

  .point-buy-value {
    font-size: 1.4em;
    font-weight: bold;
    color: #333;
    min-width: 30px;
    text-align: center;
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 2px 8px;
  }

  .point-cost {
    font-weight: bold;
    color: #555;
    min-width: 60px;
    text-align: center;
    padding: 2px 8px;
    background-color: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }

  /* Roll / Custom interface styles */
  .roll-container {
    margin-top: 15px;
    padding: 20px;
    background: linear-gradient(to bottom, #f8f8f8, #f0f0f0);
    border-radius: 12px;
    border: 2px solid #222;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  }

  .roll-info {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 18px;
    background-color: #fff;
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .roll-label {
    font-weight: bold;
    font-size: 1.1em;
    margin-right: 10px;
    color: #333;
  }

  .roll-description {
    font-weight: bold;
    font-size: 1.2em;
    color: #555;
    background-color: #f8f8f8;
    border-radius: 4px;
    padding: 2px 10px;
    text-align: center;
    border: 1px solid #e0e0e0;
  }

  .roll-assignments {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }

  .roll-ability {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: white;
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
  }

  .roll-ability:hover {
    border-color: #555;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  }

  .roll-ability .ability-name {
    font-weight: bold;
    font-size: 1.1em;
    color: #333;
    text-align: left;
    min-width: 120px;
  }

  .roll-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .roll-btn {
    width: 30px;
    height: 30px;
    font-size: 1.4em;
    font-weight: bold;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: linear-gradient(to bottom, #fff, #f5f5f5);
    color: #333;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .roll-btn:not(:disabled):hover {
    background: linear-gradient(to bottom, #f5f5f5, #e8e8e8);
    border-color: #aaa;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
    transform: translateY(-1px);
  }

  .roll-btn:not(:disabled):active {
    background: linear-gradient(to bottom, #e8e8e8, #e0e0e0);
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }

  .roll-btn:disabled {
    opacity: 0.5;
    background: #f0f0f0;
  }

  .roll-value {
    font-size: 1.4em;
    font-weight: bold;
    color: #333;
    min-width: 30px;
    text-align: center;
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 2px 8px;
  }

  .roll-button-container {
    display: flex;
    justify-content: center;
    margin-top: 10px;
  }
  
  /* Confirmation Dialog Styles */
  .confirmation-dialog {
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
  
  .confirmation-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    text-align: center;
    max-width: 400px;
    width: 90%;
  }
  
  .confirmation-content p {
    margin: 0 0 20px 0;
    font-size: 1.2em;
    color: #333;
  }
  
  .confirmation-buttons {
    display: flex;
    justify-content: center;
    gap: 15px;
  }
  
  .confirmation-buttons button {
    padding: 8px 25px;
    border: none;
    border-radius: 5px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 1.1em;
  }
  
  .confirmation-buttons button:first-child {
    background-color: #4CAF50;
    color: white;
  }
  
  .confirmation-buttons button:last-child {
    background-color: #f44336;
    color: white;
  }
  
  .confirmation-buttons button:hover {
    opacity: 0.9;
    transform: translateY(-2px);
  }
  
  .confirmation-buttons button:active {
    opacity: 1;
    transform: translateY(0);
  }
  
  /* Warning Messages Styles */
  .standard-array-warning,
  .point-buy-warning {
    display: block;
    color: #e74c3c;
    font-size: 0.85em;
    margin-top: 10px;
    background-color: #fef2f2;
    border: 1px solid #f5c6cb;
    border-radius: 5px;
    padding: 8px 12px;
    position: relative;
    width: 100%;
    box-sizing: border-box;
    text-align: center;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    animation: fadeIn 0.3s ease-out;
    font-weight: 500;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
</style>

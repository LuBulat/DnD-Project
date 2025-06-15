<template>
  <div class="character-sheet">
    <!-- Notification -->
    <Transition name="slide-fade">
      <div v-if="showNotification" :class="['notification', notificationType]">
        {{ notificationMessage }}
      </div>
    </Transition>
    
    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      :show="showConfirmationDialog"
      :title="confirmationTitle"
      :message="confirmationMessage"
      :confirm-text="confirmationConfirmText" 
      :cancel-text="confirmationCancelText"
      @confirm="handleConfirmationConfirm"
      @cancel="handleConfirmationCancel"
    />

    <!-- Ability Score Method Modal -->
    <div v-if="showAbilityScoreMethod" class="ability-score-modal-overlay">
      <div class="ability-score-modal">
        <AbilityScoreMethod
          :abilities="abilities"
          :character="character"
          @update-ability-score="updateCharacterAbilityScore"
          @abilities-confirmed="onAbilitiesConfirmed"
        />
      </div>
    </div>

    <!-- Half-Elf Ability Score Modal -->
    <HalfElfAbilityScore
      v-if="showHalfElfAbilityScore"
      :abilities="abilities"
      :current-scores="character.abilities"
      @abilities-selected="handleHalfElfAbilitySelection"
    />

    <!-- Prvi list -->
    <div class="sheet-page">
      <div class="sheet-header">
        <div class="top-row">
          <div class="character-name">
            <input type="text" v-model="character.name" placeholder="Character Name">
          </div>
          <div class="player-name">
            <input type="text" v-model="character.playerName" placeholder="Player Name">
          </div>
        </div>
        <div class="character-info">
          <div class="race-subrace-container">
            <div class="info-item">
              <label class="required">Race</label>
              <select v-model="character.race" :disabled="id !== null">
                <option v-if="!character.race" value="">Choose race</option>
                <option v-for="race in races" :key="race.id" :value="race.name">{{ race.name }}</option>
              </select>
            </div>
            <div class="info-item" v-if="subraces.length > 0">
              <label class="required">Subrace</label>
              <select v-model="character.subrace" :disabled="id !== null">
                <option v-if="!character.subrace" value="">Choose subrace</option>
                <option v-for="subrace in subraces" :key="subrace.id" :value="subrace.name">{{ subrace.name }}</option>
              </select>
            </div>
          </div>
          <div class="info-item">
            <label class="required">Class</label>
            <select v-model="character.class" :disabled="id !== null">
              <option v-if="!character.class" value="">Choose class</option>
              <option v-for="cls in classes" :key="cls.id" :value="cls.name">{{ cls.name }}</option>
            </select>
          </div>
          <div class="info-item">
            <label>Level</label>
            <div class="styled-container">
              <span class="level-value">{{ character.level }}</span>
              <div class="modifier-controls">
                <button class="modifier-btn" @click="adjustLevel(1)">+</button>
                <button class="modifier-btn" @click="adjustLevel(-1)">-</button>
              </div>
            </div>
          </div>
        </div>
        <div class="character-info">
          <div class="background-variant-container">
            <div class="info-item">
              <label class="required">Background</label>
              <select v-model="character.background" :disabled="id !== null">
                <option v-if="!character.background" value="">Choose background</option>
                <option v-for="bg in backgrounds" :key="bg.id" :value="bg.name">{{ bg.name }}</option>
              </select>
            </div>
            <div class="info-item" v-if="backgroundVariant">
              <label>Variant</label>
              <select v-model="character.backgroundVariant" :disabled="id !== null">
                <option value="">None</option>
                <option :value="backgroundVariant">{{ backgroundVariant }}</option>
              </select>
            </div>
          </div>
          <div class="info-item">
            <label>Alignment</label>
            <select v-model="character.alignment">
              <option v-if="!character.alignment" value="">Choose alignment</option>
              <option>Lawful Good</option>
              <option>Neutral Good</option>
              <option>Chaotic Good</option>
              <option>Lawful Neutral</option>
              <option>True Neutral</option>
              <option>Chaotic Neutral</option>
              <option>Lawful Evil</option>
              <option>Neutral Evil</option>
              <option>Chaotic Evil</option>
            </select>
          </div>
          <div class="info-item">
            <label>Experience Points</label>
            <input type="text" 
                  v-model="character.experiencePoints" 
                  @input="validateExperiencePoints"
                  placeholder="XP" 
                  class="styled-input">
          </div>
          <div class="info-message proficiency-info" v-if="showProficiencyInfo">
            <span>Some proficiencies, such as skills or tools, may overlap. For example, choosing the Elf race and the Sailor background both grant Perception proficiency. In that case, you can pick one additional proficiency to gain.</span>
            <button class="delete-info-btn" @click="removeProficiencyInfo">×</button>
          </div>
        </div>
      </div>
    
      <div class="sheet-body-grid">
        <!-- LEVA KOLONA -->
        <div class="left-bar">
          <div class="left-block">
            <!-- 1. deo - Ability Scores -->
            <div class="abilities-block">
              <div v-for="ability in abilities" :key="ability.name" class="ability-score">
                <div class="ability-name">{{ ability.name }}</div>
                <div class="ability-score-controls">
                  <button class="ability-score-btn" @click="adjustAbilityScore(ability.name, -1)">-</button>
                  <div class="ability-score-value">
                    <span class="score-value" :class="getAbilityScoreColorClass(ability.name)">{{ character.abilities[ability.name].score }}</span>
                  </div>
                  <button class="ability-score-btn" @click="adjustAbilityScore(ability.name, 1)">+</button>
                </div>
                <div class="ability-modifier">
                  <input type="text" :value="formatModifier(character.abilities[ability.name].modifier)" readonly class="modifier-ellipse">
                </div>
              </div>
              <div class="passive-wisdom-row-vertical">
                <div class="passive-wisdom-controls">
                  <button class="passive-wisdom-btn" @click="adjustPassiveWisdom(-1)">-</button>
                  <div class="passive-wisdom-value">
                    <span class="modifier" :class="passiveWisdomColorClass">{{ character.passiveWisdom }}</span>
                  </div>
                  <button class="passive-wisdom-btn" @click="adjustPassiveWisdom(1)">+</button>
                </div>
                <span class="passive-wisdom-label">PASSIVE WISDOM (PERCEPTION)</span>
              </div>
            </div>

            <!-- 2. deo - Inspiration, Proficiency, Saving Throws, Skills -->
            <div class="right-block">
              <div class="passive-wisdom-row">
                <div class="inspiration-container small-input">
                  <span class="modifier">{{ character.inspiration.value }}</span>
                  <div class="modifier-controls">
                    <button class="modifier-btn" @click="adjustInspiration(1)">+</button>
                    <button class="modifier-btn" @click="adjustInspiration(-1)">-</button>
                  </div>
                </div>
                <span class="passive-wisdom-label">INSPIRATION</span>
              </div>
              <div class="passive-wisdom-row">
                <div class="inspiration-container small-input">
                  <span class="modifier" :class="profClass">{{ character.proficiencyBonus }}</span>
                  <div class="modifier-controls">
                    <button class="modifier-btn" @click="adjustProf(1)">+</button>
                    <button class="modifier-btn" @click="adjustProf(-1)">-</button>
                  </div>
                </div>
                <span class="passive-wisdom-label">PROFICIENCY BONUS (PB)</span>
              </div>

              <div class="saving-throws-block">
                <div class="section-title">Saving Throws</div>
                <div class="saving-throw" v-for="ability in abilities" :key="ability.name">
                  <input type="checkbox" v-model="character.savingThrows[ability.name].proficient">
                  <span class="modifier" :class="getModifierColorClass('savingThrow', ability.name)">
                    {{ character.savingThrows[ability.name].modifier }}
                  </span>
                  <div class="modifier-controls">
                    <button class="modifier-btn" @click="adjustSavingThrowModifier(ability.name, 1)">+</button>
                    <button class="modifier-btn" @click="adjustSavingThrowModifier(ability.name, -1)">-</button>
                  </div>
                  <span class="ability-name">{{ ability.name }}</span>
                </div>
              </div>

              <div class="skills-block">
                <div class="skills-header-row">
                  <span class="pb-label">PB</span>
                  <span class="e-label">E</span>
                  <span class="skill-label">SKILLS</span>
                  <span class="prof-label">CHOICES: {{ maxSelectableSkills }}</span>
                </div>
                <div class="skill" 
                      v-for="skill in skills" 
                      :key="skill.name"
                      :class="{ 'selectable': isSkillSelectable(skill.name) }">
                  <span class="pb-col"><input type="checkbox" v-model="character.skills[skill.name].proficient"></span>
                  <span class="e-col"><input type="checkbox" v-model="character.skills[skill.name].expertise"></span>
                  <div class="mod-col modifier-container">
                    <span class="modifier" :class="getModifierColorClass('skill', skill.name)">
                      {{ character.skills[skill.name].modifier }}
                    </span>
                    <div class="modifier-controls">
                      <button class="modifier-btn" @click.stop="adjustSkillModifier(skill.name, 1)">+</button>
                      <button class="modifier-btn" @click.stop="adjustSkillModifier(skill.name, -1)">-</button>
                    </div>
                  </div>
                  <span class="skill-col skill-name">{{ skill.name }}</span>
                  <span class="abil-col ability-name">({{ skill.ability }})</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- SREDNJA KOLONA -->
        <div class="center-bar">
          <div class="top-row-2">
            <div class="initiative-box">
              <div class="initiative-header">Initiative</div>
              <div class="initiative-container">
                <button class="initiative-btn" @click="adjustInitiative(-1)">-</button>
                <div class="initiative-value">
                  <span class="modifier" :class="getModifierColorClass('initiative')">{{ character.initiative }}</span>
                </div>
                <button class="initiative-btn" @click="adjustInitiative(1)">+</button>
              </div>
            </div>
            <div class="ac-box">
              <div class="ac-header">Armor Class</div>
              <div class="ac-container">
                <button class="ac-btn" @click="adjustAC(-1)">-</button>
                <div class="ac-value">
                  <span class="modifier" :class="getModifierColorClass('ac')">{{ character.ac }}</span>
                </div>
                <button class="ac-btn" @click="adjustAC(1)">+</button>
              </div>
            </div>
            <div class="speed-box">
              <div class="speed-header">Speed</div>
              <div class="speed-container">
                <button class="speed-btn" @click="adjustSpeed(-5)">-</button>
                <div class="speed-value">
                  <span class="modifier" :class="getModifierColorClass('speed')">{{ character.speed }}</span>
                </div>
                <button class="speed-btn" @click="adjustSpeed(5)">+</button>
              </div>
            </div>
          </div>
          <div class="ac-row">
            <select v-model="character.armor" @change="updateAC">
              <option value="">No Armor</option>
              <option value="padded">Padded</option>
              <option value="leather">Leather</option>
              <option value="studded">Studded Leather</option>
              <option value="hide">Hide</option>
              <option value="chain_shirt">Chain Shirt</option>
              <option value="scale_mail">Scale Mail</option>
              <option value="breastplate">Breastplate</option>
              <option value="half_plate">Half Plate</option>
              <option value="ring_mail">Ring Mail</option>
              <option value="chain_mail">Chain Mail</option>
              <option value="splint">Splint</option>
              <option value="plate">Plate</option>
            </select>
            <div class="shield-checkbox">
              <input type="checkbox" id="shield" v-model="character.hasShield" @change="updateAC">
              <label for="shield">Shield</label>
            </div>
          </div>
          <div class="hp-block">
            <div class="hp">
              <div class="hp-max">
              <div class="hp-header">Hit Point Maximum</div>
                <div class="hp-controls">
                  <div class="hp-buttons-left">
                    <button class="hp-btn" @click="adjustMaxHP(-5)">-5</button>
                    <button class="hp-btn" @click="adjustMaxHP(-1)">-1</button>
                    <button class="hp-btn" @click="adjustMaxHP(-30)">-30</button>
                    <button class="hp-btn" @click="adjustMaxHP(-10)">-10</button>
                  </div>
                  <div class="hp-value">
                    <span class="modifier">{{ character.hp.max }}</span>
                  </div>
                  <div class="hp-buttons-right">
                    <button class="hp-btn" @click="adjustMaxHP(1)">+1</button>
                    <button class="hp-btn" @click="adjustMaxHP(5)">+5</button>
                    <button class="hp-btn" @click="adjustMaxHP(10)">+10</button>
                    <button class="hp-btn" @click="adjustMaxHP(30)">+30</button>
                  </div>
                </div>
              </div>
            </div>
            <div class="hp-current">
              <div class="hp-header">Current Hit Points</div>
              <div class="hp-controls">
                <div class="hp-buttons-left">
                  <button class="hp-btn" @click="adjustCurrentHP(-5)">-5</button>
                  <button class="hp-btn" @click="adjustCurrentHP(-1)">-1</button>
                  <button class="hp-btn" @click="adjustCurrentHP(-30)">-30</button>
                  <button class="hp-btn" @click="adjustCurrentHP(-10)">-10</button>
                </div>
                <div class="hp-value">
                  <span class="modifier">{{ character.hp.current }}</span>
                </div>
                <div class="hp-buttons-right">
                  <button class="hp-btn" @click="adjustCurrentHP(1)">+1</button>
                  <button class="hp-btn" @click="adjustCurrentHP(5)">+5</button>
                  <button class="hp-btn" @click="adjustCurrentHP(10)">+10</button>
                  <button class="hp-btn" @click="adjustCurrentHP(30)">+30</button>
                </div>
              </div>
            </div>
            <div class="hp-temp">
              <div class="hp-header">Temporary Hit Points</div>
              <div class="hp-controls">
                <div class="hp-buttons-left">
                  <button class="hp-btn" @click="adjustTempHP(-5)">-5</button>
                  <button class="hp-btn" @click="adjustTempHP(-1)">-1</button>
                  <button class="hp-btn" @click="adjustTempHP(-30)">-30</button>
                  <button class="hp-btn" @click="adjustTempHP(-10)">-10</button>
                </div>
                <div class="hp-value">
                  <span class="modifier">{{ character.hp.temp }}</span>
                </div>
                <div class="hp-buttons-right">
                  <button class="hp-btn" @click="adjustTempHP(1)">+1</button>
                  <button class="hp-btn" @click="adjustTempHP(5)">+5</button>
                  <button class="hp-btn" @click="adjustTempHP(10)">+10</button>
                  <button class="hp-btn" @click="adjustTempHP(30)">+30</button>
                </div>
              </div>
            </div>
          </div>
          <div class="hitdice-deathsaves-row">
            <div class="hit-dice-block">
              <label>Hit Dice</label>
              <div class="hit-dice-input-container small-input">
                <div class="modifier-controls">
                  <button class="modifier-btn" @click="adjustHitDice(1)">+</button>
                  <button class="modifier-btn" @click="adjustHitDice(-1)">-</button>
                </div>
                <span class="modifier">{{ character.hitDice }}</span>
                <span class="hit-dice-d">d</span>
                <span class="hit-dice-value">{{ character.hitDie }}</span>
              </div>
            </div>
            <div class="death-saves">
              <div class="death-saves-header">Death Saves</div>
              <div class="death-saves-content">
                <div class="successes">
                  <div class="success-header">Successes</div>
                  <div class="success-boxes">
                    <input type="checkbox" v-model="character.deathSaves.successes[0]">
                    <input type="checkbox" v-model="character.deathSaves.successes[1]">
                    <input type="checkbox" v-model="character.deathSaves.successes[2]">
                  </div>
                </div>
                <div class="failures">
                  <div class="failure-header">Failures</div>
                  <div class="failure-boxes">
                    <input type="checkbox" v-model="character.deathSaves.failures[0]">
                    <input type="checkbox" v-model="character.deathSaves.failures[1]">
                    <input type="checkbox" v-model="character.deathSaves.failures[2]">
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="attacks-spellcasting">
            <div class="section-title">Attacks & Spellcasting</div>
            <div class="attacks-list">
              <div v-for="(attack, index) in character.attacks" :key="index" class="attack-item">
                <input type="text" v-model="attack.name" placeholder="Name" class="attack-item-input name">
                <input type="text" v-model="attack.bonus" placeholder="Bonus" class="attack-item-input bonus">
                <input type="text" v-model="attack.damage" placeholder="Damage" class="attack-item-input damage">
                <button class="delete-attack" @click="deleteAttack(index)">Delete</button>
              </div>
              <button class="add-attack-btn" @click="addAttack">Add Attack</button>
            </div>
          </div>
          <div class="equipment">
            <div class="section-title">Equipment</div>
            <textarea v-model="character.equipment" placeholder="Equipment"></textarea>
            <div class="currency-inputs">
              <div class="currency-input">
                <span>CP</span>
                <input type="text" v-model="character.currency.cp" @input="validateCurrency($event, 'cp')">
              </div>
              <div class="currency-input">
                <span>SP</span>
                <input type="text" v-model="character.currency.sp" @input="validateCurrency($event, 'sp')">
              </div>
              <div class="currency-input">
                <span>EP</span>
                <input type="text" v-model="character.currency.ep" @input="validateCurrency($event, 'ep')">
              </div>
              <div class="currency-input">
                <span>GP</span>
                <input type="text" v-model="character.currency.gp" @input="validateCurrency($event, 'gp')">
              </div>
              <div class="currency-input">
                <span>PP</span>
                <input type="text" v-model="character.currency.pp" @input="validateCurrency($event, 'pp')">
              </div>
            </div>
          </div>
        </div>
        
        <!-- DESNA KOLONA -->
        <div class="right-bar">
          <div class="personality">
            <div class="features-traits">
              <div class="section-title">Race Features & Traits</div>
              <textarea v-model="character.raceFeatures" placeholder="Race Features & Traits"></textarea>
            </div>
            <div class="features-traits">
              <div class="section-title">Class Features & Traits</div>
              <textarea v-model="character.classFeatures" placeholder="Class Features & Traits"></textarea>
            </div>
            <div class="features-traits">
              <div class="section-title">Race Proficiencies & Languages</div>
              <textarea v-model="character.raceProficiencies" placeholder="Race Proficiencies & Languages"></textarea>
            </div>
            <div class="features-traits">
              <div class="section-title">Class Proficiencies & Languages</div>
              <textarea v-model="character.classProficiencies" placeholder="Class Proficiencies & Languages"></textarea>
            </div>
            <div class="features-traits">
              <div class="section-title">Background Features, Proficiencies & Languages</div>
              <textarea v-model="character.backgroundFeatures" placeholder="Background Features, Proficiencies & Languages"></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Drugi list -->
    <div class="sheet-page">
      <div class="second-header-row">
        <div class="second-header-fields">
          <div class="header-row">
            <div class="header-field">
              <label>Age</label>
              <input type="text" v-model="character.age">
            </div>
            <div class="header-field">
              <label>Height</label>
              <input type="text" v-model="character.height">
            </div>
            <div class="header-field">
              <label>Weight</label>
              <input type="text" v-model="character.weight">
            </div>
          </div>
          <div class="header-row">
            <div class="header-field">
              <label>Eyes</label>
              <input type="text" v-model="character.eyes">
            </div>
            <div class="header-field">
              <label>Skin</label>
              <input type="text" v-model="character.skin">
            </div>
            <div class="header-field">
              <label>Hair</label>
              <input type="text" v-model="character.hair">
            </div>
          </div>
        </div>
      </div>
      <div class="second-body-grid">
        <div class="second-col left">
          <div class="big-box char">
            <div class="appearance-header">
              <label>Character Appearance</label>
              <div class="file-input-container">
                <label for="appearanceImage" class="custom-file-upload">Choose File</label>
                <input id="appearanceImage" type="file" accept="image/*" @change="onImageChange($event, 'appearanceImage')">
              </div>
            </div>
            <img v-if="character.appearanceImage" :src="getImageUrl(character.appearanceImage)" alt="Character Appearance" class="image-preview">
          </div>
          <div class="big-box">
            <label>Character Backstory</label>
            <textarea v-model="character.backstory"></textarea>
          </div>
        </div>
        <div class="second-col center">
          <div class="allies-symbol-row">
            <div class="big-box allies-box">
              <label>Allies & Organizations</label>
              <textarea v-model="character.allies"></textarea>
            </div>
            <div class="symbol-box">
              <div class="appearance-header">
                <label>Symbol</label>
                <div class="file-input-container">
                  <label for="symbolImage" class="custom-file-upload">Choose File</label>
                  <input id="symbolImage" type="file" accept="image/*" @change="onImageChange($event, 'symbolImage')">
                </div>
              </div>
              <input type="text" v-model="character.symbolName" placeholder="Name" class="symbol-name-input">
              <img v-if="character.symbolImage" :src="getImageUrl(character.symbolImage)" alt="Symbol" class="image-preview">
            </div>
          </div>
          <div class="big-box treasure-box">
            <label>Treasure</label>
            <textarea v-model="character.treasure"></textarea>
          </div>
        </div>
        <div class="second-col right">
          <div class="info-message">
            <span>You can choose, roll for, or create your own characteristics based on the <a href="/backgrounds" target="_blank">background's</a> "Suggested Characteristics".</span>
            <button class="delete-info-btn" @click="removeInfoMessage">×</button>
          </div>
          <div class="personality-item">
            <div class="section-title">Personality Traits</div>
            <textarea v-model="character.personality.traits" placeholder="Personality Traits"></textarea>
          </div>
          <div class="personality-item">
            <div class="section-title">Ideals</div>
            <textarea v-model="character.personality.ideals" placeholder="Ideals"></textarea>
          </div>
          <div class="personality-item">
            <div class="section-title">Bonds</div>
            <textarea v-model="character.personality.bonds" placeholder="Bonds"></textarea>
          </div>
          <div class="personality-item">
            <div class="section-title">Flaws</div>
            <textarea v-model="character.personality.flaws" placeholder="Flaws"></textarea>
          </div>
        </div>
      </div>
    </div>

    <!-- Treći list -->
    <div class="sheet-page">
      <div class="sheet-header">
        <div class="spellcasting-header">
          <div class="spell-save-dc">
            <div class="spell-header">Spell Save DC</div>
            <div class="spell-controls">
              <button class="spell-btn" @click="adjustSpellSaveDC(-1)">-</button>
              <span class="spell-value" :class="getSpellValueColorClass('saveDC')">{{ character.spellcasting.saveDC }}</span>
              <button class="spell-btn" @click="adjustSpellSaveDC(1)">+</button>
            </div>
          </div>
          
          <div class="spellcasting-ability">
            <div class="spell-header">Spellcasting Ability</div>
            <div class="spell-select">
              {{ character.spellcasting.ability || "None" }}
            </div>
          </div>
          
          <div class="spell-attack-bonus">
            <div class="spell-header">Spell Attack Bonus</div>
            <div class="spell-controls">
              <button class="spell-btn" @click="adjustSpellAttackBonus(-1)">-</button>
              <span class="spell-value" :class="getSpellValueColorClass('attackBonus')">{{ character.spellcasting.attackBonus }}</span>
              <button class="spell-btn" @click="adjustSpellAttackBonus(1)">+</button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Filteri -->
      <div class="spell-filters-row">
        <!-- Selektor klase -->
        <div class="spell-filter">
          <label for="filter-class">Filter by Class: </label>
          <select id="filter-class" v-model="selectedSpellClass" @change="filterSpells">
            <option value="null">All Classes</option>
            <option v-for="cls in classes" :key="cls.id" :value="cls.id">{{ cls.name }}</option>
          </select>
        </div>

        <!-- Selektor tipa magije -->
        <div class="spell-filter">
          <label for="filter-school">Filter by School: </label>
          <select id="filter-school" v-model="selectedSpellType" @change="filterSpells">
            <option value="null">All Types</option>
            <option v-for="type in spellTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </div>
      </div>

      <div class="spell-content">
        <div v-if="showPreparedSpellsInfo" class="info-message spell-prepared-info">
          <span>All spells except cantrips have a checkbox. Check the box to mark a spell as prepared.</span>
          <button class="delete-info-btn" @click="removePreparedSpellsInfo">×</button>
        </div>
        <div class="spell-grid">
          <!-- Dinamički prikaz za sve nivoe čarolija -->
          <div v-for="(levelInfo, levelIndex) in spellLevels" :key="levelIndex" class="spell-level-section">
            <div class="spell-level-header">
              <div class="level-diamond">
                <span>{{ levelInfo.level }}</span>
              </div>
              <div class="level-name" v-if="levelInfo.level === 0">CANTRIPS</div>
              <div class="level-name" v-else>
                <div class="spell-level-slots">
                  <div class="slots-container">
                    <span class="slots-label">SLOTS <br> TOTAL</span>
                    <div class="slots-input-container">
                      <button class="slots-btn" @click="adjustSlot(-1, levelInfo.level)">-</button>
                      <span class="slots-input">{{ spellSlots[levelInfo.level].total }}</span>
                      <button class="slots-btn" @click="adjustSlot(1, levelInfo.level)">+</button>
                      <span class="slots-separator">/</span>
                      <button class="slots-btn" @click="adjustUsedSlot(-1, levelInfo.level)">-</button>
                      <span class="slots-input">{{ spellSlots[levelInfo.level].used }}</span>
                      <button class="slots-btn" @click="adjustUsedSlot(1, levelInfo.level)">+</button>
                    </div>
                    <span class="slots-label slots-expended">SLOTS <br> EXPENDED</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="spell-list-rows">
              <div v-for="(spell, index) in character.spells[levelInfo.listKey]" :key="`${levelInfo.listKey}-${index}`" class="level1-item">
                <div class="cantrip-header">
                  <input v-if="levelInfo.level > 0" type="checkbox" class="spell-checkbox" v-model="spell.prepared">
                  <div :class="levelInfo.level === 0 ? 'cantrip-name' : 'spell-name'">{{ spell.spell_name }}</div>
                  <button class="delete-spell-btn" @click="removeSpell(index, levelInfo.listKey)">×</button>
                </div>
                <div class="underline"></div>
              </div>
              <div style="text-align: center; margin-top: 15px;">
                <button class="add-spell-btn" @click="openSpellModal(levelInfo.level)">Add Spell</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Jedinstveni modal za izbor čarolija -->
    <div v-if="showSpellModal" class="spell-modal">
      <div class="spell-modal-content">
        <span class="close-modal" @click="closeSpellModal">&times;</span>
        <h3>Select a {{ currentSpellLevel === 0 ? 'Cantrip' : `Level ${currentSpellLevel} Spell` }}</h3>
        <div v-if="loadingSpells" class="loading">Loading...</div>
        <div v-else class="spell-list">
          <div v-if="availableSpellsList.length === 0" class="no-spells-message">
            All available {{ currentSpellLevel === 0 ? 'cantrips' : `level ${currentSpellLevel} spells` }} are already added.
          </div>
          <div v-else v-for="spell in availableSpellsList" :key="spell.spell_id" class="spell-item" @click="addSpell(spell)">
            {{ spell.spell_name }}
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Fixed buttons container -->
  <div class="fixed-buttons-container">
    <div class="back-button-container">
      <button 
        class="navigation-button" 
        @click="backToDashboard"
      >
        Back to Dashboard
      </button>
    </div>
    <div class="save-button-container">
      <button 
        class="navigation-button" 
        @click="handleSave"
        :disabled="isSaving"
      >
        {{ isSaving ? 'Saving...' : 'Save Character' }}
      </button>
    </div>
  </div>
</template>
  
<script>
  import api from '../axios';
  import axios from 'axios';
  import AbilityScoreMethod from '../components/AbilityScoreMethod.vue';
  import HalfElfAbilityScore from '../components/HalfElfAbilityScore.vue';
  import ConfirmationDialog from '../components/ConfirmationDialog.vue';

  export default {
    name: 'CharacterSheet',
    components:{
      AbilityScoreMethod,
      HalfElfAbilityScore,
      ConfirmationDialog
    },
    props: {
      id: {
        type: [String, Number],
        default: null
      }
    },
    data() {
      return {
        showAbilityScoreMethod: true,
        showHalfElfAbilityScore: false,
        acManualModifier: 0,
        spellSaveDCManualModifier: 0, // Dodajem novu promenljivu za praćenje manualnih modifikacija spell save DC-a
        spellAttackBonusManualModifier: 0, // Dodajem novu promenljivu za praćenje manualnih modifikacija spell attack bonus-a
        spellSlots: {
          1: { total: 0, used: 0 },
          2: { total: 0, used: 0 },
          3: { total: 0, used: 0 },
          4: { total: 0, used: 0 },
          5: { total: 0, used: 0 },
          6: { total: 0, used: 0 },
          7: { total: 0, used: 0 },
          8: { total: 0, used: 0 },
          9: { total: 0, used: 0 }
        },
        // Definišemo samo podržane nivoe čarolija
        maxSpellLevel: 9,
        // Podaci za jedinstveni modal za čarolije
        showSpellModal: false,
        currentSpellLevel: 0,
        loadingSpells: false,
        availableSpellsList: [],
        // Postojeći podaci
        classes: [], // Lista klasa za selektor
        races: [], // Lista rasa za selektor
        backgrounds: [], // Lista pozadina za selektor
        subraces: [], // Lista podrasa za selektor
        backgroundVariant: '', // Varijanta pozadine trenutno izabrane pozadine
        previousBackground: '', // Pratimo prethodnu pozadinu
        previousBackgroundGold: 0, // Pamtimo zlato prethodne pozadine
        // Dodajemo nove promenljive za filtere
        selectedSpellClass: null, // Trenutno izabrana klasa za filtiranje čini
        selectedSpellType: null, // Trenutno izabrani tip magije
        spellTypes: ['Abjuration', 'Evocation', 'Necromancy', 'Transmutation', 'Conjuration', 'Divination', 'Enchantment', 'Illusion'], // Lista tipova
        // Ne čuvamo više pojedinačne liste čarolija
        character: {
          name: '',
          class: '',
          level: 1,
          background: '',
          backgroundVariant: '',
          playerName: '',
          race: '',
          subrace: '',
          alignment: '',
          experiencePoints: 0,
          hitDie: 0, // Dodajem hitDie
          hitDice: 1, // Dodajem hitDice za broj kockica
          abilities: {
            Strength: { score: 10, modifier: 0 },
            Dexterity: { score: 10, modifier: 0 },
            Constitution: { score: 10, modifier: 0 },
            Intelligence: { score: 10, modifier: 0 },
            Wisdom: { score: 10, modifier: 0 },
            Charisma: { score: 10, modifier: 0 }
          },
          baseRaceScores: {},
          pureRaceScores: {},
          baseAbilityScores: {},
          savingThrows: {
            Strength: { proficient: false, modifier: 0 },
            Dexterity: { proficient: false, modifier: 0 },
            Constitution: { proficient: false, modifier: 0 },
            Intelligence: { proficient: false, modifier: 0 },
            Wisdom: { proficient: false, modifier: 0 },
            Charisma: { proficient: false, modifier: 0 }
          },
          skills: {
            Acrobatics: { proficient: false, expertise: false, modifier: 0, ability: 'Dex', fromRace: false, fromBackground: false },
            'Animal Handling': { proficient: false, expertise: false, modifier: 0, ability: 'Wis', fromRace: false, fromBackground: false },
            Arcana: { proficient: false, expertise: false, modifier: 0, ability: 'Int', fromRace: false, fromBackground: false },
            Athletics: { proficient: false, expertise: false, modifier: 0, ability: 'Str', fromRace: false, fromBackground: false },
            Deception: { proficient: false, expertise: false, modifier: 0, ability: 'Cha', fromRace: false, fromBackground: false },
            History: { proficient: false, expertise: false, modifier: 0, ability: 'Int', fromRace: false, fromBackground: false },
            Insight: { proficient: false, expertise: false, modifier: 0, ability: 'Wis', fromRace: false, fromBackground: false },
            Intimidation: { proficient: false, expertise: false, modifier: 0, ability: 'Cha', fromRace: false, fromBackground: false },
            Investigation: { proficient: false, expertise: false, modifier: 0, ability: 'Int', fromRace: false, fromBackground: false },
            Medicine: { proficient: false, expertise: false, modifier: 0, ability: 'Wis', fromRace: false, fromBackground: false },
            Nature: { proficient: false, expertise: false, modifier: 0, ability: 'Int', fromRace: false, fromBackground: false },
            Perception: { proficient: false, expertise: false, modifier: 0, ability: 'Wis', fromRace: false, fromBackground: false },
            Performance: { proficient: false, expertise: false, modifier: 0, ability: 'Cha', fromRace: false, fromBackground: false },
            Persuasion: { proficient: false, expertise: false, modifier: 0, ability: 'Cha', fromRace: false, fromBackground: false },
            Religion: { proficient: false, expertise: false, modifier: 0, ability: 'Int', fromRace: false, fromBackground: false },
            'Sleight of Hand': { proficient: false, expertise: false, modifier: 0, ability: 'Dex', fromRace: false, fromBackground: false },
            Stealth: { proficient: false, expertise: false, modifier: 0, ability: 'Dex', fromRace: false, fromBackground: false },
            Survival: { proficient: false, expertise: false, modifier: 0, ability: 'Wis', fromRace: false, fromBackground: false }
          },
          proficiencyBonus: 2,
          profBonusModifier: 0,
          inspiration: {
            value: 0,
            proficient: false
          },
          hp: {
            max: 0,
            current: 0,
            temp: 0,
            base: 0
          },
          ac: 10,
          initiative: 0,
          speed: 30,
          deathSaves: {
            successes: [false, false, false],
            failures: [false, false, false]
          },
          currency: {
            cp: 0,
            sp: 0,
            ep: 0,
            gp: 0,
            pp: 0
          },
          equipment: '',
          personality: {
            traits: '',
            ideals: '',
            bonds: '',
            flaws: ''
          },
          raceFeatures: '',
          classFeatures: '',
          raceProficiency: '',
          classProficiency: '',
          attacks: [],
          spellcasting: {
            ability: '',
            saveDC: 8,
            attackBonus: 0,
            baseSaveDC: 8,
            baseAttackBonus: 0
          },
          passiveWisdom: 10,
          passiveWisdomBase: 10,
          passiveWisdomManualModifier: 0,
          age: '',
          height: '',
          weight: '',
          eyes: '',
          skin: '',
          hair: '',
          appearance: '',
          backstory: '',
          allies: '',
          symbolName: '',
          treasure: '',
          additionalFeatures: '',
          backgroundFeatures: '',
          appearanceImage: '',
          symbolImage: '',
          spells: {
            cantrips: [],
            level1: [],
            level2: [],
            level3: [],
            level4: [],
            level5: [],
            level6: [],
            level7: [],
            level8: [],
            level9: []
          },
          armor: '',
          hasShield: false,
        },
        abilities: [
          { name: 'Strength', short: 'Str' },
          { name: 'Dexterity', short: 'Dex' },
          { name: 'Constitution', short: 'Con' },
          { name: 'Intelligence', short: 'Int' },
          { name: 'Wisdom', short: 'Wis' },
          { name: 'Charisma', short: 'Cha' }
        ],
        skills: [
          { name: 'Acrobatics', ability: 'Dex' },
          { name: 'Animal Handling', ability: 'Wis' },
          { name: 'Arcana', ability: 'Int' },
          { name: 'Athletics', ability: 'Str' },
          { name: 'Deception', ability: 'Cha' },
          { name: 'History', ability: 'Int' },
          { name: 'Insight', ability: 'Wis' },
          { name: 'Intimidation', ability: 'Cha' },
          { name: 'Investigation', ability: 'Int' },
          { name: 'Medicine', ability: 'Wis' },
          { name: 'Nature', ability: 'Int' },
          { name: 'Perception', ability: 'Wis' },
          { name: 'Performance', ability: 'Cha' },
          { name: 'Persuasion', ability: 'Cha' },
          { name: 'Religion', ability: 'Int' },
          { name: 'Sleight of Hand', ability: 'Dex' },
          { name: 'Stealth', ability: 'Dex' },
          { name: 'Survival', ability: 'Wis' }
        ],
        selectableSkills: [], // Lista skillova koje korisnik može izabrati
        maxSelectableSkills: 0, // Maksimalan broj skillova koje korisnik može izabrati
        previousRaceBonus: 0, // Broj dodatnih izbora od prethodne rase
        previousClassChoices: 0, // Broj izbora od prethodne klase
        manualInitiative: false,
        initiativeModifier: 0,
        showProficiencyInfo: true,
        showPreparedSpellsInfo: true,
        previousOverlapCount: 0,
        isSaving: false,
        showNotification: false,
        notificationMessage: '',
        notificationType: 'success',
        // Dodajem stanja za konfirmacioni dijalog
        showConfirmationDialog: false,
        confirmationTitle: '',
        confirmationMessage: '',
        confirmationConfirmText: 'Yes',
        confirmationCancelText: 'No',
        confirmationAction: null,
        // Dodajem flag za praćenje da li je stranica promenjena
        hasUnsavedChanges: false,
      }
    },
    computed: {
      pointsSpent() {
        return this.calculatePointsSpent();
      },
      
      // Nema potrebe za pojedinačnim računatim svojstvima za dostupne čarolije 
      // jer sada koristimo centralizovanu availableSpellsList
      
      // Generisanje nivoa čarolija dinamički
      spellLevels() {
        const levels = [];
        // Dodajemo cantripove (nivo 0)
        levels.push({ level: 0, listKey: 'cantrips' });
        // Dodajemo ostale nivoe (1-9)
        for (let i = 1; i <= this.maxSpellLevel; i++) {
          levels.push({ level: i, listKey: `level${i}` });
        }
        return levels;
      },
      
      proficiencyBonus() {
        const level = this.character.level;
        if (level >= 17) return 6;
        if (level >= 13) return 5;
        if (level >= 9) return 4;
        if (level >= 5) return 3;
        return 2;
      },
      initiative() {
        return this.character.abilities.Dexterity.modifier;
      },
      passiveWisdomColorClass() {
        if (!this.character.passiveWisdomBase) {
          // Ako base nije postavljen, izračunaj ga
          this.character.passiveWisdomBase = this.calculateBasePassiveWisdom();
        }
        
        // Poredi sa baznom vrednošću
        if (this.character.passiveWisdomManualModifier > 0) return 'higher-value';
        if (this.character.passiveWisdomManualModifier < 0) return 'lower-value';
        return '';
      },
      profClass() {
        if (this.character.profBonusModifier > 0) return 'higher-value';
        return '';
      },
      selectedSkillsCount() {
        // Broji samo skill-ove koji su čekirani a nisu od rase ili background-a
        // i koji su u listi selektabilnih skillova
        return Object.entries(this.character.skills).filter(([name, skill]) => 
          skill.proficient && 
          !skill.fromRace && 
          !skill.fromBackground && 
          this.selectableSkills.includes(name)
        ).length;
      },
      
      // Generisanje nivoa čarolija dinamički
      spellLevels() {
        const levels = [];
        // Dodajemo cantripove (nivo 0)
        levels.push({ level: 0, listKey: 'cantrips' });
        // Dodajemo ostale nivoe (1-9)
        for (let i = 1; i <= this.maxSpellLevel; i++) {
          levels.push({ level: i, listKey: `level${i}` });
        }
        return levels;
      }
    },
    watch: {
      'character.level': {
        immediate: true,
        handler(newLevel, oldLevel) {
          this.updateProficiencyBonus();
          // Ako je hitDice veći od novog level-a, postavi ga na level
          if (this.character.hitDice > newLevel) {
            this.character.hitDice = newLevel;
          }
          
          // Update max HP when level changes - only add Constitution modifier
          if (this.character.class && oldLevel) {  // Only update if class is selected and level is changing
            const levelDiff = newLevel - oldLevel;
            const conMod = this.character.abilities.Constitution.modifier;
            // Add Constitution modifier for each new level
            this.character.hp.max += conMod * levelDiff;
            
            // Add Hill Dwarf bonus for each new level
            if (this.character.subrace === 'Hill Dwarf') {
              this.character.hp.max += levelDiff;
            }
            
            // Adjust current HP if it exceeds new max
            if (this.character.hp.current > this.character.hp.max) {
              this.character.hp.current = this.character.hp.max;
            }
            
            // Show notification about hit points when level changes
            if (newLevel > oldLevel && this.character.class) {
              this.showInfoNotification(`Remember to manually add hit points for your new level (${this.character.level}). Roll ${this.character.hitDie} or use the default value for your class.`);
            } else if (newLevel < oldLevel && this.character.class) {
              this.showInfoNotification(`Remember to manually reduce hit points as you decreased to level ${this.character.level}. Consider removing the average hit points (${Math.ceil(this.character.hitDie/2) + 1}) or your last roll value.`);
            }
          }
        }
      },
      'character.hitDice': {
        handler(newValue) {
          if (newValue > this.character.level) {
            this.character.hitDice = this.character.level;
          }
        }
      },
      'character.savingThrows': {
        deep: true,
        handler(newSavingThrows) {
          Object.keys(newSavingThrows).forEach(ability => {
            this.character.savingThrows[ability].modifier = this.calculateSavingThrowModifier(ability);
          });
        }
      },
      'character.skills': {
        deep: true,
        handler(newSkills) {
          Object.keys(newSkills).forEach(skill => {
            const ability = this.getAbilityForSkill(skill);
            this.updateSkillModifiers(ability);
          });
          // Update passive wisdom when perception changes
          this.updatePassiveWisdom();
        }
      },
      'character.abilities': {
        deep: true,
        handler() {
          // Ažuriraj spellcasting vrednosti kada se promene ability skorovi
          if (this.character.spellcasting.ability) {
            this.updateSpellcastingValues();
          }
        }
      },
      'character.race': {
        immediate: true,
        handler(newRace, oldRace) {
          // Preskači pozive kada se radi o učitanom karakteru
          if (this.id !== null) return;
          
          if (oldRace) {
            // Only remove Hill Dwarf bonus if we're changing from Dwarf to another race
            if (oldRace === 'Dwarf' && newRace !== 'Dwarf' && this.character.subrace === 'Hill Dwarf') {
              this.character.hp.max -= this.character.level;
              // Adjust current HP if it exceeds new max
              if (this.character.hp.current > this.character.hp.max) {
                this.character.hp.current = this.character.hp.max;
              }
            }
            
            // Remove previous race's overlap count from maxSelectableSkills
            this.maxSelectableSkills -= this.previousOverlapCount;
            this.previousOverlapCount = 0;
          }
          
          if (newRace) {
            this.fetchRaceDetails(newRace)
            
            // Oduzmi prethodni bonus od rase
            this.maxSelectableSkills -= this.previousRaceBonus;
            this.previousRaceBonus = 0;
            
            // Resetuj samo rasne proficiency-je
            Object.keys(this.character.skills).forEach(skill => {
              if (this.character.skills[skill].fromRace) {
                this.character.skills[skill].fromRace = false;
                // Ako skill nije proficient od background-a, resetuj i proficient flag
                if (!this.character.skills[skill].fromBackground) {
                  this.character.skills[skill].proficient = false;
                }
              }
            });
            
            let overlapCount = 0;
            
            // Postavi proficiency bonuse na osnovu rase
            if (newRace === 'Elf') {
              if (this.character.skills['Perception'].fromBackground) {
                overlapCount++;
              }
              this.character.skills['Perception'].proficient = true;
              this.character.skills['Perception'].fromRace = true;
            } else if (newRace === 'Half-Orc') {
              if (this.character.skills['Intimidation'].fromBackground) {
                overlapCount++;
              }
              this.character.skills['Intimidation'].proficient = true;
              this.character.skills['Intimidation'].fromRace = true;
            } else if (newRace === 'Half-Elf') {
              // Prikaži modal za izbor ability score-ova
              this.showHalfElfAbilityScore = true;
              // Za Half-Elf samo dodaj +2 na broj izbora
              this.previousRaceBonus = 2;
              this.maxSelectableSkills += this.previousRaceBonus;
            }
            
            // Povećaj broj izbora za svaki overlap
            this.previousOverlapCount = overlapCount;
            if (overlapCount > 0) {
              this.maxSelectableSkills += overlapCount;
            }
            
            // Update modifier nakon promene proficiency bonusa
            this.updateSkillModifiers('Wisdom');
            this.updateSkillModifiers('Charisma');
          }
        }
      },
      'character.subrace': {
        handler(newSubrace, oldSubrace) {
          // Preskači pozive kada se radi o učitanom karakteru
          if (this.id !== null) return;
          
          // Only handle Hill Dwarf HP bonus changes when changing subrace within Dwarf race
          if (this.character.race === 'Dwarf') {
            if (oldSubrace === 'Hill Dwarf' && newSubrace !== 'Hill Dwarf') {
              // Remove Hill Dwarf HP bonus when changing from Hill Dwarf
              this.character.hp.max -= this.character.level;
              // Adjust current HP if it exceeds new max
              if (this.character.hp.current > this.character.hp.max) {
                this.character.hp.current = this.character.hp.max;
              }
            } else if (newSubrace === 'Hill Dwarf' && oldSubrace !== 'Hill Dwarf') {
              // Add Hill Dwarf HP bonus when changing to Hill Dwarf
              this.character.hp.max += this.character.level;
            }
          }
          
          if (newSubrace) {
            this.applySubraceBonuses(newSubrace);
          }
        }
      },
      'character.class': {
        immediate: true,
        handler(newClass) {
          // Preskači pozive kada se radi o učitanom karakteru
          if (this.id !== null) return;
          
          if (newClass) {
            // Sačuvaj proficiency bonuse od rase i background-a
            const savedProficiencies = {};
            Object.keys(this.character.skills).forEach(skill => {
              if (this.character.skills[skill].fromRace || this.character.skills[skill].fromBackground) {
                savedProficiencies[skill] = {
                  fromRace: this.character.skills[skill].fromRace,
                  fromBackground: this.character.skills[skill].fromBackground
                };
              }
            });
            
            // Resetuj sve skillove na ne-proficient
            Object.keys(this.character.skills).forEach(skill => {
              this.character.skills[skill].proficient = false;
            });
            
            // Vrati sačuvane proficiency bonuse
            Object.keys(savedProficiencies).forEach(skill => {
              this.character.skills[skill].proficient = true;
              this.character.skills[skill].fromRace = savedProficiencies[skill].fromRace;
              this.character.skills[skill].fromBackground = savedProficiencies[skill].fromBackground;
            });
            
            this.fetchClassDetails(newClass)
          }
        }
      },
      'character.background': {
        immediate: true,
        handler(newBackground) {
          // Preskači pozive kada se radi o učitanom karakteru
          if (this.id !== null) return;
          
          if (newBackground) {
            this.fetchBackgroundDetails(newBackground);
          }
        }
      },
      'character.abilities.Dexterity.modifier': {
        handler() {
          this.updateAC();
        }
      },
      'character.abilities.Constitution.modifier': {
        handler(newMod, oldMod) {
          if (this.character.class) {  // Only update if class is selected
            if (oldMod !== undefined) {  // If modifier is changing (not initial setup)
              const modDiff = newMod - oldMod;
              // Add the difference multiplied by level to max HP
              this.character.hp.max += modDiff * this.character.level;
              
              // Adjust current HP if it exceeds new max
              if (this.character.hp.current > this.character.hp.max) {
                this.character.hp.current = this.character.hp.max;
              }
            }
          }
        }
      }
    },
    created() {
      this.fetchClasses();
      this.fetchRaces();
      this.fetchBackgrounds();
      
      // Ako postoji ID, učitaj karakter
      if (this.id) {
        this.loadCharacter();
        this.showAbilityScoreMethod = false;
      } else {
        // Za nove karaktere, inicijalizuj praćenje promena
        this.setupChangeTracking();
      }
      
      // Dodaj event listener za beforeunload (zatvaranje taba/browsera)
      window.addEventListener('beforeunload', this.handleBeforeUnload);
    },
    beforeUnmount() {
      // Ukloni event listener kada se komponenta unmount-uje
      window.removeEventListener('beforeunload', this.handleBeforeUnload);
    },
    async mounted() {
      // Učitaj čarolije za sve nivoe koristeći maxSpellLevel parametar
      for (let level = 0; level <= this.maxSpellLevel; level++) {
        await this.fetchSpellsForLevel(level);
      }
      
      // Ako je učitan karakter sa rasom, dohvatimo podrase za tu rasu
      if (this.id && this.character.race) {
        try {
          const response = await axios.get(`http://localhost:5000/api/races/name/${encodeURIComponent(this.character.race)}`);
          if (response.data && response.data.id) {
            // Dohvatimo podrase bez postavljanja character.subrace
            const subraceResponse = await axios.get(`http://localhost:5000/api/races/${response.data.id}/subraces`);
            this.subraces = subraceResponse.data;
          }
        } catch (error) {
          console.error('Greška prilikom dohvatanja podrasa za učitani karakter:', error);
          this.subraces = [];
        }
      }
    },
    methods: {
      // Metode za rad sa ability scores
      updateCharacterAbilityScore({ ability, value }) {
        // Ažuriraš trenutno stanje karaktera
        this.character.abilities[ability].score = value;
        
        // Inicijalizacija baseAbilityScores
        if (!this.character.baseAbilityScores[ability]) {
          this.character.baseAbilityScores[ability] = value;
        } else {
          // Ažuriranje base vrendnosti
          this.character.baseAbilityScores[ability] = value;
        }

        this.calculateModifier(ability);
      },
      onAbilitiesConfirmed() {
        this.showAbilityScoreMethod = false;
      },
      adjustSlot(amount, level) {
        const newTotal = this.spellSlots[level].total + amount;
        if (newTotal >= 0) {
          this.spellSlots[level].total = newTotal;
          // Proveri da li je used veći od novog total-a i prilagodi ako jeste
          if (this.spellSlots[level].used > newTotal) {
            this.spellSlots[level].used = newTotal;
          }
        }
      },
      adjustUsedSlot(amount, level) {
        const newUsed = this.spellSlots[level].used + amount;
        if (newUsed >= 0 && newUsed <= this.spellSlots[level].total) {
          this.spellSlots[level].used = newUsed;
        }
      },
      async fetchClasses() {
        try {
          const response = await api.get('/classes');
          this.classes = response.data;
        } catch (error) {
          console.error('Greška prilikom učitavanja klasa:', error);
        }
      },
      async fetchRaces() {
        try {
          const response = await api.get('/races');
          this.races = response.data;
        } catch (error) {
          console.error('Greška prilikom učitavanja rasa:', error);
        }
      },
      async fetchBackgrounds() {
        try {
          const response = await api.get('/backgrounds');
          this.backgrounds = response.data;
        } catch (error) {
          console.error('Greška prilikom učitavanja pozadina:', error);
        }
      },
      async fetchBackgroundDetails(backgroundName) {
        try {
          const response = await api.get(`/backgrounds/name/${encodeURIComponent(backgroundName)}`);
          const backgroundData = response.data;
          
          // Reset background variant
          this.character.backgroundVariant = '';
          
          // Preskačemo deo koji menja podatke ako se radi o učitanom karakteru
          if (this.id !== null) {
            // Samo postavimo backgroundVariant ako se radi o učitanom karakteru
            this.backgroundVariant = backgroundData.variant || '';
            return;
          }
          
          // Update background features
          let featuresText = '';
          
          // Add the features from the background
          if (backgroundData.features) {
            featuresText += `Features:\n${backgroundData.features}\n\n`;
          }
          
          // Add the skills proficiencies
          if (backgroundData.skill_proficiencies) {
            featuresText += `Skill Proficiencies:\n${backgroundData.skill_proficiencies}\n\n`;
            
            // Remove previous background's overlap count
            this.maxSelectableSkills -= this.previousOverlapCount;
            this.previousOverlapCount = 0;
            
            // Resetuj samo background proficiency-je
            Object.keys(this.character.skills).forEach(skill => {
              if (this.character.skills[skill].fromBackground) {
                this.character.skills[skill].fromBackground = false;
                // Ako skill nije proficient od rase, resetuj i proficient flag
                if (!this.character.skills[skill].fromRace) {
                  this.character.skills[skill].proficient = false;
                }
              }
            });
            
            // Primeni nove background proficiency-je
            const skills = backgroundData.skill_proficiencies.split(',').map(s => s.trim());
            let overlapCount = 0;
            
            skills.forEach(skill => {
              // Provera da li skill već postoji u karakteru
              const foundSkill = Object.keys(this.character.skills).find(
                s => s.toLowerCase() === skill.toLowerCase()
              );
              
              if (foundSkill) {
                // Ako je skill već proficient od rase, povećaj broj izbora
                if (this.character.skills[foundSkill].fromRace) {
                  overlapCount++;
                }
                this.character.skills[foundSkill].proficient = true;
                this.character.skills[foundSkill].fromBackground = true;
              }
            });
            
            // Update overlap count i maxSelectableSkills
            this.previousOverlapCount = overlapCount;
            if (overlapCount > 0) {
              this.maxSelectableSkills += overlapCount;
            }
            
            // Ažuriraj modifier
            skills.forEach(skill => {
              const foundSkill = Object.keys(this.character.skills).find(
                s => s.toLowerCase() === skill.toLowerCase()
              );
              if (foundSkill) {
                const ability = this.getAbilityForSkill(foundSkill);
                if (ability) this.updateSkillModifiers(ability);
              }
            });
          }
          
          // Add tool proficiencies if present
          if (backgroundData.tool_proficiencies) {
            featuresText += `Tool Proficiencies:\n${backgroundData.tool_proficiencies}\n\n`;
          }
          
          // Add languages if present
          if (backgroundData.languages) {
            featuresText += `Languages:\n${backgroundData.languages}\n\n`;
          }
          
          // Update the background features text area
          this.character.backgroundFeatures = featuresText.replace(/\s+$/g, '');
          
          // If available, update personality traits, ideals, bonds, and flaws
          if (backgroundData.personality_trait) {
            this.character.personality.traits = backgroundData.personality_trait;
          }
          if (backgroundData.ideal) {
            this.character.personality.ideals = backgroundData.ideal;
          }
          if (backgroundData.bond) {
            this.character.personality.bonds = backgroundData.bond;
          }
          if (backgroundData.flaw) {
            this.character.personality.flaws = backgroundData.flaw;
          }
          
          // Dodaj opremu pozadine u equipment
          if (backgroundData.starting_equipment) {
            let newEquipment = '';
            const equipmentText = this.character.equipment;
            
            // Izvuci samo Class equipment deo (ako postoji)
            if (equipmentText.includes('Class equipment:')) {
              // Uzimamo samo deo od početka do "Background equipment:" (ako postoji)
              const classEndIndex = equipmentText.indexOf('Background equipment:');
              if (classEndIndex !== -1) {
                newEquipment = equipmentText.substring(0, classEndIndex).trim();
              } else {
                newEquipment = equipmentText.trim();
              }
              // Dodaj prazan red samo ako imamo Class equipment
              newEquipment += "\n\n";
            }
            
            // Dodaj novu opremu pozadine
            newEquipment += "Background equipment:\n" + backgroundData.starting_equipment;
            
            this.character.equipment = newEquipment;
          }
          
          // Automatski dodaj zlato iz pozadine
          if (backgroundData.starting_gold) {
            // Ako menjamo pozadinu, oduzmi zlato prethodne pozadine
            if (this.previousBackground && this.previousBackground !== backgroundName && this.previousBackgroundGold > 0) {
              this.character.currency.gp -= this.previousBackgroundGold;
            }
            
            // Dodaj zlato nove pozadine
            this.character.currency.gp += backgroundData.starting_gold;
            
            // Zapamti trenutnu pozadinu i zlato
            this.previousBackground = backgroundName;
            this.previousBackgroundGold = backgroundData.starting_gold;
          }
          
          // Učitaj podatak o varijanti
          this.backgroundVariant = backgroundData.variant || '';
          
        } catch (error) {
          console.error('Greška prilikom dohvatanja podataka o pozadini:', error);
        }
      },
      calculateModifier(abilityName) {
        const score = this.character.abilities[abilityName].score
        const modifier = Math.floor((score - 10) / 2)
        this.character.abilities[abilityName].modifier = modifier
        
        // Update saving throws
        this.character.savingThrows[abilityName].modifier = this.calculateSavingThrowModifier(abilityName)
        
        // Update skills
        this.updateSkillModifiers(abilityName)
        
        // Update passive wisdom when Wisdom modifier changes
        if (abilityName === 'Wisdom') {
          this.updatePassiveWisdom();
        }

        // Update initiative when Dexterity changes
        if (abilityName === 'Dexterity') {
          this.character.initiative = modifier + (this.character.initiativeModifier || 0);
        }
      },
      calculateSavingThrowModifier(abilityName) {
        const baseModifier = this.character.abilities[abilityName].modifier
        // Koristi character.proficiencyBonus koji može biti manuelno modifikovan
        const proficiency = this.character.savingThrows[abilityName].proficient ? this.character.proficiencyBonus : 0
        const manualModifier = this.character.savingThrows[abilityName].manualModifier || 0
        const total = parseInt(baseModifier) + proficiency + manualModifier
        return this.formatModifier(total)
      },
      updateSkillModifiers(abilityName) {
        Object.entries(this.character.skills).forEach(([skillName, skill]) => {
          if (this.getAbilityShortName(abilityName) === skill.ability) {
            const baseModifier = this.character.abilities[abilityName].modifier
            let proficiency = 0;
            if (skill.proficient) {
              // Koristimo character.proficiencyBonus koji može biti manuelno modifikovan
              proficiency = skill.expertise ? this.character.proficiencyBonus * 2 : this.character.proficiencyBonus;
            }
            const manualModifier = skill.manualModifier || 0
            const total = parseInt(baseModifier) + proficiency + manualModifier
            skill.modifier = this.formatModifier(total)
          }
        })
      },
      getAbilityShortName(abilityName) {
        const ability = this.abilities.find(a => a.name === abilityName)
        return ability ? ability.short : ''
      },
      addAttack() {
        this.character.attacks.push({
          name: '',
          bonus: '',
          damage: ''
        })
      },
      deleteAttack(index) {
        this.character.attacks.splice(index, 1);
      },
      formatModifier(mod) {
        if (mod > 0) return `+${mod}`;
        if (mod < 0) return `${mod}`;
        return '0';
      },
      onAbilityInput(abilityName) {
        let val = this.character.abilities[abilityName].score;
        if (val < 0) val = 0;
        if (val > 20) val = 20;
        this.character.abilities[abilityName].score = val;
        this.calculateModifier(abilityName);
      },
      async onImageChange(event, key) {
        const file = event.target.files[0];
        if (!file) return;

        try {
          // Kreiraj FormData za upload
          const formData = new FormData();
          formData.append('image', file);

          // Pošalji sliku na server
          const response = await axios.post('http://localhost:5000/api/upload-image', 
            formData, 
            {
              headers: {
                'Content-Type': 'multipart/form-data',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              }
            }
          );

          if (response.data.success) {
            // Sačuvaj putanju do slike umesto Base64 podataka
            this.character[key] = response.data.image_path;
          } else {
            console.error('Upload failed:', response.data.error);
            this.showErrorNotification('Neuspešan upload slike.');
          }
        } catch (error) {
          console.error('Error uploading image:', error);
          this.showErrorNotification('Greška prilikom uploada slike.');
        }
      },

      updateAllModifiers() {
        // Update saving throws
        Object.keys(this.character.savingThrows).forEach(ability => {
          this.character.savingThrows[ability].modifier = this.calculateSavingThrowModifier(ability);
        });
        
        // Update skills
        Object.keys(this.character.skills).forEach(skill => {
          this.updateSkillModifiers(this.getAbilityForSkill(skill));
        });
      },
      getAbilityForSkill(skillName) {
        const skill = this.character.skills[skillName];
        return Object.keys(this.character.abilities).find(ability => 
          this.getAbilityShortName(ability) === skill.ability
        );
      },
      updatePassiveWisdom() {
        // Umesto računanja komponenti, koristimo direktno vrednost Perception skilla
        // jer ona već uključuje sve relevantne bonuse (ability mod, proficiency, expertise, manual mod)
        const perceptionValue = parseInt(this.character.skills['Perception'].modifier);
        
        // Passive Wisdom (Perception) je 10 + Perception modifier
        const baseValue = 10 + perceptionValue;
        this.character.passiveWisdomBase = baseValue;
        
        // Dodaj dodatni manuelni modifier za passive wisdom ako postoji
        this.character.passiveWisdom = baseValue + (this.character.passiveWisdomManualModifier || 0);
      },
      calculateBasePassiveWisdom() {
        // Koristimo direktno vrednost Perception skilla koja već uključuje sve modifikatore
        const perceptionValue = parseInt(this.character.skills['Perception'].modifier);
        return 10 + perceptionValue;
      },
      adjustPassiveWisdom(amount) {
        // Ako ne postoji manual modifier, inicijalizuj ga
        if (!this.character.passiveWisdomManualModifier) {
          this.character.passiveWisdomManualModifier = 0;
        }
        
        // Ažuriraj manualni modifikator
        this.character.passiveWisdomManualModifier += amount;
        
        // Ažuriraj ukupnu vrednost
        this.updatePassiveWisdom();
      },
      getAbilityScoreColorClass(abilityName) {
        const current = this.character.abilities[abilityName].score;
        const base = this.character.baseRaceScores[abilityName];

        if (base === undefined) return ''; // još nije inicijalizovano

        if (current > base) return 'higher-value';
        if (current < base) return 'lower-value';
        return '';
      },
      adjustAbilityScore(abilityName, amount) {
        const newValue = this.character.abilities[abilityName].score + amount;
        if (newValue >= 0 && newValue <= 20) {
          this.character.abilities[abilityName].score = newValue;
          this.calculateModifier(abilityName);
        }
      },
      adjustCurrentHP(amount) {
        this.character.hp.current += amount;
        this.validateCurrentHP();
      },
      validateCurrentHP() {
        if (this.character.hp.current < 0) {
          this.character.hp.current = 0;
        }
        if (this.character.hp.current > this.character.hp.max) {
          this.character.hp.current = this.character.hp.max;
        }
      },
      parseAbilityScoreIncrease(abilityScoreStr) {
        const increases = {};
        const parts = abilityScoreStr.split(',');
        
        parts.forEach(part => {
          const trimmed = part.trim();
          if (trimmed.includes('plus two other ability scores')) {
            // Poseban slučaj za Half-Elf
            increases['HalfElf'] = true;
          } else if (trimmed.includes('All ability scores')) {
            // Poseban slučaj za Human
            this.abilities.forEach(ability => {
              increases[ability.name] = 1;
            });
          } else {
            const match = trimmed.match(/(\w+)\s*\+\s*(\d+)/);
            if (match) {
              const [_, ability, value] = match;
              increases[ability] = parseInt(value);
            }
          }
        });
        
        return increases;
      },
      async fetchRaceDetails(raceName) {
        try {
          const response = await axios.get(`http://localhost:5000/api/races/name/${encodeURIComponent(raceName)}`)
          const raceData = response.data
          
          // Postavi brzinu
          this.character.baseSpeed = raceData.speed;
          this.character.speed = raceData.speed;

          // Postavi race traits
          this.character.raceFeatures = raceData.traits

          // Postavi race proficiencies & languages
          this.character.raceProficiencies = 'Languages:\n' + raceData.languages
          if (raceData.proficiency) {
            this.character.raceProficiencies += '\n\nProficiencies:\n' + raceData.proficiency
          }

          // Preskočimo resetovanje ability skorova i primenu racial bonusa ako se radi o učitanom karakteru
          if (this.id === null) {
            // Resetuj ability scores na osnovne vrednosti
            this.abilities.forEach(ability => {
              const baseValue = this.character.baseAbilityScores[ability.name] || 10;
              this.character.abilities[ability.name].score = baseValue;
              this.calculateModifier(ability.name);
            });

            // Postavi ability score increases
            const increases = this.parseAbilityScoreIncrease(raceData.ability_score_increase);
            
            // Standardni slučaj za ostale rase
            Object.entries(increases).forEach(([ability, value]) => {
              if (this.character.abilities[ability]) {
                this.character.abilities[ability].score += value;
                this.calculateModifier(ability);
              }
            });

            // Sačuvaj osnovne vrednosti nakon dodate rase
            this.abilities.forEach(ability => {
              this.character.pureRaceScores[ability.name] = this.character.abilities[ability.name].score;
              this.character.baseRaceScores[ability.name] = this.character.abilities[ability.name].score;
            });
          }

          // Dohvati podrase za izabranu rasu samo ako se radi o novom karakteru
          if (this.id === null) {
            this.fetchSubraces(raceData.id);
          }
        } catch (error) {
          console.error('Greška prilikom dohvatanja podataka o rasi:', error)
        }
      },
      async fetchSubraces(raceId) {
        try {
          const response = await axios.get(`http://localhost:5000/api/races/${raceId}/subraces`)
          this.subraces = response.data
          // Resetuj subrace kada se promeni rasa
          this.character.subrace = ''
        } catch (error) {
          console.error('Greška prilikom dohvatanja podrasa:', error)
          this.subraces = []
        }
      },
      async applySubraceBonuses(subraceName) {
        const subrace = this.subraces.find(s => s.name === subraceName)
        if (subrace) {
          // Resetuj i postavi novi tekst za subrace features
          this.character.raceFeatures = this.character.raceFeatures.split('\n\nSubrace Features & Traits:')[0];
          this.character.raceFeatures += '\n\nSubrace Features & Traits:\n' + subrace.traits;

          // Resetuj i postavi novi tekst za subrace proficiencies
          this.character.raceProficiencies = this.character.raceProficiencies.split('\n\nSubrace Proficiencies:')[0];
          if (subrace.proficiency) {
            this.character.raceProficiencies += '\n\nSubrace Proficiencies:\n' + subrace.proficiency;
          }

          // Vrati ability scores na base + rase vrednosti
          this.abilities.forEach(ability => {
            this.character.abilities[ability.name].score = this.character.baseRaceScores[ability.name];
            this.calculateModifier(ability.name);
          });

          // Primeni nove subrace bonuse
          const subraceIncreases = this.parseAbilityScoreIncrease(subrace.ability_score_increase);
          Object.entries(subraceIncreases).forEach(([ability, value]) => {
            if (this.character.abilities[ability]) {
              this.character.abilities[ability].score += value;
              this.calculateModifier(ability);
            }
          });

          // Sačuvaj nove osnovne vrednosti nakon subrace bonusa
          this.abilities.forEach(ability => {
            this.character.baseRaceScores[ability.name] = this.character.abilities[ability.name].score;
          });
        }
        // Resetuj brzinu na standardnu vrednost za rasu
        if (this.character.race === 'Elf') {
          this.character.baseSpeed = 30;
          this.character.speed = 30;
        }
        
        // Postavi brzinu na 35 samo za Wood Elf
        if (subraceName === 'Wood Elf'){
          this.character.baseSpeed = 35;
          this.character.speed = 35;
        }
      },
      async fetchClassDetails(className) {
        try {
          const response = await api.get(`/classes/name/${encodeURIComponent(className)}`);
          const classData = response.data;
          
          // Preskačemo deo koji resetuje podatke ako se radi o učitanom karakteru
          if (this.id === null) {
            // Oduzmi prethodni broj izbora od klase
            this.maxSelectableSkills -= this.previousClassChoices;
            
            // Postavi hit die
            this.character.hitDie = classData.hit_die;

            // Postavi max hp - uključi Hill Dwarf bonus ako je izabran
            let initialHP = classData.hit_die + this.character.abilities.Constitution.modifier * this.character.level;
            if (this.character.subrace === 'Hill Dwarf') {
              initialHP += 1; // Dodaj Hill Dwarf bonus za prvi nivo
            }
            this.character.hp.max = initialHP;
          }

          // Postavi spellcasting ability ako postoji i ako klasa ima magiju
          if (classData.spellcasting && classData.spellcasting_ability) {
            this.character.spellcasting.ability = classData.spellcasting_ability;
            this.updateSpellcastingValues();
          } else {
            this.character.spellcasting.ability = '';
            this.updateSpellcastingValues();
          }
          
          // Postavi saving throw proficiencies samo ako se radi o novom karakteru
          if (this.id === null && classData.saving_throws) {
            // Prvo resetuj sve saving throws na false
            Object.keys(this.character.savingThrows).forEach(ability => {
              this.character.savingThrows[ability].proficient = false;
            });
            
            // Zatim postavi true za saving throws koje klasa ima
            const savingThrows = classData.saving_throws.split(',').map(s => s.trim());
            savingThrows.forEach(ability => {
              if (this.character.savingThrows[ability]) {
                this.character.savingThrows[ability].proficient = true;
              }
            });
          }

          // Resetuj i postavi selectable skills samo ako se radi o novom karakteru
          if (this.id === null) {
            if (className === 'Bard') {
              // Za Barda, svi skillovi su selectable
              this.selectableSkills = Object.keys(this.character.skills);
              this.previousClassChoices = parseInt(classData.num_skills) || 0;
              this.maxSelectableSkills += this.previousClassChoices;
            } else if (classData.skill_choices) {
              const skillChoices = classData.skill_choices.split(',').map(s => s.trim());
              this.selectableSkills = skillChoices;
              this.previousClassChoices = parseInt(classData.num_skills) || 0;
              this.maxSelectableSkills += this.previousClassChoices;
            }
          }

          // Resetuj class proficiencies i dodaj nove samo ako se radi o novom karakteru
          if (this.id === null) {
            this.character.classProficiencies = '';
            
            if (classData.armor_proficiencies) {
              this.character.classProficiencies += 'Armor Proficiencies:\n' + classData.armor_proficiencies;
            }
            
            if (classData.weapon_proficiencies) {
              this.character.classProficiencies += (this.character.classProficiencies ? '\n\n' : '') + 
                'Weapon Proficiencies:\n' + classData.weapon_proficiencies;
            }
            
            if (classData.tool_proficiencies) {
              this.character.classProficiencies += (this.character.classProficiencies ? '\n\n' : '') + 
                'Tool Proficiencies:\n' + classData.tool_proficiencies;
            }

            // Postavi class features
            if (classData.class_features) {
              this.character.classFeatures = classData.class_features;
            }

            // Postavi starting equipment
            if (classData.starting_equipment) {
              // Izdvoji deo opreme koji pripada backgroundu ako postoji
              const equipmentText = this.character.equipment;
              const backgroundEquipment = equipmentText.includes('Background equipment:') 
                ? equipmentText.substring(equipmentText.indexOf('Background equipment:')) 
                : '';
              
              // Dodaj opremu klase
              this.character.equipment = "Class equipment:\n" + "Choose between (a), (b) or (c):\n" + classData.starting_equipment;
              
              // Dodaj opremu pozadine ako postoji
              if (backgroundEquipment) {
                this.character.equipment += "\n\n" + backgroundEquipment;
              }
            }
          }
          
        } catch (error) {
          console.error('Greška prilikom dohvatanja podataka o klasi:', error);
        }
      },
      validateLevel() {
        if (this.character.level < 1) {
          this.character.level = 1;
        } else if (this.character.level > 20) {
          this.character.level = 20;
        }
      },
      validateHP() {
        if (this.character.hp.max < 0) {
          this.character.hp.max = 0;
        }
        if (this.character.hp.temp < 0) {
          this.character.hp.temp = 0;
        }
      },
      resetSelectableSkills() {
        // Sačuvaj proficiency bonuse od rase i background-a
        const savedProficiencies = {};
        Object.keys(this.character.skills).forEach(skill => {
          if (this.character.skills[skill].fromRace || this.character.skills[skill].fromBackground) {
            savedProficiencies[skill] = {
              fromRace: this.character.skills[skill].fromRace,
              fromBackground: this.character.skills[skill].fromBackground
            };
          }
        });
        
        // Resetuj sve skillove na ne-proficient
        Object.keys(this.character.skills).forEach(skill => {
          this.character.skills[skill].proficient = false;
        });
        
        // Vrati sačuvane proficiency bonuse
        Object.keys(savedProficiencies).forEach(skill => {
          this.character.skills[skill].proficient = true;
          this.character.skills[skill].fromRace = savedProficiencies[skill].fromRace;
          this.character.skills[skill].fromBackground = savedProficiencies[skill].fromBackground;
        });
        
        this.selectableSkills = [];
        this.selectedSkillsCount = 0;
        this.maxSelectableSkills = 0;
        this.previousRaceBonus = 0;
        this.previousClassChoices = 0;
      },
      isSkillSelectable(skillName) {
        // Ako skill nije u listi izboriva, nije selectable
        if (!this.selectableSkills.includes(skillName)) return false;
        
        // Ako je skill već proficient zbog rase ili background-a, nije selectable (već je čekiran)
        if (this.character.skills[skillName].fromRace || this.character.skills[skillName].fromBackground) return false;
        
        // Broj izabranih skillova samo iz selectableSkills liste, isključujući one od rase i background-a
        const selectedCount = this.selectableSkills.filter(skill => 
          this.character.skills[skill].proficient && 
          !this.character.skills[skill].fromRace && 
          !this.character.skills[skill].fromBackground
        ).length;
        
        // Ako je dostignut broj izabranih skillova, nijedan skill nije selectable
        if (selectedCount >= this.previousClassChoices) return false;
        
        // Inače je selectable
        return true;
      },
      toggleSkillProficiency(skillName) {
        // Ako skill nije u listi izboriva ili je dobijen od rase ili backgrounda, ne može se menjati
        if (!this.selectableSkills.includes(skillName) || 
            this.character.skills[skillName].fromRace || 
            this.character.skills[skillName].fromBackground) return;

        const skill = this.character.skills[skillName];
        
        // Ako skill nije proficient (pokušavamo da ga čekiramo) ali smo već izabrali maksimalan broj, prekinemo
        if (!skill.proficient && this.selectedSkillsCount >= this.previousClassChoices) {
            return;
        }

        skill.proficient = !skill.proficient;
        this.updateSkillModifiers(this.getAbilityForSkill(skillName));
      },
      
      adjustSavingThrowModifier(abilityName, amount) {
        if (!this.character.savingThrows[abilityName].manualModifier) {
          this.character.savingThrows[abilityName].manualModifier = 0;
        }
        this.character.savingThrows[abilityName].manualModifier += amount;
        this.character.savingThrows[abilityName].modifier = this.calculateSavingThrowModifier(abilityName);
      },
      
      adjustSkillModifier(skillName, amount) {
        if (!this.character.skills[skillName].manualModifier) {
          this.character.skills[skillName].manualModifier = 0;
        }
        this.character.skills[skillName].manualModifier += amount;
        const abilityName = this.getAbilityForSkill(skillName);
        this.updateSkillModifiers(abilityName);
      },
      calculateBaseSavingThrowModifier(abilityName) {
        const baseModifier = this.character.abilities[abilityName].modifier;
        const proficiency = this.character.savingThrows[abilityName].proficient ? this.character.proficiencyBonus : 0;
        return baseModifier + proficiency;
      },
      calculateBaseSkillModifier(skillName) {
        const skill = this.character.skills[skillName];
        const abilityName = this.getAbilityForSkill(skillName);
        const baseModifier = this.character.abilities[abilityName].modifier;
        let proficiency = 0;
        
        if (skill.proficient) {
          proficiency = skill.expertise ? this.character.proficiencyBonus * 2 : this.character.proficiencyBonus;
        }
        
        return baseModifier + proficiency;
      },
      getModifierColorClass(type, name) {
        if (type === 'initiative') {
          const manualModifier = this.character.initiativeModifier;
          if (manualModifier > 0) return 'higher-value';
          if (manualModifier < 0) return 'lower-value';
          return '';
        }
        
        if (type === 'ac') {
          const dexMod = this.character.abilities.Dexterity.modifier;
          let baseAC = 10; // Default AC when no armor

          // Calculate expected AC based on armor type
          switch(this.character.armor) {
            case 'padded':
            case 'leather':
              baseAC = 11 + dexMod;
              break;
            case 'studded':
              baseAC = 12 + dexMod;
              break;
            case 'hide':
              baseAC = 12 + Math.min(dexMod, 2);
              break;
            case 'chain_shirt':
              baseAC = 13 + Math.min(dexMod, 2);
              break;
            case 'scale_mail':
            case 'breastplate':
              baseAC = 14 + Math.min(dexMod, 2);
              break;
            case 'half_plate':
              baseAC = 15 + Math.min(dexMod, 2);
              break;
            case 'ring_mail':
              baseAC = 14;
              break;
            case 'chain_mail':
              baseAC = 16;
              break;
            case 'splint':
              baseAC = 17;
              break;
            case 'plate':
              baseAC = 18;
              break;
            default:
              baseAC = 10 + dexMod;
          }

          // Add shield bonus if equipped
          if (this.character.hasShield) {
            baseAC += 2;
          }

          if (this.character.ac > baseAC) return 'higher-value';
          if (this.character.ac < baseAC) return 'lower-value';
          return '';
        }
        
       if (type === 'speed') {
          const baseSpeed = this.character.baseSpeed ?? 30; // koristi baseSpeed iz karaktera ako postoji, inače je 30

          if (this.character.speed > baseSpeed) return 'higher-value';
          if (this.character.speed < baseSpeed) return 'lower-value';
          return '';
        }
        
        const baseModifier = type === 'savingThrow' 
          ? this.calculateBaseSavingThrowModifier(name)
          : this.calculateBaseSkillModifier(name);
        
        const manualModifier = type === 'savingThrow'
          ? this.character.savingThrows[name].manualModifier
          : this.character.skills[name].manualModifier;

        if (manualModifier > 0) return 'higher-value';
        if (manualModifier < 0) return 'lower-value';
        return '';
      },
      adjustInitiative(amount) {
        if (!this.character.initiativeModifier) {
          this.character.initiativeModifier = 0;
        }
        this.character.initiativeModifier += amount;
        this.character.initiative = this.character.abilities.Dexterity.modifier + this.character.initiativeModifier;
      },
      adjustAC(amount) {
        this.acManualModifier += amount; // Ažuriramo manualni modifier
        this.updateAC(); // Pozivamo updateAC da primeni promene
      },
      adjustSpeed(amount) {
        this.character.speed += amount;
      },
      adjustInspiration(amount) {
        const newValue = this.character.inspiration.value + amount;
        if (newValue >= 0) {
          this.character.inspiration.value = newValue;
        }
      },
      adjustMaxHP(amount) {
        if (!this.character.class) return;  // Don't allow manual HP adjustment before class selection
        
        let newValue = this.character.hp.max + amount;
        if (newValue < 0) {
          newValue = 0;
        }
        this.character.hp.max = newValue;

        // Ako je trenutni HP veći od maksimalnog, smanji ga na maksimalni
        if (this.character.hp.current > this.character.hp.max) {
          this.character.hp.current = this.character.hp.max;
        }
      },
      adjustTempHP(amount) {
        let newValue = this.character.hp.temp + amount;
        if (newValue < 0) {
          newValue = 0;
        }
        this.character.hp.temp = newValue;
      },
      adjustLevel(amount) {
        // Proveri da li je klasa izabrana pre nego što dozvoli promenu levela
        if (!this.character.class) {
          this.showInfoNotification("Please select a character class before adjusting level. Your class choice determines important features like hit dice and proficiencies.");
          return;
        }
        
        const newLevel = this.character.level + amount;
        if (newLevel >= 1 && newLevel <= 20) {
          this.character.level = newLevel;
        }
      },
      adjustHitDice(amount) {
        const newHitDice = this.character.hitDice + amount;
        if (newHitDice >= 0 && newHitDice <= this.character.level) {
          this.character.hitDice = newHitDice;
        }
      },
      validateExperiencePoints(event) {
        this.character.experiencePoints = event.target.value.replace(/[^0-9\-\/]/g, '');
      },
      validateCurrency(event, type) {
        const value = event.target.value;
        if (value === '') {
          this.character.currency[type] = '';
        } else {
          this.character.currency[type] = value.replace(/[^0-9]/g, '');
        }
      },
      adjustProf(amount) {
        // Ako pokušavamo da povećamo, a već je povećan za 1, ne radimo ništa
        if (amount > 0 && this.character.profBonusModifier >= 1) return;
        
        // Ako pokušavamo da smanjimo, a već smo na osnovnoj vrednosti, ne radimo ništa
        if (amount < 0 && this.character.profBonusModifier <= 0) return;
        
        // Inače, primenjujemo promenu
        this.character.profBonusModifier += amount;
        this.updateProficiencyBonus();
      },
      updateProficiencyBonus() {
        // Base proficiency bonus based on level
        let baseBonus = 2;
        const level = this.character.level;
        if (level >= 17) baseBonus = 6;
        else if (level >= 13) baseBonus = 5;
        else if (level >= 9) baseBonus = 4;
        else if (level >= 5) baseBonus = 3;
        
        // Apply modifier
        this.character.proficiencyBonus = baseBonus + this.character.profBonusModifier;
        
        // Update skills and saving throws
        this.updateAllModifiers();
        
        // Update passive wisdom specifically
        this.updatePassiveWisdom();
        
        // Update spellcasting values (spell save DC and spell attack bonus)
        if (this.character.spellcasting.ability) {
          this.updateSpellcastingValues();
        }
      },
      // Generička funkcija za uklanjanje info poruka sa animacijom
      removeInfoElement(selector, propertyToUpdate = null) {
        const infoElement = document.querySelector(selector);
        if (infoElement) {
          infoElement.style.opacity = '0';
          setTimeout(() => {
            if (propertyToUpdate) {
              this[propertyToUpdate] = false;
            } else {
              infoElement.style.display = 'none';
            }
          }, 300); // kratka animacija pre uklanjanja
        }
      },
      
      // Metode koje koriste generičku funkciju
      removeInfoMessage() {
        this.removeInfoElement('.second-col.right > .info-message');
      },
      
      removeProficiencyInfo() {
        this.removeInfoElement('.info-message.proficiency-info', 'showProficiencyInfo');
      },

      removePreparedSpellsInfo() {
        this.removeInfoElement('.info-message.spell-prepared-info', 'showPreparedSpellsInfo');
      },

      adjustSpellSaveDC(amount) {
        this.spellSaveDCManualModifier += amount; // Ažuriramo manualni modifier
        this.updateSpellcastingValues(); // Pozivamo updateSpellcastingValues da primeni promene
      },

      adjustSpellAttackBonus(amount) {
        this.spellAttackBonusManualModifier += amount; // Ažuriramo manualni modifier
        this.updateSpellcastingValues(); // Pozivamo updateSpellcastingValues da primeni promene
      },

      getSpellValueColorClass(valueType) {
        if (valueType === 'saveDC') {
          if (this.spellSaveDCManualModifier > 0) return 'higher-value';
          if (this.spellSaveDCManualModifier < 0) return 'lower-value';
          return '';
        } else if (valueType === 'attackBonus') {
          if (this.spellAttackBonusManualModifier > 0) return 'higher-value';
          if (this.spellAttackBonusManualModifier < 0) return 'lower-value';
          return '';
        }
        return '';
      },

      updateSpellcastingValues() {
        // Dobijamo modifier za izabrani ability
        let abilityModifier = 0;
        
        if (this.character.spellcasting.ability) {
          if (this.character.spellcasting.ability === 'Intelligence') {
            abilityModifier = this.character.abilities.Intelligence.modifier;
          } else if (this.character.spellcasting.ability === 'Wisdom') {
            abilityModifier = this.character.abilities.Wisdom.modifier;
          } else if (this.character.spellcasting.ability === 'Charisma') {
            abilityModifier = this.character.abilities.Charisma.modifier;
          }
        }
        
        // Računamo nove vrednosti
        // Spell Save DC = 8 + spellcasting modifier + proficiency bonus + manual modifier
        this.character.spellcasting.saveDC = 8 + abilityModifier + this.character.proficiencyBonus + this.spellSaveDCManualModifier;
        
        // Spell Attack Bonus = spellcasting modifier + proficiency bonus + manual modifier
        this.character.spellcasting.attackBonus = abilityModifier + this.character.proficiencyBonus + this.spellAttackBonusManualModifier;
        
        // Sačuvaj vrednosti kao bazične za bojenje (bez manualnih modifikacija)
        this.character.spellcasting.baseSaveDC = 8 + abilityModifier + this.character.proficiencyBonus;
        this.character.spellcasting.baseAttackBonus = abilityModifier + this.character.proficiencyBonus;
      },
      // Ove generičke funkcije su zamenjene metodama addSpell i removeSpell 
      // koje se koriste sa dinamičkim modalnim prozorom
      // Nepotrebne pojedinačne metode za svaki nivo čarolija su uklonjene
      // Sada koristimo generički pristup sa addSpell i removeSpell metodama
      
      // Nepotrebne pojedinačne metode za učitavanje čarolija su uklonjene
      // Sada koristimo direktno fetchSpellsForLevel metodu
      
      // Ova metoda više nije potrebna jer koristimo fetchSpellsForCurrentLevel
      // i centralizovanu availableSpellsList
      // Generička funkcija za dohvatanje magija po nivou
      async fetchSpellsForLevel(level) {
        try {
          // Prosleđujemo filtere ako postoje
          let params = {};
          
          // Dodaj filter po klasi
          if (this.selectedSpellClass && this.selectedSpellClass !== 'null') {
            params.class_id = this.selectedSpellClass;
          }
          
          // Dodaj filter po tipu magije
          if (this.selectedSpellType && this.selectedSpellType !== 'null') {
            params.spell_type = this.selectedSpellType;
          }
          
          await axios.get(`http://localhost:5000/api/spells/by-level/${level}`, { params });
          // Ne čuvamo više rezultate u pojedinačnim listama, jer koristimo fetchSpellsForCurrentLevel
          // kada je to potrebno
        } catch (error) {
          console.error(`Greška prilikom učitavanja level ${level} spells:`, error);
        }
      },
      
      // Objedinjena metoda za filtriranje čarolija po klasi i školi magije
      filterSpells() {
        // Ponovo učitamo sve čarolije sa filtriranjem
        for (let level = 0; level <= this.maxSpellLevel; level++) {
          this.fetchSpellsForLevel(level);
        }
      },
      
      // Dohvatanje čarolija po klasi - sada je samo wrapper oko filterSpells
      setClassFilter(classId) {
        this.selectedSpellClass = classId;
        this.filterSpells();
      },
      
      // Nema potrebe za pojedinačnim metodama za svaki nivo
      // jer koristimo generičku fetchSpellsForLevel metodu direktno
      updateAC() {
        const dexMod = this.character.abilities.Dexterity.modifier;
        let baseAC = 10; // Default AC when no armor

        // Calculate base AC based on armor type
        switch(this.character.armor) {
          case 'padded':
          case 'leather':
            baseAC = 11 + dexMod;
            break;
          case 'studded':
            baseAC = 12 + dexMod;
            break;
          case 'hide':
            baseAC = 12 + Math.min(dexMod, 2);
            break;
          case 'chain_shirt':
            baseAC = 13 + Math.min(dexMod, 2);
            break;
          case 'scale_mail':
          case 'breastplate':
            baseAC = 14 + Math.min(dexMod, 2);
            break;
          case 'half_plate':
            baseAC = 15 + Math.min(dexMod, 2);
            break;
          case 'ring_mail':
            baseAC = 14;
            break;
          case 'chain_mail':
            baseAC = 16;
            break;
          case 'splint':
            baseAC = 17;
            break;
          case 'plate':
            baseAC = 18;
            break;
          default:
            baseAC = 10 + dexMod;
        }

        // Add shield bonus if equipped
        if (this.character.hasShield) {
          baseAC += 2;
        }

        // Dodajemo manualni modifier na base AC
        this.character.ac = baseAC + this.acManualModifier;
      },
      handleHalfElfAbilitySelection(selectedAbilities) {
        // Primeni +1 na izabrane ability-je
        selectedAbilities.forEach(ability => {
          this.character.abilities[ability].score += 1;
          this.calculateModifier(ability);
        });

        // Sačuvaj nove osnovne vrednosti
        this.abilities.forEach(ability => {
          this.character.baseRaceScores[ability.name] = this.character.abilities[ability.name].score;
        });

        // Show notification about skill choices bonus
        this.showInfoNotification("As a Half-Elf, you gain proficiency in any two skills of your choice.");

        // Zatvori modal
        this.showHalfElfAbilityScore = false;
      },
      showSuccessNotification(message) {
        this.notificationMessage = message
        this.notificationType = 'success'
        this.showNotification = true
        setTimeout(() => {
          this.showNotification = false
        }, 3000)
      },
      
      showErrorNotification(message) {
        this.notificationMessage = message
        this.notificationType = 'error'
        this.showNotification = true
        setTimeout(() => {
          this.showNotification = false
        }, 3000)
      },
      
      showInfoNotification(message) {
        this.notificationMessage = message
        this.notificationType = 'info'
        this.showNotification = true
        setTimeout(() => {
          this.showNotification = false
        }, 5000)
      },

      async handleSave() {
        if (this.isSaving) return;
        
        // Postavi dijalog u zavisnosti od toga da li je nov ili postojeći karakter
        if (this.id) {
          this.confirmationTitle = "Save Changes";
          this.confirmationMessage = "Are you sure you want to save these changes? This will overwrite all previously saved data and the changes cannot be undone!";
        } else {
          this.confirmationTitle = "Save Character";
          this.confirmationMessage = "Are you sure you want to save this character?";
        }
        this.confirmationConfirmText = "Save";
        this.confirmationCancelText = "Cancel";
        this.confirmationAction = 'save-character';
        this.showConfirmationDialog = true;
      },

      // Metode za obradu dijaloga
      handleConfirmationConfirm() {
        if (this.confirmationAction === 'navigate-dashboard') {
          this.hasUnsavedChanges = false; // Sprečava ponovni dijalog
          this.$router.push('/dashboard');
        } else if (this.confirmationAction === 'navigate-custom' && this.pendingNavigation) {
          this.hasUnsavedChanges = false; // Sprečava ponovni dijalog
          // Prvo definišemo next(true) kako bi se dozvolila navigacija
          this.pendingNavigation.next(true);
          // Zatim eksplicitno navigiramo na željenu rutu
          if (this.pendingNavigation.to) {
            this.$router.push(this.pendingNavigation.to.path);
          }
        } else if (this.confirmationAction === 'save-character') {
          this.saveCharacter();
        }
        this.showConfirmationDialog = false;
        this.confirmationAction = null;
        this.pendingNavigation = null;
      },

      handleConfirmationCancel() {
        this.showConfirmationDialog = false;
        this.confirmationAction = null;
        this.pendingNavigation = null;
      },

      // Pomeriti logiku iz handleSave u novu metodu saveCharacter
      async saveCharacter() {
        this.isSaving = true;
        
        try {
          // Provera da li je ime karaktera uneto
          if (!this.character.name || this.character.name.trim() === '') {
            this.showErrorNotification('Character name is required!')
            
            // Skrolaj do Character Name inputa
            this.$nextTick(() => {
              const nameInput = document.querySelector('.character-name input')
              if (nameInput) {
                nameInput.scrollIntoView({ behavior: 'smooth', block: 'center' })
                nameInput.classList.add('invalid-input')
                nameInput.focus()
                
                // Ukloni invalid-input klasu nakon 3 sekunde
                setTimeout(() => {
                  nameInput.classList.remove('invalid-input')
                }, 3000)
              }
            })
            
            this.isSaving = false
            return
          }
          
          // Provera da li je rasa izabrana
          if (!this.character.race || this.character.race.trim() === '') {
            this.showErrorNotification('Race is required!')
            
            // Skrolaj do Race select polja
            this.$nextTick(() => {
              const raceSelect = document.querySelector('.race-subrace-container .info-item:first-child select')
              if (raceSelect) {
                raceSelect.scrollIntoView({ behavior: 'smooth', block: 'center' })
                raceSelect.classList.add('invalid-input')
                raceSelect.focus()
                
                // Ukloni invalid-input klasu nakon 3 sekunde
                setTimeout(() => {
                  raceSelect.classList.remove('invalid-input')
                }, 3000)
              } else {
                console.error('Race select element not found')
              }
            })
            
            this.isSaving = false
            return
          }
          
          // Provera da li je subrasa izabrana (ako postoje opcije za podrasu)
          if (this.subraces.length > 0 && (!this.character.subrace || this.character.subrace.trim() === '')) {
            this.showErrorNotification('Subrace is required!')
            
            // Skrolaj do Subrace select polja
            this.$nextTick(() => {
              const subraceSelect = document.querySelector('.race-subrace-container .info-item:nth-child(2) select')
              if (subraceSelect) {
                subraceSelect.scrollIntoView({ behavior: 'smooth', block: 'center' })
                subraceSelect.classList.add('invalid-input')
                subraceSelect.focus()
                
                // Ukloni invalid-input klasu nakon 3 sekunde
                setTimeout(() => {
                  subraceSelect.classList.remove('invalid-input')
                }, 3000)
              }
            })
            
            this.isSaving = false
            return
          }
          
          // Provera da li je klasa izabrana
          if (!this.character.class || this.character.class.trim() === '') {
            this.showErrorNotification('Class is required!')
            
            // Skrolaj do Class select polja
            this.$nextTick(() => {
              // Direktniji pristup - prvo probamo najprecizniji selektor
              let classSelectElement = document.querySelector('.character-info div.info-item:nth-child(3) select');
              
              // Ako nije pronađen, probamo direktno class selektor
              if (!classSelectElement) {
                classSelectElement = document.querySelector('select[v-model="character.class"]');
              }
              
              // Ako i dalje nije pronađen, pokušavamo sa ručnim pretraživanjem svih select elemenata
              if (!classSelectElement) {
                const allSelects = Array.from(document.querySelectorAll('select'));
                classSelectElement = allSelects.find(select => {
                  return select.getAttribute('v-model') === 'character.class' || select.innerHTML.includes('Choose class');
                });
              }
              
              // Konačno, ako imamo element, primeni scroll
              if (classSelectElement) {
                classSelectElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                classSelectElement.classList.add('invalid-input');
                classSelectElement.focus();
                
                // Ukloni invalid-input klasu nakon 3 sekunde
                setTimeout(() => {
                  classSelectElement.classList.remove('invalid-input');
                }, 3000);
              } else {
                // Ako ni jedan način nije uspeo, probaj poslednji pokušaj sa direktnim skrolovanjem do oblasti
                console.error('Class select element not found, trying fallback');
                const characterInfoSection = document.querySelector('.character-info');
                if (characterInfoSection) {
                  characterInfoSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
              }
            });
            
            this.isSaving = false
            return
          }
          
          // Provera da li je pozadina izabrana
          if (!this.character.background || this.character.background.trim() === '') {
            this.showErrorNotification('Background is required!')
            
            // Skrolaj do Background select polja
            this.$nextTick(() => {
              const backgroundSelect = document.querySelector('.background-variant-container .info-item:first-child select')
              if (backgroundSelect) {
                backgroundSelect.scrollIntoView({ behavior: 'smooth', block: 'center' })
                backgroundSelect.classList.add('invalid-input')
                backgroundSelect.focus()
                
                // Ukloni invalid-input klasu nakon 3 sekunde
                setTimeout(() => {
                  backgroundSelect.classList.remove('invalid-input')
                }, 3000)
              } else {
                console.error('Background select element not found')
              }
            })
            
            this.isSaving = false
            return
          }
          
          // Provera da li su izabrane sve potrebne skills profesije
          if (this.id === null && this.previousClassChoices > 0) {
            // Proveri da li ima dovoljno izabranih skillova
            if (this.selectedSkillsCount < this.previousClassChoices) {
              const remainingSkills = this.previousClassChoices - this.selectedSkillsCount;
              this.showErrorNotification(`You have to select ${remainingSkills} more skills from the allowed options!`);
              
              // Skrolaj do Skills sekcije
              this.$nextTick(() => {
                const skillsBlock = document.querySelector('.skills-block')
                if (skillsBlock) {
                  skillsBlock.scrollIntoView({ behavior: 'smooth', block: 'center' })
                  skillsBlock.classList.add('invalid-input')
                  
                  // Ukloni invalid-input klasu nakon 3 sekunde
                  setTimeout(() => {
                    skillsBlock.classList.remove('invalid-input')
                  }, 3000)
                }
              })
              
              this.isSaving = false
              return
            }
            
            // Proveri da li su izabrane dozvoljene veštine (highlighted)
            const nonSelectableSkills = this.getNonSelectableSelectedSkills();
            if (nonSelectableSkills.length > 0) {
              this.showErrorNotification(`Izabrali ste veštine koje nisu u dozvoljenim opcijama. Izaberite samo dozvoljene veštine!`);
              
              // Skrolaj do Skills sekcije
              this.$nextTick(() => {
                const skillsBlock = document.querySelector('.skills-block')
                if (skillsBlock) {
                  skillsBlock.scrollIntoView({ behavior: 'smooth', block: 'center' })
                  skillsBlock.classList.add('invalid-input')
                  
                  // Ukloni invalid-input klasu nakon 3 sekunde
                  setTimeout(() => {
                    skillsBlock.classList.remove('invalid-input')
                  }, 3000)
                }
              })
              
              this.isSaving = false
              return
            }
          }
          
          // Pripremi podatke za slanje, isključujući velike Base64 slike
          const characterData = {
            ...this.character,
            // Konvertuj currency vrednosti u brojeve, sa 0 kao default vrednost za prazna polja
            currency_cp: parseInt(this.character.currency.cp) || 0,
            currency_sp: parseInt(this.character.currency.sp) || 0,
            currency_ep: parseInt(this.character.currency.ep) || 0,
            currency_gp: parseInt(this.character.currency.gp) || 0,
            currency_pp: parseInt(this.character.currency.pp) || 0,
            // Dodaj spell slots
            spellSlots: this.spellSlots,
            // Proficiency Bonus i Inspiration eksplicitno mapiramo 
            proficiencyBonus: this.character.proficiencyBonus,
            profBonusModifier: this.character.profBonusModifier,
            inspirationValue: this.character.inspiration.value,
            // Eksplicitno mapiramo raceProficiencies i classProficiencies
            raceProficiency: this.character.raceProficiencies,
            classProficiency: this.character.classProficiencies,
            // Dodajemo base vrednosti za praćenje promena i bojenje
            baseAbilityScores: this.character.baseAbilityScores,
            baseRaceScores: this.character.baseRaceScores,
            pureRaceScores: this.character.pureRaceScores,
            baseSpeed: this.character.baseSpeed || 30,
            // Dodajemo manualne modifikatore
            acManualModifier: this.acManualModifier,
            spellSaveDCManualModifier: this.spellSaveDCManualModifier,
            spellAttackBonusManualModifier: this.spellAttackBonusManualModifier,
            initiativeModifier: this.character.initiativeModifier,
            // Čuvamo i manual modifiers za saving throws i skills
            savingThrowManualModifiers: Object.entries(this.character.savingThrows).reduce((acc, [ability, data]) => {
              acc[ability] = data.manualModifier || 0;
              return acc;
            }, {}),
            skillManualModifiers: Object.entries(this.character.skills).reduce((acc, [skill, data]) => {
              acc[skill] = data.manualModifier || 0;
              return acc;
            }, {}),
            // Dodajemo podatke o choices za čuvanje
            selectableSkills: this.selectableSkills,
            maxSelectableSkills: this.maxSelectableSkills,
            previousRaceBonus: this.previousRaceBonus,
            previousClassChoices: this.previousClassChoices,
            previousOverlapCount: this.previousOverlapCount,
          }
          
          let url = 'http://localhost:5000/api/characters'
          let method = 'post'
          
          // Ako postoji ID, onda ažuriramo postojećeg karaktera
          if (this.id) {
            url = `http://localhost:5000/api/characters/${this.id}`
            method = 'put'
          }
          
          const response = await axios({
            method,
            url,
            data: characterData,
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          })
          
          // Show success notification
          this.showSuccessNotification('Character saved successfully!')
          
          // Uvek redirektuj na dashboard nakon uspešnog čuvanja
          this.$router.push('/dashboard');
          
          // Nakon uspešnog čuvanja
          this.hasUnsavedChanges = false;
        } catch (error) {
          // Log the full error details
          console.error('Error saving character:', error.response?.data || error)
          this.showErrorNotification('Error. Can\'t save character. Please try again.')
        } finally {
          this.isSaving = false
        }
      },
      openSpellModal(level) {
        this.currentSpellLevel = level;
        this.loadingSpells = true;
        
        // Postavi odgovarajuću listu čarolija na osnovu nivoa
        this.fetchSpellsForCurrentLevel().then(() => {
          this.showSpellModal = true;
          this.loadingSpells = false;
        });
      },
      closeSpellModal() {
        this.showSpellModal = false;
        this.currentSpellLevel = 0;
        this.availableSpellsList = [];
      },
      addSpell(spell) {
        const levelInfo = this.spellLevels.find(l => l.level === this.currentSpellLevel);
        
        if (levelInfo) {
          if (!this.character.spells[levelInfo.listKey]) {
            this.character.spells[levelInfo.listKey] = [];
          }
          
          // Dodaj prepared property za čarolije iznad nivoa 0
          if (this.currentSpellLevel > 0) {
            spell.prepared = false;
          }
          
          this.character.spells[levelInfo.listKey].push(spell);
        }
        
        this.closeSpellModal();
      },
      removeSpell(index, listKey) {
        if (this.character.spells && this.character.spells[listKey]) {
          this.character.spells[listKey].splice(index, 1);
        }
      },
      async fetchSpellsForCurrentLevel() {
        try {
          // Prosleđujemo filtere ako postoje
          let params = {};
          
          // Dodaj filter po klasi
          if (this.selectedSpellClass && this.selectedSpellClass !== 'null') {
            params.class_id = this.selectedSpellClass;
          }
          
          // Dodaj filter po tipu magije
          if (this.selectedSpellType && this.selectedSpellType !== 'null') {
            params.spell_type = this.selectedSpellType;
          }
          
          const response = await axios.get(`http://localhost:5000/api/spells/by-level/${this.currentSpellLevel}`, { params });
          const allSpells = response.data.spells;
          
          // Nađi odgovarajući listKey za trenutni nivo (sada iz računate vrednosti)
          const levelInfo = this.spellLevels.find(l => l.level === this.currentSpellLevel);
          if (levelInfo) {
            const characterSpells = this.character.spells[levelInfo.listKey] || [];
            
            // Filtriraj samo čarolije koje karakter već nema
            this.availableSpellsList = allSpells.filter(spell => 
              !characterSpells.some(existingSpell => existingSpell.spell_id === spell.spell_id)
            );
          } else {
            this.availableSpellsList = [];
          }
        } catch (error) {
          console.error(`Greška prilikom učitavanja čarolija nivoa ${this.currentSpellLevel}:`, error);
          this.availableSpellsList = [];
        }
      },
      getImageUrl(imagePath) {
        // Ako je putanja puna URL adresa ili base64 string, vrati je kao takvu
        if (!imagePath) return '';
        if (imagePath.startsWith('data:') || imagePath.startsWith('http')) {
          return imagePath;
        }
        // Inače, konstruiši URL za server
        return `http://localhost:5000${imagePath}`;
      },
      
      backToDashboard() {
        // Samo prikaži dijalog ako ima promena
        if (!this.hasUnsavedChanges) {
          this.$router.push('/dashboard');
          return;
        }
        
        this.confirmationTitle = "Leave Character Sheet";
        this.confirmationMessage = "Are you sure you want to leave this page? All unsaved changes will be lost and you cannot undo this action!";
        this.confirmationConfirmText = "Leave";
        this.confirmationCancelText = "Stay";
        this.confirmationAction = 'navigate-dashboard';
        this.showConfirmationDialog = true;
      },
      
      async loadCharacter() {
        if (!this.id) return
        
        try {
          this.isSaving = true
          
          const response = await axios.get(`http://localhost:5000/api/characters/${this.id}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          })
          
          if (response.data) {
            // Postavi podatke iz baze u lokalni karakter
            const characterData = response.data
            
            // Mapiranje osnovnih podataka
            this.character.name = characterData.name || ''
            this.character.class = characterData.class || ''
            this.character.level = characterData.level || 1
            this.character.background = characterData.background || ''
            this.character.backgroundVariant = characterData.backgroundVariant || ''
            this.character.playerName = characterData.playerName || ''
            this.character.race = characterData.race || ''
            this.character.subrace = characterData.subrace || ''
            this.character.alignment = characterData.alignment || ''
            this.character.experiencePoints = characterData.experiencePoints || 0
            this.character.hitDie = characterData.hitDie || 0
            this.character.hitDice = characterData.hitDice || 1
            
            // Učitavanje base vrednosti za bojenje
            this.character.baseAbilityScores = characterData.baseAbilityScores || {}
            this.character.baseRaceScores = characterData.baseRaceScores || {}
            this.character.pureRaceScores = characterData.pureRaceScores || {}
            this.character.baseSpeed = characterData.baseSpeed || 30
            
            // Učitavanje manualnih modifikatora
            this.acManualModifier = characterData.acManualModifier || 0
            this.spellSaveDCManualModifier = characterData.spellSaveDCManualModifier || 0
            this.spellAttackBonusManualModifier = characterData.spellAttackBonusManualModifier || 0
            this.character.initiativeModifier = characterData.initiativeModifier || 0
            
            // Ability Scores
            if (characterData.abilities) {
              Object.keys(characterData.abilities).forEach(ability => {
                if (this.character.abilities[ability]) {
                  this.character.abilities[ability].score = characterData.abilities[ability].score || 10
                  
                  // Izračunaj modifier na osnovu score-a umesto da koristiš vrednost iz baze
                  this.calculateModifier(ability)
                  
                  // Ako base vrednosti nisu učitane iz baze, inicijalizujemo ih sa trenutnim vrednostima
                  if (!this.character.baseAbilityScores[ability]) {
                    this.character.baseAbilityScores[ability] = characterData.abilities[ability].score || 10
                  }
                  if (!this.character.baseRaceScores[ability]) {
                    this.character.baseRaceScores[ability] = characterData.abilities[ability].score || 10
                  }
                  if (!this.character.pureRaceScores[ability]) {
                    this.character.pureRaceScores[ability] = characterData.abilities[ability].score || 10
                  }
                }
              })
            }
            
            // Saving Throws
            if (characterData.savingThrows) {
              Object.keys(characterData.savingThrows).forEach(ability => {
                if (this.character.savingThrows[ability]) {
                  this.character.savingThrows[ability].proficient = characterData.savingThrows[ability].proficient || false
                  this.character.savingThrows[ability].modifier = characterData.savingThrows[ability].modifier || 0
                  
                  // Učitavanje manualnih modifikatora za saving throws
                  if (characterData.savingThrowManualModifiers && characterData.savingThrowManualModifiers[ability] !== undefined) {
                    this.character.savingThrows[ability].manualModifier = characterData.savingThrowManualModifiers[ability];
                  }
                }
              })
            }
            
            // Skills
            if (characterData.skills) {
              Object.keys(characterData.skills).forEach(skill => {
                if (this.character.skills[skill]) {
                  this.character.skills[skill].proficient = characterData.skills[skill].proficient || false
                  this.character.skills[skill].expertise = characterData.skills[skill].expertise || false
                  this.character.skills[skill].modifier = characterData.skills[skill].modifier || 0
                  this.character.skills[skill].ability = characterData.skills[skill].ability || this.character.skills[skill].ability
                  this.character.skills[skill].fromRace = characterData.skills[skill].fromRace || false
                  this.character.skills[skill].fromBackground = characterData.skills[skill].fromBackground || false
                  
                  // Učitavanje manualnih modifikatora za skills
                  if (characterData.skillManualModifiers && characterData.skillManualModifiers[skill] !== undefined) {
                    this.character.skills[skill].manualModifier = characterData.skillManualModifiers[skill];
                  }
                }
              })
            }
            
            // Proficiency Bonus
            this.character.proficiencyBonus = characterData.proficiencyBonus || 2
            this.character.profBonusModifier = characterData.profBonusModifier || 0
            
            // Inspiration
            if (characterData.inspiration) {
              this.character.inspiration.value = characterData.inspiration.value || 0
              this.character.inspiration.proficient = characterData.inspiration.proficient || false
            } else {
              // Ako inspiracija dolazi kao posebna polja
              this.character.inspiration.value = characterData.inspirationValue || 0
            }
            
            // HP
            if (characterData.hp) {
              this.character.hp.max = characterData.hp.max || 0
              this.character.hp.current = characterData.hp.current || 0
              this.character.hp.temp = characterData.hp.temp || 0
              this.character.hp.base = characterData.hp.base || 0
            }
            
            // Combat stats
            this.character.ac = characterData.ac || 10
            this.character.initiative = characterData.initiative || 0
            this.character.speed = characterData.speed || 30
            
            // Death Saves
            if (characterData.deathSaves) {
              this.character.deathSaves.successes = characterData.deathSaves.successes || [false, false, false]
              this.character.deathSaves.failures = characterData.deathSaves.failures || [false, false, false]
            }
            
            // Currency
            if (characterData.currency) {
              this.character.currency.cp = characterData.currency.cp || 0
              this.character.currency.sp = characterData.currency.sp || 0
              this.character.currency.ep = characterData.currency.ep || 0
              this.character.currency.gp = characterData.currency.gp || 0
              this.character.currency.pp = characterData.currency.pp || 0
            }
            
            // Equipment
            this.character.equipment = characterData.equipment || ''
            
            // Personality
            if (characterData.personality) {
              this.character.personality.traits = characterData.personality.traits || ''
              this.character.personality.ideals = characterData.personality.ideals || ''
              this.character.personality.bonds = characterData.personality.bonds || ''
              this.character.personality.flaws = characterData.personality.flaws || ''
            }
            
            // Features i Proficiencies
            this.character.raceFeatures = characterData.raceFeatures || ''
            this.character.classFeatures = characterData.classFeatures || ''
            this.character.raceProficiencies = characterData.raceProficiencies || characterData.raceProficiency || ''
            this.character.classProficiencies = characterData.classProficiencies || characterData.classProficiency || ''
            this.character.backgroundFeatures = characterData.backgroundFeatures || ''
            
            // Attacks
            this.character.attacks = characterData.attacks || []
            
            // Spellcasting
            if (characterData.spellcasting) {
              this.character.spellcasting.ability = characterData.spellcasting.ability || ''
              this.character.spellcasting.saveDC = characterData.spellcasting.saveDC || 8
              this.character.spellcasting.attackBonus = characterData.spellcasting.attackBonus || 0
              this.character.spellcasting.baseSaveDC = characterData.spellcasting.baseSaveDC || 8
              this.character.spellcasting.baseAttackBonus = characterData.spellcasting.baseAttackBonus || 0
            }
            
            // Passive Wisdom
            this.character.passiveWisdom = characterData.passiveWisdom || 10
            this.character.passiveWisdomBase = characterData.passiveWisdomBase || 10
            this.character.passiveWisdomManualModifier = characterData.passiveWisdomManualModifier || 0
            
            // Character details
            this.character.age = characterData.age || ''
            this.character.height = characterData.height || ''
            this.character.weight = characterData.weight || ''
            this.character.eyes = characterData.eyes || ''
            this.character.skin = characterData.skin || ''
            this.character.hair = characterData.hair || ''
            this.character.backstory = characterData.backstory || ''
            this.character.allies = characterData.allies || ''
            this.character.symbolName = characterData.symbolName || ''
            this.character.treasure = characterData.treasure || ''
            
            // Images
            this.character.appearanceImage = characterData.appearanceImage || ''
            this.character.symbolImage = characterData.symbolImage || ''
            
            // Spells
            if (characterData.spells) {
              // Mapiranje čarolija za svaki nivo
              this.character.spells = characterData.spells
            }
            
            // Spell Slots
            if (characterData.spellSlots) {
              this.spellSlots = characterData.spellSlots
            }
            
            // Armor
            this.character.armor = characterData.armor || ''
            this.character.hasShield = characterData.hasShield || false
            
            // Ne prikazuj AbilityScoreMethod modal kada učitavamo postojećeg karaktera
            this.showAbilityScoreMethod = false
            
            // Ažuriranje vrednosti na osnovu učitanih manualnih modifikatora
            this.updateAC() // Primenimo promene na AC sa učitanim acManualModifier
            
            // Ažuriranje spellcasting vrednosti ako je postavljena spellcasting ability
            if (this.character.spellcasting.ability) {
              this.updateSpellcastingValues() // Primenimo promene na spell vrednosti sa učitanim modifikatorima
            }
            
            // Ažuriranje initiative sa učitanim initiativeModifier
            if (this.character.initiativeModifier) {
              this.character.initiative = this.character.abilities.Dexterity.modifier + this.character.initiativeModifier
            }
            
            // Ažuriranje svih saving throws i skills modifikatora
            this.updateAllModifiers()
            
            // Ažuriranje pasivne mudrosti
            this.updatePassiveWisdom()
            
            this.showSuccessNotification('Character loaded successfully!')
            
            // Učitavanje podataka o choices
            this.selectableSkills = characterData.selectableSkills || [];
            this.maxSelectableSkills = characterData.maxSelectableSkills || 0;
            this.previousRaceBonus = characterData.previousRaceBonus || 0;
            this.previousClassChoices = characterData.previousClassChoices || 0;
            this.previousOverlapCount = characterData.previousOverlapCount || 0;
          }
          
          // Na kraju metode, nakon uspešnog učitavanja
          this.setupChangeTracking();
        } catch (error) {
          console.error('Error loading character:', error)
          this.showErrorNotification('Error. Can\'t load character. Please try again.')
        } finally {
          this.isSaving = false
        }
      },
      // Handler za beforeunload
      handleBeforeUnload(event) {
        if (this.hasUnsavedChanges) {
          const message = "Are you sure you want to leave? You have unsaved changes that will be lost!";
          event.returnValue = message;
          return message;
        }
      },
      // Kod za postavljanje hasUnsavedChanges na true kada se desi promena
      // Možemo pratiti promene korisničkog unosa
      setupChangeTracking() {
        // Inicijalno nakon učitavanja karaktera ili nakon čuvanja, postaviti na false
        this.hasUnsavedChanges = false;
        
        // Pratimo duboke promene na character objektu
        this.$watch('character', () => {
          this.hasUnsavedChanges = true;
        }, { deep: true });
      },
      
      // Metoda koja vraća listu veština koje su izabrane ali nisu selektabilne
      getNonSelectableSelectedSkills() {
        const nonSelectableSelected = [];
        
        // Prolazimo kroz sve veštine
        Object.keys(this.character.skills).forEach(skillName => {
          const skill = this.character.skills[skillName];
          
          // Ako je veština izabrana, a nije od rase ili backgrounda
          if (skill.proficient && !skill.fromRace && !skill.fromBackground) {
            // Ako nije u listi selektabilnih, dodaj je u rezultat
            if (!this.selectableSkills.includes(skillName)) {
              nonSelectableSelected.push(skillName);
            }
          }
        });
        
        return nonSelectableSelected;
      },
    },
    // Dodajem kontrolu za napuštanje rute
    beforeRouteLeave(to, from, next) {
      // Ako idemo na login, dozvoli direktan logout
      if (to.path === '/login') {
        next();
        return;
      }

      // Ako nema izmena, dozvoli navigaciju
      if (!this.hasUnsavedChanges) {
        next();
        return;
      }

      // Ako ima izmena, prikaži dijalog
      this.confirmationTitle = "Leave Character Sheet";
      this.confirmationMessage = "Are you sure you want to leave this page? All unsaved changes will be lost and you cannot undo this action!";
      this.confirmationConfirmText = "Leave";
      this.confirmationCancelText = "Stay";
      this.confirmationAction = 'navigate-custom';
      this.pendingNavigation = { next, to };
      this.showConfirmationDialog = true;
      
      // Blokiraj navigaciju dok korisnik ne odluči
      next(false);
    },
  }
</script>
  
<style scoped>
  @import "@/assets/Sheet.css";

  /* Stilovi za validaciju */
  .invalid-input {
    border: 2px solid #ff3860 !important;
    background-color: rgba(255, 56, 96, 0.1) !important;
    animation: shake 0.5s;
  }
  
  /* Stil za info notifikacije */
  .notification.info {
    background: linear-gradient(to right, #3498db, #2980b9);
    border: 2px solid #2980b9;
  }
  
  /* Stil za oznaku * kod obaveznih polja */
  label.required:after {
    content: " *";
    color: red;
    font-weight: bold;
  }
  
  /* Stil za obavezna polja */
  input::placeholder[placeholder*="*"] {
    color: #888;
  }
  
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
  }
  
  .fixed-buttons-container {
    position: fixed;
    bottom: 30px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    padding: 0 30px;
    z-index: 100;
    align-items: center;
    pointer-events: none; /* Ovo će učiniti kontejner transparentnim za klikove */
  }

  .back-button-container,
  .save-button-container {
    flex: 0 0 auto;
    pointer-events: auto; /* Ovo će omogućiti klikove samo na samim dugmićima */
  }

  .back-button-container {
    position: static;
    float: left;
  }
  
  .save-button-container {
    position: static;
    float: right;
  }

  .navigation-button {
    background: linear-gradient(to right, rgba(70, 70, 70, 0.8), rgba(40, 40, 40, 0.8));
    color: gold;
    border: 2px solid silver;
    padding: 12px 24px;
    border-radius: 4px;
    transition: all 0.3s ease;
    font-size: 1.2rem;
    font-weight: bold;
    white-space: nowrap;
    min-width: 200px;
  }
  
  .navigation-button:hover {
    background: linear-gradient(to right, rgba(100, 100, 100, 0.8), rgba(70, 70, 70, 0.8));
    box-shadow: 0 0 15px gold;
    transform: translateY(-2px);
  }

  .navigation-button:disabled {
    opacity: 0.6;
    box-shadow: none;
    transform: none;
  }
  
</style>
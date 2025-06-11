<template>
  <div class="spells-page">
    <div class="header-container">
      <h1 class="text-2xl font-bold mb-4">Select a Spell</h1>

      <!-- Pretraga -->
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search for a spell..."
          @input="fetchSpells"
          class="search-input"
        />
      </div>
    </div>
    
    <div class="filter">
      <!-- Selektor klase -->
      <div class="class-selector">
        <span for="class-select">Filter by Class: </span>
        <select id="class-select" v-model="selectedClass" @change="fetchSpells">
          <option value="null">All classes</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">{{ cls.name }}</option>
        </select>
      </div>

      <!-- Selektor nivoa magije -->
      <div class="class-selector">
        <span for="level-select">Filter by Level: </span>
        <select id="level-select" v-model="selectedLevel" @change="fetchSpells">
          <option value="null">All levels</option>
          <option v-for="n in 10" :key="n-1" :value="n-1">{{ n - 1 }}</option>
        </select>
      </div>

      <!-- Selektor tipa magije -->
      <div class="class-selector">
        <span for="type-select">Filter by School: </span>
        <select id="type-select" v-model="selectedType" @change="fetchSpells">
          <option value="null">All types</option>
          <option v-for="type in spellTypes" :key="type" :value="type">{{ type }}</option>
        </select>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <ExpandableSpell
        v-for="spell in spells"
        :key="spell.spell_id"
        :item="spell"
        endpoint="spells"
      />
    </div>

    <!-- Paginacija -->
    <div v-if="totalPages > 1" class="pagination flex flex-col items-center gap-2 mt-6">
      <div class="flex gap-2">
        <button @click="changePage(currentPage - 1)" :disabled="currentPage <= 1" class="pag">Prev</button>

        <template v-for="page in visiblePages" :key="page">
          <span v-if="page === '...'" class="pag disabled">...</span>
          <button
            v-else
            @click="changePage(page)"
            :disabled="page === currentPage"
            :class="['pag', { active: page === currentPage }]"
          >
            {{ page }}
          </button>
        </template>

        <button @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages" class="pag">Next</button>
      </div>
    </div>
  </div>
</template>

<script>
import ExpandableSpell from '@/components/ExpandableSpell.vue';
import api from '../axios';

export default {
  components: { ExpandableSpell },
  data() {
    return {
      spells: [],
      classes: [],  // Lista klasa za selektor
      selectedClass: null, // Trenutno izabrana klasa
      selectedType: null,  // Trenutno izabrani tip magije
      selectedLevel: null, // Trenutno izabrani nivo magije
      spellTypes: ['Abjuration', 'Evocation', 'Necromancy', 'Transmutation', 'Conjuration', 'Divination', 'Enchantment', 'Illusion'], // Lista tipova
      searchQuery: '', // Pretraga
      currentPage: 1,
      totalPages: 1
    };
  },
  created() {
    this.fetchClasses();  // Učitaj klase prilikom kreiranja stranice
    this.fetchSpells();   // Učitaj magije
  },
  methods: {
    async fetchClasses() {
      try {
        const response = await api.get('/classes');
        this.classes = response.data;
      } catch (error) {
        console.error('Greška prilikom učitavanja klasa:', error);
      }
    },
    async fetchSpells(page = 1, perPage = 10) {
      try {
        let url = '/spells';

        const params = {
          page: page,
          per_page: perPage,
          search: this.searchQuery
        };

        // Ako je selektovana klasa, filtriraj prema klasi
        if (this.selectedClass && this.selectedClass !== 'null') {
          url = `/spells/by-class/${this.selectedClass}`;
        }

        // Filter po tipu magije
        if (this.selectedType && this.selectedType !== 'null') {
          params.spell_type = this.selectedType;
        }

        // Filter po nivou magije
        if (this.selectedLevel !== null && this.selectedLevel !== 'null') {
          params.spell_level = this.selectedLevel;
        }

        const response = await api.get(url, { params });

        this.spells = response.data.spells || response.data;
        this.currentPage = response.data.current_page || 1;
        this.totalPages = response.data.pages || 1;
      } catch (error) {
        console.error('Greška prilikom učitavanja magija:', error);
      }
    },
    async changePage(page) {
      if (page > 0 && page <= this.totalPages) {
        await this.fetchSpells(page);
      }
    }
  },
  watch: {
    selectedClass() {
      this.currentPage = 1;
      this.fetchSpells(1);
    },
    selectedType() {
      this.currentPage = 1;
      this.fetchSpells(1);
    },
    selectedLevel() {
      this.currentPage = 1;
      this.fetchSpells(1);
    },
    searchQuery() {
      this.currentPage = 1;
      this.fetchSpells(1);
    }
  },
  computed: {
    visiblePages() {
      const pages = [];
      const total = this.totalPages;
      const current = this.currentPage;

      if (total <= 8) {
        for (let i = 1; i <= total; i++) {
          pages.push(i);
        }
      } else {
        if (current <= 5) {
          pages.push(1, 2, 3, 4, 5, 6, 7, '...', total);
        } else if (current >= total - 4) {
          pages.push(1, '...', total - 6, total - 5, total - 4, total - 3, total - 2, total - 1, total);
        } else {
          pages.push(1, '...', current - 2, current - 1, current, current + 1, current + 2, '...', total);
        }
      }

      return pages;
    }
  }
};
</script>

<style scoped>
.spells-page {
  padding: 0.6rem 1.25rem;
}

.spells-page h1 {
  margin-top: 2rem;
}

.grid.grid-cols-2.gap-4 {
  margin-bottom: 2rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
}

.pag {
  border: none;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 5px;
  color: silver;
  transition: all 0.3s ease;
  background-color: rgba(0, 0, 0, 0.4);
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
}

.pag:hover {
  background-color: rgb(0, 0, 0);
  color: gold;
}

.pag.active {
  background-color: rgb(0, 0, 0);
  color: gold;
}

.pag.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.class-selector {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.class-selector span{
  font-size: 1.5rem;
  color: silver;
  font-weight: bold;
}

.class-selector select {
  border-radius: 25px; 
  border: 2px solid silver;
  background-color: rgba(0, 0, 0, 0.6);
  color: silver;
  padding: 0.5rem 1.25rem;
  font-size: 1.3rem;
  outline: none;
  transition: all 0.3s ease;
}

.class-selector select:hover {
  background-color: black;
  border-color: gold;
  color: gold;
}

.class-selector select:focus {
  background-color: rgb(0, 0, 0);
  border-color: gold;
  color: gold;
  box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.search-input {
  padding: 0.5rem 1.25rem;
  border-radius: 25px;
  border: 2px solid silver;
  background-color: rgba(0, 0, 0, 0.6);
  color: silver;
  font-size: 1.3rem;
  outline: none;
  transition: all 0.3s ease;
}

.search-input:hover {
  background-color: black;
  border-color: gold;
  color: gold;
}

.search-input:focus {
  background-color: rgb(0, 0, 0);
  border-color: gold;
  color: gold;
  box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3);
}

.filter{
  display: flex;
  justify-content: space-evenly;
  align-items: center;
}
</style>
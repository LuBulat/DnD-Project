<template>
  <div class="item-button-container">
    <button class="item-button" @click="toggleDescription">
      <span v-if="!showDescription" class="item-name">{{ item.name }}</span>
      <span :class="['arrow', { 'arrow-down': showDescription }]">▼</span>
    </button>

    <div v-if="loading" class="loading-text">Loading description...</div>

    <div v-if="description && showDescription && !loading" class="description-container">
      <div class="description-content" v-html="processedDescription"></div>
    </div>
  </div>
</template>

<script>
import api from '../axios';

export default {
  props: {
    item: Object,
    endpoint: String
  },
  data() {
    return {
      description: '',
      showDescription: false,
      loading: false
    };
  },
  computed: {
    processedDescription() {
      return this.description
        .replace(/@click="toggleSection\('([^']+)'\)"/g, (match, id) => {
          return `data-section="${id}" class="toggle-section-button" data-open-text="Close Section"`;
        })
        .replace(/v-show="expandedSections\['([^']+)'\]"/g, (match, id) => {
          return `data-show="${id}" class="toggle-section-content hidden"`;
        });
    }
  },
  methods: {
    async toggleDescription() {
      if (this.description) {
        this.showDescription = !this.showDescription;
        if (this.showDescription) {
          this.$nextTick(this.attachToggleListeners);
        }
        return;
      }

      this.loading = true;
      this.showDescription = true;

      try {
        const response = await api.get(`/${this.endpoint}/${this.item.id}`);
        this.description = response.data.description;
      } catch (error) {
        console.error(`Error loading ${this.endpoint} description:`, error);
        this.description = 'Description not available.';
      } finally {
        this.loading = false;
        this.$nextTick(this.attachToggleListeners);
      }
    },
    attachToggleListeners() {
      const buttons = this.$el.querySelectorAll('.toggle-section-button');
      buttons.forEach(btn => {
        const id = btn.getAttribute('data-section');

        // Kloniraj dugme da ukloniš prethodne event listenere
        const newBtn = btn.cloneNode(true);
        btn.replaceWith(newBtn);

        newBtn.addEventListener('click', () => this.toggleSection(id, newBtn));
      });
    },
    toggleSection(id, button) {
      const content = this.$el.querySelector(`[data-show="${id}"]`);

      if (content) {
        content.classList.toggle('hidden');
      }

      if (button) {
        const openText = button.dataset.openText || 'Close Section';
        const defaultText = button.dataset.defaultText || button.textContent;

        const isOpen = button.dataset.opened === 'true';

        if (isOpen) {
          button.textContent = defaultText;
          button.dataset.opened = 'false';
        } else {
          if (!button.dataset.defaultText) {
            button.dataset.defaultText = button.textContent;
          }
          button.textContent = openText;
          button.dataset.opened = 'true';
        }
      }
    }
  }
};
</script>

<style>
@import "@/assets/Expandable.css";

.toggle-section-button {
  width: 25%;
  margin: auto;
  margin-bottom: 1%;
  padding: 15px;
  background: transparent;
  border: 2px solid;
  border-color: silver;
  border-radius: 50px;
  color: gold;
  font-size: 1.5rem;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s ease;
}

.toggle-section-button.hide {
  display: none;
}

.toggle-section-button:hover {
  background: linear-gradient(to right, rgba(192, 192, 192, 0.3), rgba(192, 192, 192, 0.2));
}

.toggle-section-content {
  padding: 20px 45px;
  color: silver;
  border: 2px dashed silver;
  border-radius: 50px;
  animation: fadeIn 0.5s ease;
  margin-bottom: 1%;
}

.hidden {
  display: none;
}   

</style>
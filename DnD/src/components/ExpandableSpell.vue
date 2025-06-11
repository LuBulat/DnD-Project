<template>
    <div class="item-button-container">
      <button class="item-button" @click="toggleDescription">
        <span v-if="!showDescription" class="item-name">{{ item.spell_name }}</span>
        <span :class="['arrow', { 'arrow-down': showDescription }]">▼</span>
      </button>
  
      <div v-if="loading" class="loading-text">Loading description...</div>
  
      <div v-if="description && showDescription && !loading" class="description-container">
        <h1>{{ item.spell_name }}</h1>
        <p><strong>Level:</strong> {{ item.spell_level }}</p>
        <p><strong>Type:</strong> {{ item.spell_type }}</p>
        <p><strong>Casting Time:</strong> {{ item.casting_time }}</p>
        <p><strong>Range:</strong> {{ item.spell_range }}</p>
        <p><strong>Components:</strong> {{ item.components }}</p>
        <p><strong>Duration:</strong> {{ item.duration }}</p>
        <p><strong>Description:</strong> {{ description }}</p>
        <p v-if="item.higher_levels"><strong>Higher Levels:</strong> {{ item.higher_levels }}</p>
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
    methods: {
      async toggleDescription() {
        if (this.description) {
          this.showDescription = !this.showDescription;
          return;
        }
  
        this.loading = true;
        this.showDescription = true;
  
        try {
          const response = await api.get(`/spells/${this.item.spell_id}`);
          this.description = response.data.description;
          this.item.spell_level = response.data.spell_level;
          this.item.spell_type = response.data.spell_type;
          this.item.casting_time = response.data.casting_time;
          this.item.spell_range = response.data.spell_range;
          this.item.components = response.data.components;
          this.item.duration = response.data.duration;
          this.item.higher_levels = response.data.higher_levels;
        } catch (error) {
          console.error('Error loading spell description:', error);
          this.description = 'Description not available.';
        } finally {
          this.loading = false;
        }
      }
    }
  };
  </script>
  
<style scoped>
  @import "@/assets/Expandable.css";

  .description-container{
    font-size: 1.4rem;
  }

  h1{
    color: gold;
    font-size: 2.2rem;
    border-bottom: 2px solid silver;
    padding-bottom: 1rem;
  }

</style>
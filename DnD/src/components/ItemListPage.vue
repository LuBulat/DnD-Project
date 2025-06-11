<template>
  <div class="item-page">
    <div class="item-content">
      <div class="item-left">
        <h1 class="text-2xl font-bold mb-4">Select a {{ title }}</h1>
        <div class="grid grid-cols-2 gap-4">
          <ExpandableItem
            v-for="item in items"
            :key="item.id"
            :item="item"
            :endpoint="endpoint"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../axios';
import ExpandableItem from '@/components/ExpandableItem.vue';

export default {
  components: { ExpandableItem },
  props: {
    endpoint: String, // 'races' или 'classes'
    title: String     // 'Race' или 'Class'
  },
  data() {
    return {
      items: []
    };
  },
  created() {
    this.fetchItems();
  },
  methods: {
    async fetchItems() {
      try {
        const response = await api.get(`/${this.endpoint}`);
        this.items = response.data;
      } catch (error) {
        console.error(`Error fetching ${this.endpoint}:`, error);
      }
    }
  }
};
</script>

<style scoped>
.item-page {
  padding: 20px;
}
.item-content {
  display: flex;
  gap: 20px;
}
.item-left {
  width: 100%;
  overflow-y: auto;
}
</style>
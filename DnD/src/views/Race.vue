<template>
  <div>
    <ItemListPage endpoint="races" title="Race" />
    <ScrollToTop />
  </div>
</template>

<script>
  import ItemListPage from '@/components/ItemListPage.vue';
  import ScrollToTop from '@/components/ScrollToTop.vue';

  export default {
    components: { ItemListPage, ScrollToTop }
  };
</script>

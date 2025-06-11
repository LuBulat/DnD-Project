<template>
  <div class="error-page">
    <h1>Page Not Found</h1>
    <p>The route you are looking for does not exist.</p>
  </div>
</template>

<script setup>
</script>

<style scoped>
.error-page {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 50vh;
  text-align: center;
}

h1, p {
  color: gold; /* Zlatna boja za tekst */
}

h1 {
  font-size: 3rem;
}

p {
  font-size: 1.5rem;
}
</style>

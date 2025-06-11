<template>
  <div class="scroll-to-top">
    <button class="scroll-button" @click="scrollToTop">
      <span class="arrow arrow-up">▼</span>
    </button>
  </div>
</template>

<script>
export default {
  methods: {
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }
};
</script>

<style scoped>
.scroll-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 999;
}

.scroll-button {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(30, 30, 30, 0.7);
  border: 2px solid gold;
  color: gold;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s ease;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
}

.scroll-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.6);
  border-color: #ffe44d;
  color: #ffe44d;
}

.arrow {
  font-size: 1.7rem;
  font-weight: bold;
  transition: transform 0.3s ease;
  margin: auto;
  margin-bottom: 8px;
}

.arrow-up {
  transform: rotate(180deg);
}
</style> 
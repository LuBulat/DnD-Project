<template>
    <div class="carousel-container">
      <div class="carousel-images">
        <img
          v-for="(image, index) in images"
          :key="index"
          :src="image"
          :alt="'Image ' + (index + 1)"
          :class="getImageClass(index)"
        />
      </div>
      <div class="carousel-indicators">
        <span
          v-for="(image, index) in images"
          :key="'indicator-' + index"
          :class="['indicator', { 'active': index === activeIndex }]"
          @click="changeImage(index)"
        ></span>
      </div>
    </div>
  </template>
  
  <script>
  import dragonbornImage from '@/assets/dragonborn.png';
  import elfImage from '@/assets/elf.png';
  import elf2Image from '@/assets/elf2.png';
  import humanImage from '@/assets/human.png';
  import orcImage from '@/assets/orc.png';
  import dwarfImage from '@/assets/dwarf.png';
  
  export default {
    data() {
      return {
        images: [dragonbornImage, elfImage, elf2Image, humanImage, orcImage, dwarfImage],
        activeIndex: 0,
        previousIndex: null,
        direction: 'right',
        interval: null,
      };
    },
    methods: {
      changeImage(index) {
        if (index === this.activeIndex) return;
        this.direction = index > this.activeIndex ? 'right' : 'left';
        this.previousIndex = this.activeIndex;
        this.activeIndex = index;
        clearInterval(this.interval);
        this.startAutoChange();
      },
      startAutoChange() {
        this.interval = setInterval(() => {
          this.direction = 'right';
          this.previousIndex = this.activeIndex;
          this.activeIndex = (this.activeIndex + 1) % this.images.length;
        }, 4000);
      },
      getImageClass(index) {
        if (index === this.activeIndex) {
          return [
            'carousel-image',
            'active',
            this.direction === 'right' ? 'slide-in-right' : 'slide-in-left',
          ];
        }
        if (index === this.previousIndex) {
          return [
            'carousel-image',
            this.direction === 'right' ? 'slide-out-left' : 'slide-out-right',
          ];
        }
        return 'carousel-image';
      },
    },
    mounted() {
      this.startAutoChange();
    },
    beforeDestroy() {
      clearInterval(this.interval);
    },
  };
  </script>
  
  <style scoped>
  .carousel-container {
    position: relative;
    width: 100%;
    max-width: 500px;
    margin: 0 auto;
    margin-top: 3%;
    margin-bottom: 3%;
  }
  
  .carousel-images {
    position: relative;
    width: 100%;
    height: 600px;
    overflow: hidden;
  }
  
  .carousel-image {
    position: absolute;
    width: 100%;
    height: 100%;
    object-fit: contain;
    top: 0;
    left: 0;
    opacity: 0;
    z-index: 1;
    transform: translateX(100%);
  }
  
  .carousel-image.active {
    z-index: 2;
    opacity: 1;
  }
  
  .carousel-image.slide-in-right {
    animation: slideInRight 0.6s forwards;
  }
  .carousel-image.slide-in-left {
    animation: slideInLeft 0.6s forwards;
  }
  .carousel-image.slide-out-left {
    animation: slideOutLeft 0.6s forwards;
    z-index: 2;
  }
  .carousel-image.slide-out-right {
    animation: slideOutRight 0.6s forwards;
    z-index: 2;
  }
  
  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0%);
      opacity: 1;
    }
  }
  
  @keyframes slideInLeft {
    from {
      transform: translateX(-100%);
      opacity: 0;
    }
    to {
      transform: translateX(0%);
      opacity: 1;
    }
  }
  
  @keyframes slideOutLeft {
    from {
      transform: translateX(0%);
      opacity: 1;
    }
    to {
      transform: translateX(-100%);
      opacity: 0;
    }
  }
  
  @keyframes slideOutRight {
    from {
      transform: translateX(0%);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
  
  .carousel-indicators {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 10px;
  }
  
  .indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.5);
    transition: background-color 0.3s;
  }
  
  .indicator.active {
    background-color: gold;
  }
  </style>
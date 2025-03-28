<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as ParticleLogic from '../utils/ParticleLogic';
import * as ShootingStarLogic from '../utils/ShootingStarLogic';

const props = defineProps({
  darkMode: Boolean,
  showParticles: {
    type: Boolean,
    default: true
  },
  maxParticles: {
    type: Number,
    default: 500
  }
});

const canvas = ref(null);
let ctx = null;
let animationFrame = null;
let particles = [];
let shootingStars = []; 
let mouseX = 0;
let mouseY = 0;
let scrollSpeed = 0;
let lastScrollTop = 0;
let scrollTimeout = null;
let clickEffects = []; 
let autoSpawnInterval = null; 
let shootingStarInterval = null; 
const currentParticleCount = ref(0); 
const destroyedStarsCount = ref(parseInt(localStorage.getItem('destroyedStars') || '0')); 

const incrementDestroyedStars = () => {
  destroyedStarsCount.value++;
  localStorage.setItem('destroyedStars', destroyedStarsCount.value.toString());
};

const spawnShootingStar = () => {
  if (!props.showParticles) return;
  
  
  if (shootingStars.length >= 5) return;
  
  
  if (Math.random() > 0.3) return;
  
  shootingStars.push(ShootingStarLogic.createShootingStar());
};

const setupShootingStars = () => {
  clearInterval(shootingStarInterval);
  shootingStarInterval = setInterval(spawnShootingStar, 800); 
};

const autoSpawnParticles = () => {
  if (!props.showParticles) return;
  
  
  if (particles.length >= props.maxParticles) return;
  
  const config = ParticleLogic.getParticleConfig(props.darkMode, props.maxParticles);
  const spawnCount = Math.min(10, props.maxParticles - particles.length);
  
  for (let i = 0; i < spawnCount; i++) {
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * window.innerHeight;
    particles.push(ParticleLogic.createParticle(x, y, config));
  }
};

const setupAutoSpawn = () => {
  clearInterval(autoSpawnInterval);
  autoSpawnInterval = setInterval(autoSpawnParticles, 2000); 
};

const handleMouseMove = (e) => {
  if (!props.showParticles) return;
  mouseX = e.clientX;
  mouseY = e.clientY;
};

const handleScroll = () => {
  if (!props.showParticles) return;
  const st = window.pageYOffset || document.documentElement.scrollTop;
  scrollSpeed = Math.abs(st - lastScrollTop) / 10;
  lastScrollTop = st;
  
  
  clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(() => {
    scrollSpeed = 0;
  }, 150);
};

const handleClick = (e) => {
  if (!props.showParticles) return;
  
  
  if (e.target.tagName.toLowerCase() === 'button' || 
      e.target.tagName.toLowerCase() === 'a' ||
      e.target.closest('header') ||
      e.target.closest('footer')) {
    return;
  }
  
  const clickX = e.clientX;
  const clickY = e.clientY;
  const repelRadius = 150;
  const repelStrength = 10;
  
  
  clickEffects.push({
    x: clickX,
    y: clickY,
    radius: 0,
    maxRadius: repelRadius,
    alpha: 1,
    color: props.darkMode ? '#e384c7' : '#9e6593',
  });
  
  
  let starDestroyed = false;
  shootingStars.forEach((star, index) => {
    const dx = star.x - clickX;
    const dy = star.y - clickY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance < repelRadius) {
      const result = ShootingStarLogic.createExplosion(
        star.x, star.y, star.color, 
        particles, 
        ParticleLogic.getParticleConfig,
        ParticleLogic.createParticle,
        props.darkMode,
        props.maxParticles
      );
      particles = result.particles;
      clickEffects = [...clickEffects, ...result.clickEffects];
      shootingStars.splice(index, 1);
      
      if(!star.willExplode) {
        incrementDestroyedStars();
      }
      
      starDestroyed = true;
    }
  });
  
  
  particles = ParticleLogic.handleParticleClick(particles, clickX, clickY, repelRadius, repelStrength);
};

const handleRightClick = (e) => {
  if (!props.showParticles) return;
  e.preventDefault();
  
  
  if (e.target.tagName.toLowerCase() === 'button' || 
      e.target.tagName.toLowerCase() === 'a' ||
      e.target.closest('header') ||
      e.target.closest('footer')) {
    return;
  }
  
  const config = ParticleLogic.getParticleConfig(props.darkMode, props.maxParticles);
  const spawnCount = 10; 
  const spawnRadius = 30; 
  
  
  clickEffects.push({
    x: e.clientX,
    y: e.clientY,
    radius: spawnRadius,
    maxRadius: spawnRadius,
    alpha: 1,
    color: props.darkMode ? '#ffffff' : '#e384c7',
    isSpawn: true
  });
  
  
  if (particles.length + spawnCount > props.maxParticles) {
    
    const removeCount = (particles.length + spawnCount) - props.maxParticles;
    
    
    for (let i = 0; i < removeCount; i++) {
      const randomIndex = Math.floor(Math.random() * particles.length);
      particles.splice(randomIndex, 1);
    }
  }
  
  
  for (let i = 0; i < spawnCount; i++) {
    const angle = Math.random() * Math.PI * 2;
    const distance = Math.random() * spawnRadius;
    const x = e.clientX + Math.cos(angle) * distance;
    const y = e.clientY + Math.sin(angle) * distance;
    
    particles.push(ParticleLogic.createParticle(x, y, config));
  }
};

const animate = () => {
  if (!ctx) return;
  
  if (!props.showParticles) {
    
    if (canvas.value) {
      ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
    }
    animationFrame = requestAnimationFrame(animate);
    return;
  }
  
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
  
  
  currentParticleCount.value = particles.length;
  
  
  clickEffects.forEach((effect, index) => {
    effect.alpha -= 0.02;
    
    if (effect.isExplosion) {
      effect.radius += (effect.maxRadius - effect.radius) * 0.3; 
    } else if (!effect.isSpawn) {
      effect.radius += (effect.maxRadius - effect.radius) * 0.1;
    } else {
      effect.radius -= effect.radius * 0.1;
    }
    
    if (effect.alpha <= 0) {
      clickEffects.splice(index, 1);
      return;
    }
    
    ctx.beginPath();
    ctx.arc(effect.x, effect.y, effect.radius, 0, Math.PI * 2);
    ctx.strokeStyle = effect.color;
    ctx.globalAlpha = effect.alpha;
    ctx.lineWidth = effect.isExplosion ? 1 : 2; 
    ctx.stroke();
    ctx.globalAlpha = 1;
  });
  
  
  const scrollFactor = 1 + (scrollSpeed * 0.1);
  
  
  particles = ParticleLogic.updateAndDrawParticles(ctx, particles, mouseX, mouseY, scrollFactor, canvas.value);
  
  
  const result = ShootingStarLogic.updateAndDrawShootingStars(
    ctx, 
    shootingStars, 
    mouseX, 
    mouseY, 
    props.darkMode,
    ShootingStarLogic.createExplosion,
    ParticleLogic.getParticleConfig,
    ParticleLogic.createParticle,
    particles,
    props.maxParticles,
    incrementDestroyedStars
  );
  
  shootingStars = result.shootingStars;
  particles = result.particles;
  
  
  if (particles.length > props.maxParticles * 1.5) {
    particles = particles.slice(0, props.maxParticles);
  }
  
  animationFrame = requestAnimationFrame(animate);
};

const handleResize = () => {
  if (canvas.value) {
    canvas.value.width = window.innerWidth;
    canvas.value.height = window.innerHeight;
  }
};

const initAnimation = () => {
  if (!canvas.value) return;
  
  
  ctx = canvas.value.getContext('2d');
  
  
  handleResize();
  
  
  if (particles.length === 0 || !props.showParticles) {
    const config = ParticleLogic.getParticleConfig(props.darkMode, props.maxParticles);
    particles = ParticleLogic.createParticles(config);
  }
  
  
  animate();
  
  
  setupAutoSpawn();
  
  
  setupShootingStars();
};

watch(() => props.darkMode, (newVal) => {
  const config = ParticleLogic.getParticleConfig(newVal, props.maxParticles);
  particles = ParticleLogic.createParticles(config);
});

watch(() => props.showParticles, (newVal) => {
  if (newVal) {
    
    initAnimation();
  } else {
    
    particles = [];
    shootingStars = [];
    clickEffects = [];
    clearInterval(autoSpawnInterval);
    clearInterval(shootingStarInterval);
  }
});

watch(() => props.maxParticles, (newVal) => {
  
  if (particles.length > newVal) {
    const removeCount = particles.length - newVal;
    for (let i = 0; i < removeCount; i++) {
      const randomIndex = Math.floor(Math.random() * particles.length);
      particles.splice(randomIndex, 1);
    }
  }
});

onMounted(() => {
  initAnimation();
  window.addEventListener('resize', handleResize);
  window.addEventListener('mousemove', handleMouseMove);
  window.addEventListener('scroll', handleScroll);
  window.addEventListener('click', handleClick);
  window.addEventListener('contextmenu', handleRightClick);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('mousemove', handleMouseMove);
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('click', handleClick);
  window.removeEventListener('contextmenu', handleRightClick);
  
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }
  
  clearTimeout(scrollTimeout);
  clearInterval(autoSpawnInterval);
  clearInterval(shootingStarInterval);
});
</script>

<template>
  <canvas 
    ref="canvas" 
    class="fixed top-0 left-0 w-full h-full pointer-events-none z-0"
  ></canvas>
  
  <!-- Destroyed Stars Counter -->
  <div 
    v-if="showParticles" 
    class="fixed top-20 left-3 text-sm font-medium text-gray-700 dark:text-gray-300 opacity-75 z-60 flex items-center backdrop-blur-sm bg-white/30 dark:bg-gray-800/30 px-3 py-1 rounded-full shadow-sm"
  >
    <i class="fas fa-star-half-alt mr-2 text-yellow-500 dark:text-yellow-300"></i>
    <span>{{ destroyedStarsCount }}</span>
  </div>
  
  <!-- Particle counter -->
  <div 
    v-if="showParticles" 
    class="fixed bottom-2 right-3 text-sm font-medium text-gray-700 dark:text-gray-300 opacity-75 z-0 bg-white/30 dark:bg-gray-800/30 px-3 py-1 rounded-full shadow-sm"
  >
    {{ currentParticleCount }}/{{ maxParticles }}
  </div>
  
  <!-- Hint text -->
  <div 
    v-if="showParticles" 
    class="fixed bottom-4 right-4 text-xs text-gray-500 dark:text-gray-400 bg-white/50 dark:bg-gray-800/50 p-2 rounded-lg backdrop-blur-sm opacity-0 animate-fade-in-out z-10"
  >
    <p>Psst! Klicke und rechtsklicke für einen überraschungseffekt...</p>
  </div>
</template>

<style scoped>
@keyframes fadeInOut {
  0% { opacity: 0; }
  10% { opacity: 0.8; }
  80% { opacity: 0.8; }
  100% { opacity: 0; }
}

.animate-fade-in-out {
  animation: fadeInOut 10s ease-in-out forwards;
}

/* Add subtle animation to counter */
@keyframes pulse-scale {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.fas.fa-star-half-alt {
  animation: pulse-scale 3s infinite ease-in-out;
}
</style>

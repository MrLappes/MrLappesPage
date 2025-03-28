<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import * as ParticleLogic from '../utils/ParticleLogic';
import * as ShootingStarLogic from '../utils/ShootingStarLogic';

// Add i18n support
const { t } = useI18n();

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

// Charging mechanics
const isCharging = ref(false);
const chargeLevel = ref(0);
const maxChargeTime = 3000; // 3 seconds for max charge
const chargeStartTime = ref(0);
const chargeType = ref(null); // 'left' or 'right'
const chargePosition = ref({ x: 0, y: 0 });
let chargeInterval = null;

// Screen shake effect
const isShaking = ref(false);
const shakeIntensity = ref(0);
const shakeDecay = 0.9; // How quickly the shake effect decays
let shakingTimeout = null;

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
  
  // Update charge position if actively charging
  if (isCharging.value) {
    chargePosition.value = { x: e.clientX, y: e.clientY };
  }
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

// Start charging on mouse down
const handleMouseDown = (e) => {
  if (!props.showParticles) return;
  
  // Don't charge if clicking on interactive elements
  if (e.target.tagName.toLowerCase() === 'button' || 
      e.target.tagName.toLowerCase() === 'a' ||
      e.target.closest('header') ||
      e.target.closest('footer')) {
    return;
  }
  
  // Prevent default for right click
  if (e.button === 2) {
    e.preventDefault();
  }
  
  // Start charging
  isCharging.value = true;
  chargeType.value = e.button === 0 ? 'left' : 'right';
  chargeStartTime.value = Date.now();
  chargeLevel.value = 0;
  chargePosition.value = { x: e.clientX, y: e.clientY };
  
  // Update charge level continuously
  clearInterval(chargeInterval);
  chargeInterval = setInterval(() => {
    const elapsedTime = Date.now() - chargeStartTime.value;
    chargeLevel.value = Math.min(1, elapsedTime / maxChargeTime);
    
    // Add a pulsing effect to indicate charging - more dramatic with higher charge
    const pulseSize = 20 + chargeLevel.value * 60;
    const maxPulseSize = 30 + chargeLevel.value * 100;
    const pulseAlpha = 0.2 + chargeLevel.value * 0.3;
    
    clickEffects.push({
      x: chargePosition.value.x,
      y: chargePosition.value.y,
      radius: pulseSize,
      maxRadius: maxPulseSize,
      alpha: pulseAlpha,
      color: chargeType.value === 'left' 
        ? (props.darkMode ? '#e384c7' : '#9e6593') 
        : (props.darkMode ? '#ffffff' : '#e384c7'),
      isCharging: true
    });
    
    // Add mini-particles around the cursor when charge is high
    if (chargeLevel.value > 0.5 && Math.random() > 0.5) {
      const config = ParticleLogic.getParticleConfig(props.darkMode, props.maxParticles);
      const angle = Math.random() * Math.PI * 2;
      const distance = 20 + Math.random() * 30 * chargeLevel.value;
      const x = chargePosition.value.x + Math.cos(angle) * distance;
      const y = chargePosition.value.y + Math.sin(angle) * distance;
      
      if (particles.length < props.maxParticles * 1.2) {
        const p = ParticleLogic.createParticle(x, y, config);
        p.energy = chargeLevel.value;
        p.opacity = 0.7 + chargeLevel.value * 0.3;
        p.speedX = (Math.random() - 0.5) * 2 * chargeLevel.value;
        p.speedY = (Math.random() - 0.5) * 2 * chargeLevel.value;
        particles.push(p);
      }
    }
  }, 50);
};

// Release charge on mouse up
const handleMouseUp = (e) => {
  if (!isCharging.value || !props.showParticles) return;
  
  clearInterval(chargeInterval);
  const finalChargeLevel = chargeLevel.value;
  
  if (chargeType.value === 'left') {
    // Push particles away with force proportional to charge
    const repelRadius = 150 + finalChargeLevel * 350; // 150-500 based on charge
    const repelStrength = 10 + finalChargeLevel * 30; // 10-40 based on charge
    
    // Screen shake for strong pushes
    if (finalChargeLevel > 0.7) {
      triggerScreenShake(finalChargeLevel * 15);
    }
    
    // Visual explosion effect
    clickEffects.push({
      x: chargePosition.value.x,
      y: chargePosition.value.y,
      radius: 0,
      maxRadius: repelRadius,
      alpha: 0.7 + finalChargeLevel * 0.3,
      color: props.darkMode ? '#e384c7' : '#9e6593',
      isExplosion: true
    });
    
    // Check for star collisions
    let starDestroyed = false;
    shootingStars.forEach((star, index) => {
      const dx = star.x - chargePosition.value.x;
      const dy = star.y - chargePosition.value.y;
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
    
    // Apply repel force to particles
    particles = ParticleLogic.handleParticleClick(
      particles, 
      chargePosition.value.x, 
      chargePosition.value.y, 
      repelRadius, 
      repelStrength
    );
  } else if (chargeType.value === 'right') {
    // Spawn particles based on charge level
    const config = ParticleLogic.getParticleConfig(props.darkMode, props.maxParticles);
    const spawnCount = Math.round(10 + finalChargeLevel * 90); // 10-100 based on charge
    const spawnRadius = 30 + finalChargeLevel * 70; // 30-100 based on charge
    
    // Screen shake for big spawns
    if (finalChargeLevel > 0.7) {
      triggerScreenShake(finalChargeLevel * 10);
    }
    
    // Visual spawn effect
    clickEffects.push({
      x: chargePosition.value.x,
      y: chargePosition.value.y,
      radius: spawnRadius * 1.5,
      maxRadius: spawnRadius * 1.5,
      alpha: 0.8,
      color: props.darkMode ? '#ffffff' : '#e384c7',
      isSpawn: true
    });
    
    // Remove excess particles if needed
    if (particles.length + spawnCount > props.maxParticles * 1.5) {
      const removeCount = (particles.length + spawnCount) - props.maxParticles * 1.5;
      for (let i = 0; i < removeCount; i++) {
        const randomIndex = Math.floor(Math.random() * particles.length);
        particles.splice(randomIndex, 1);
      }
    }
    
    // Create new particles in a spiral pattern for cooler effect
    for (let i = 0; i < spawnCount; i++) {
      const angle = (i / spawnCount) * Math.PI * 8 + Math.random() * 0.5;
      const distance = (Math.random() * 0.6 + 0.4) * spawnRadius * (1 - i/spawnCount);
      const x = chargePosition.value.x + Math.cos(angle) * distance;
      const y = chargePosition.value.y + Math.sin(angle) * distance;
      
      const p = ParticleLogic.createParticle(x, y, config);
      // Add outward momentum based on spawn pattern
      p.speedX += Math.cos(angle) * (2 + finalChargeLevel * 3);
      p.speedY += Math.sin(angle) * (2 + finalChargeLevel * 3);
      particles.push(p);
    }
  }
  
  // Reset charging state
  isCharging.value = false;
  chargeLevel.value = 0;
  chargeType.value = null;
};

// Screen shake effect
const triggerScreenShake = (intensity) => {
  shakeIntensity.value = intensity;
  isShaking.value = true;
  
  // Clear previous shake timeout
  if (shakingTimeout) {
    clearTimeout(shakingTimeout);
  }
  
  // Auto-stop shaking after a short period
  shakingTimeout = setTimeout(() => {
    isShaking.value = false;
    shakeIntensity.value = 0;
  }, 1000);
};

// Handle the original click for backward compatibility and for short clicks
const handleClick = (e) => {
  if (isCharging.value || !props.showParticles) return;
  
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
  if (isCharging.value || !props.showParticles) return;
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

const renderChargingEffect = (ctx, position, level, type, isDark) => {
  const { x, y } = position;
  const baseColor = type === 'left' 
    ? (isDark ? '#e384c7' : '#9e6593') 
    : (isDark ? '#ffffff' : '#e384c7');
  
  // Pulse intensity increases with charge level
  const pulseRate = 100 - (level * 50); // Faster pulse at higher charge
  const pulseSize = 1 + Math.sin(Date.now() / pulseRate) * 0.2 * (1 + level * 2);
  const ringSize = 30 * pulseSize;
  
  // Base charging circle
  ctx.beginPath();
  ctx.arc(x, y, ringSize, 0, Math.PI * 2);
  ctx.strokeStyle = baseColor;
  ctx.lineWidth = 2 + level * 3;
  ctx.globalAlpha = 0.4 + level * 0.4;
  ctx.stroke();
  
  // Progress arc
  ctx.beginPath();
  ctx.arc(x, y, ringSize, -Math.PI/2, Math.PI * 2 * level - Math.PI/2);
  ctx.strokeStyle = baseColor;
  ctx.lineWidth = 4 + level * 4;
  ctx.globalAlpha = 0.7 + level * 0.3;
  ctx.stroke();
  
  // Warning indicators for high charge
  if (level > 0.7) {
    // Danger lightning bolts
    const boltCount = Math.floor(level * 5) + 2;
    const radius = ringSize * 1.2;
    
    for (let i = 0; i < boltCount; i++) {
      const angle = (i / boltCount) * Math.PI * 2 + (Date.now() / 500);
      const startX = x + Math.cos(angle) * radius;
      const startY = y + Math.sin(angle) * radius;
      
      // Draw lightning bolt
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      
      // Create zig-zag pattern
      let currentX = startX;
      let currentY = startY;
      const segments = 3;
      const boltLength = 20 + level * 20;
      
      for (let j = 0; j < segments; j++) {
        const segAngle = angle + (Math.random() - 0.5) * 0.5;
        const segLength = boltLength / segments;
        currentX += Math.cos(segAngle) * segLength;
        currentY += Math.sin(segAngle) * segLength;
        ctx.lineTo(currentX, currentY);
      }
      
      ctx.strokeStyle = level > 0.9 ? '#ffcc00' : baseColor;
      ctx.lineWidth = 2 + level * 2;
      ctx.globalAlpha = 0.7 + Math.sin(Date.now() / 100) * 0.3;
      ctx.stroke();
    }
    
    // Warning rings for max charge
    if (level > 0.9) {
      // Outer danger ring
      ctx.beginPath();
      ctx.arc(x, y, ringSize * 1.5, 0, Math.PI * 2);
      ctx.strokeStyle = '#ff0000';
      ctx.lineWidth = 2;
      ctx.globalAlpha = 0.3 + Math.sin(Date.now() / 50) * 0.2;
      ctx.stroke();
      
      // Hazard markers
      const markerCount = 8;
      for (let i = 0; i < markerCount; i++) {
        const markerAngle = (i / markerCount) * Math.PI * 2;
        const markerX = x + Math.cos(markerAngle) * (ringSize * 1.5);
        const markerY = y + Math.sin(markerAngle) * (ringSize * 1.5);
        
        // Draw warning marker
        ctx.save();
        ctx.translate(markerX, markerY);
        ctx.rotate(markerAngle);
        
        ctx.beginPath();
        ctx.moveTo(-5, -10);
        ctx.lineTo(5, -10);
        ctx.lineTo(0, 0);
        ctx.closePath();
        
        ctx.fillStyle = '#ff0000';
        ctx.globalAlpha = 0.7 + Math.sin(Date.now() / 100 + i) * 0.3;
        ctx.fill();
        ctx.restore();
      }
    }
  }
  
  // Inner glow
  const gradient = ctx.createRadialGradient(x, y, 0, x, y, ringSize * 0.7);
  gradient.addColorStop(0, type === 'left' 
    ? `rgba(227, 132, 199, ${0.3 + level * 0.5})` 
    : `rgba(255, 255, 255, ${0.3 + level * 0.5})`);
  gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

  ctx.beginPath();
  ctx.arc(x, y, ringSize * 0.7, 0, Math.PI * 2);
  ctx.fillStyle = gradient;
  ctx.globalAlpha = 0.5 + level * 0.5;
  ctx.fill();
  
  // Reset global alpha
  ctx.globalAlpha = 1;
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
  
  // Apply screen shake effect
  if (isShaking.value && shakeIntensity.value > 0.1) {
    const shakeOffsetX = (Math.random() - 0.5) * shakeIntensity.value;
    const shakeOffsetY = (Math.random() - 0.5) * shakeIntensity.value;
    ctx.save();
    ctx.translate(shakeOffsetX, shakeOffsetY);
    shakeIntensity.value *= shakeDecay; // Reduce shake intensity over time
  }
  
  currentParticleCount.value = particles.length;
  
  // Render click/charge effects
  clickEffects.forEach((effect, index) => {
    // Different behavior for charging pulse vs. regular effect
    if (effect.isCharging) {
      effect.alpha -= 0.05;
      effect.radius = effect.maxRadius * (1 - Math.abs(Math.sin(Date.now() / 100) * 0.3));
    } else {
      effect.alpha -= 0.02;
      
      if (effect.isExplosion) {
        effect.radius += (effect.maxRadius - effect.radius) * 0.3;
      } else if (!effect.isSpawn) {
        effect.radius += (effect.maxRadius - effect.radius) * 0.1;
      } else {
        effect.radius -= effect.radius * 0.1;
      }
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
  
  // Render charging indicator if actively charging
  if (isCharging.value) {
    renderChargingEffect(
      ctx, 
      chargePosition.value, 
      chargeLevel.value, 
      chargeType.value, 
      props.darkMode
    );
  }
  
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
  
  // Reset transform if we applied a shake
  if (isShaking.value && shakeIntensity.value > 0.1) {
    ctx.restore();
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
  window.addEventListener('mousedown', handleMouseDown);  // Add mousedown handler
  window.addEventListener('mouseup', handleMouseUp);      // Add mouseup handler
  window.addEventListener('contextmenu', handleRightClick);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('mousemove', handleMouseMove);
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('click', handleClick);
  window.removeEventListener('mousedown', handleMouseDown);
  window.removeEventListener('mouseup', handleMouseUp);
  window.removeEventListener('contextmenu', handleRightClick);
  
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }
  
  clearTimeout(scrollTimeout);
  clearInterval(autoSpawnInterval);
  clearInterval(shootingStarInterval);
  clearInterval(chargeInterval);  // Clean up charge interval
  clearTimeout(shakingTimeout);    // Clean up shake timeout
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
    {{ t('animations.particleCount', { current: currentParticleCount, max: maxParticles }) }}
  </div>
  
  <!-- Hint text - Updated to be more visible and informative -->
  <div 
    v-if="showParticles" 
    class="fixed bottom-4 left-4 text-xs text-gray-600 dark:text-gray-300 bg-white/70 dark:bg-gray-800/70 p-3 rounded-lg backdrop-blur-sm opacity-0 animate-fade-in-out z-10 max-w-xs"
  >
    <p class="font-medium">{{ t('animations.hint') }}</p>
    <p class="mt-1">✨ Hold mouse buttons to charge powerful effects!</p>
    <p class="mt-1">⚡ Full charge unlocks special effects and screen shake!</p>
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

/* Enhanced fade-in for hints */
@keyframes fadeInOut {
  0% { opacity: 0; transform: translateY(10px); }
  10% { opacity: 0.9; transform: translateY(0); }
  70% { opacity: 0.9; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-10px); }
}

.animate-fade-in-out {
  animation: fadeInOut 12s ease-in-out forwards;
}
</style>

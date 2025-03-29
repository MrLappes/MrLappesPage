<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import * as ParticleLogic from '../utils/ParticleLogic';
import * as ShootingStarLogic from '../utils/ShootingStarLogic';
import { renderChargingEffect } from '../utils/ChargingEffects'; 


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
  },
  touchMode: {
    type: Boolean,
    default: false
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


const isCharging = ref(false);
const chargeLevel = ref(0);
const maxChargeTime = 3000; 
const chargeStartTime = ref(0);
const chargeType = ref(null); 
const chargePosition = ref({ x: 0, y: 0 });
let chargeInterval = null;


const isShaking = ref(false);
const shakeIntensity = ref(0);
const shakeDecay = 0.9; 
let shakingTimeout = null;


const activeTouchId = ref(null);
const isTouchDevice = ref(false);


onMounted(() => {
  isTouchDevice.value = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
});

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
  
  
  
  if (!props.touchMode || (props.touchMode && activeTouchId.value !== null)) {
    mouseX = e.clientX;
    mouseY = e.clientY;
  }
  
  
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


const handleMouseDown = (e) => {
  if (!props.showParticles) return;
  
  
  if (e.target.tagName.toLowerCase() === 'button' || 
      e.target.tagName.toLowerCase() === 'a' ||
      e.target.closest('header') ||
      e.target.closest('footer')) {
    return;
  }
  
  
  if (e.button === 2) {
    e.preventDefault();
  }
  
  
  isCharging.value = true;
  chargeType.value = e.button === 0 ? 'left' : 'right';
  chargeStartTime.value = Date.now();
  chargeLevel.value = 0;
  chargePosition.value = { x: e.clientX, y: e.clientY };
  
  
  clearInterval(chargeInterval);
  chargeInterval = setInterval(() => {
    const elapsedTime = Date.now() - chargeStartTime.value;
    chargeLevel.value = Math.min(1, elapsedTime / maxChargeTime);
    
    
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


const handleMouseUp = (e) => {
  if (!isCharging.value || !props.showParticles) return;
  
  clearInterval(chargeInterval);
  const finalChargeLevel = chargeLevel.value;
  
  if (chargeType.value === 'left') {
    
    
    
    const baseRadius = 120; 
    const maxRadius = 400; 
    const exponent = 3; 
    
    
    const repelRadius = baseRadius + (maxRadius - baseRadius) * Math.pow(finalChargeLevel, exponent);
    
    
    const repelStrength = 8 + finalChargeLevel * 32; 
    
    
    if (finalChargeLevel > 0.7) {
      triggerScreenShake(finalChargeLevel * 15);
    }
    
    
    clickEffects.push({
      x: chargePosition.value.x,
      y: chargePosition.value.y,
      radius: 0,
      maxRadius: repelRadius,
      alpha: 0.7 + finalChargeLevel * 0.3,
      color: props.darkMode ? '#e384c7' : '#9e6593',
      isExplosion: true,
      
      growthExponent: 1.5, 
    });
    
    
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
    
    
    particles = ParticleLogic.handleParticleClick(
      particles, 
      chargePosition.value.x, 
      chargePosition.value.y, 
      repelRadius, 
      repelStrength
    );
  } else if (chargeType.value === 'right') {
    
    const config = ParticleLogic.getParticleConfig(props.darkMode, props.maxParticles);
    
    
    const maxPossibleSpawn = Math.floor(props.maxParticles * 0.5);
    const spawnCount = Math.round(10 + finalChargeLevel * (maxPossibleSpawn - 10));
    const spawnRadius = 30 + finalChargeLevel * 70;
    
    
    if (finalChargeLevel > 0.7) {
      triggerScreenShake(finalChargeLevel * 10);
    }
    
    
    clickEffects.push({
      x: chargePosition.value.x,
      y: chargePosition.value.y,
      radius: spawnRadius * 1.5,
      maxRadius: spawnRadius * 1.5,
      alpha: 0.8,
      color: props.darkMode ? '#ffffff' : '#e384c7',
      isSpawn: true
    });
    
    
    
    if (particles.length + spawnCount > props.maxParticles * 1.5) {
      const currentExcess = particles.length + spawnCount - (props.maxParticles * 1.5);
      const particlesToMark = Math.min(currentExcess, particles.length);
      
      
      for (let i = 0; i < particlesToMark; i++) {
        const randomIndex = Math.floor(Math.random() * particles.length);
        
        
        if (particles[randomIndex].expiresAt) {
          i--; 
          continue;
        }
        
        
        const expirationDelay = 1000 + Math.random() * 4000;
        particles[randomIndex].expiresAt = Date.now() + expirationDelay;
        
        
        particles[randomIndex].expiring = true;
      }
    }
    
    
    for (let i = 0; i < spawnCount; i++) {
      const angle = (i / spawnCount) * Math.PI * 8 + Math.random() * 0.5;
      const distance = (Math.random() * 0.6 + 0.4) * spawnRadius * (1 - i/spawnCount);
      const x = chargePosition.value.x + Math.cos(angle) * distance;
      const y = chargePosition.value.y + Math.sin(angle) * distance;
      
      const p = ParticleLogic.createParticle(x, y, config);
      
      p.speedX += Math.cos(angle) * (2 + finalChargeLevel * 3);
      p.speedY += Math.sin(angle) * (2 + finalChargeLevel * 3);
      particles.push(p);
    }

    
    if (finalChargeLevel > 0.5) {
      particles.forEach(p => {
        
        const dx = p.x - chargePosition.value.x;
        const dy = p.y - chargePosition.value.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance > 0) {
          const angle = Math.atan2(dy, dx);
          const boostFactor = 1 + finalChargeLevel * 2;
          
          
          p.speedX += Math.cos(angle) * boostFactor * (1 - Math.min(1, distance / 800));
          p.speedY += Math.sin(angle) * boostFactor * (1 - Math.min(1, distance / 800));
          
          
          p.energy = Math.min(1.0, p.energy + finalChargeLevel * 0.5);
        }
      });
    }
  }
  
  
  isCharging.value = false;
  chargeLevel.value = 0;
  chargeType.value = null;
};


const triggerScreenShake = (intensity) => {
  shakeIntensity.value = intensity;
  isShaking.value = true;
  
  
  if (shakingTimeout) {
    clearTimeout(shakingTimeout);
  }
  
  
  shakingTimeout = setTimeout(() => {
    isShaking.value = false;
    shakeIntensity.value = 0;
  }, 1000);
};


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


const handleTouchStart = (e) => {
  if (!props.showParticles) return;
  
  
  if (e.target.tagName.toLowerCase() === 'button' || 
      e.target.tagName.toLowerCase() === 'a' ||
      e.target.closest('header') ||
      e.target.closest('footer')) {
    return;
  }
  
  
  const touchCount = e.touches.length;
  
  
  if (touchCount === 1) {
    
    if (activeTouchId.value === null) {
      const touch = e.touches[0];
      activeTouchId.value = touch.identifier;
      mouseX = touch.clientX;
      mouseY = touch.clientY;
    }
    return;
  }
  
  
  e.preventDefault();
  
  
  if (!isCharging.value && touchCount >= 2) {
    
    let sumX = 0;
    let sumY = 0;
    
    for (let i = 0; i < e.touches.length; i++) {
      sumX += e.touches[i].clientX;
      sumY += e.touches[i].clientY;
    }
    
    const centerX = sumX / touchCount;
    const centerY = sumY / touchCount;
    
    
    activeTouchId.value = 'multi-touch';
    
    
    
    
    const effectType = touchCount === 2 ? 'left' : 'right';
    
    
    isCharging.value = true;
    chargeType.value = effectType;
    chargeStartTime.value = Date.now();
    chargeLevel.value = 0;
    chargePosition.value = { x: centerX, y: centerY };
    
    
    mouseX = centerX;
    mouseY = centerY;
    
    
    clearInterval(chargeInterval);
    chargeInterval = setInterval(() => {
      const elapsedTime = Date.now() - chargeStartTime.value;
      chargeLevel.value = Math.min(1, elapsedTime / maxChargeTime);
      
      
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
  }
};


const handleTouchMove = (e) => {
  if (!props.showParticles) return;
  
  
  if (e.touches.length === 1 && activeTouchId.value !== 'multi-touch') {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      if (touch.identifier === activeTouchId.value) {
        mouseX = touch.clientX;
        mouseY = touch.clientY;
        break;
      }
    }
    return;
  }
  
  
  if (isCharging.value && activeTouchId.value === 'multi-touch') {
    
    let sumX = 0;
    let sumY = 0;
    const touchCount = e.touches.length;
    
    for (let i = 0; i < touchCount; i++) {
      sumX += e.touches[i].clientX;
      sumY += e.touches[i].clientY;
    }
    
    const centerX = sumX / touchCount;
    const centerY = sumY / touchCount;
    
    
    mouseX = centerX;
    mouseY = centerY;
    chargePosition.value = { x: centerX, y: centerY };
    
    
    
    if (touchCount >= 2) {
      chargeType.value = touchCount === 2 ? 'left' : 'right';
    }
  }
};


const handleTouchEnd = (e) => {
  if (!props.showParticles) return;
  
  
  if (activeTouchId.value !== 'multi-touch') {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      if (touch.identifier === activeTouchId.value) {
        activeTouchId.value = null;
        
        if (props.touchMode) {
          mouseX = -1000;
          mouseY = -1000;
        }
        break;
      }
    }
    return;
  }
  
  
  
  const remainingTouches = e.touches.length;
  
  if (remainingTouches < 2) {
    
    activeTouchId.value = null;
    
    
    if (props.touchMode) {
      mouseX = -1000;
      mouseY = -1000;
    }
    
    
    if (isCharging.value) {
      clearInterval(chargeInterval);
      const finalChargeLevel = chargeLevel.value;
      const currentEffectType = chargeType.value;
      
      
      if (currentEffectType === 'left') {
        
        
        
        
        const baseRadius = 120;
        const maxRadius = 400;
        const exponent = 3;
        
        const repelRadius = baseRadius + (maxRadius - baseRadius) * Math.pow(finalChargeLevel, exponent);
        const repelStrength = 8 + finalChargeLevel * 32;
        
        
        if (finalChargeLevel > 0.7) {
          triggerScreenShake(finalChargeLevel * 15);
        }
        
        
        clickEffects.push({
          x: chargePosition.value.x,
          y: chargePosition.value.y,
          radius: 0,
          maxRadius: repelRadius,
          alpha: 0.7 + finalChargeLevel * 0.3,
          color: props.darkMode ? '#e384c7' : '#9e6593',
          isExplosion: true,
          growthExponent: 1.5,
        });
        
        
        particles = ParticleLogic.handleParticleClick(
          particles, 
          chargePosition.value.x, 
          chargePosition.value.y, 
          repelRadius, 
          repelStrength
        );
        
      } else {
        
        
        
        
        const config = ParticleLogic.getParticleConfig(props.darkMode, props.maxParticles);
        
        
        const maxPossibleSpawn = Math.floor(props.maxParticles * 0.5);
        const spawnCount = Math.round(10 + finalChargeLevel * (maxPossibleSpawn - 10));
        const spawnRadius = 30 + finalChargeLevel * 70;
        
        
        if (finalChargeLevel > 0.7) {
          triggerScreenShake(finalChargeLevel * 10);
        }
        
        
        clickEffects.push({
          x: chargePosition.value.x,
          y: chargePosition.value.y,
          radius: spawnRadius * 1.5,
          maxRadius: spawnRadius * 1.5,
          alpha: 0.8,
          color: props.darkMode ? '#ffffff' : '#e384c7',
          isSpawn: true
        });
        
        
        if (particles.length + spawnCount > props.maxParticles * 1.5) {
          const currentExcess = particles.length + spawnCount - (props.maxParticles * 1.5);
          const particlesToMark = Math.min(currentExcess, particles.length);
          
          
          for (let i = 0; i < particlesToMark; i++) {
            const randomIndex = Math.floor(Math.random() * particles.length);
            
            if (particles[randomIndex].expiresAt) {
              i--; 
              continue;
            }
            
            const expirationDelay = 1000 + Math.random() * 4000;
            particles[randomIndex].expiresAt = Date.now() + expirationDelay;
            particles[randomIndex].expiring = true;
          }
        }
        
        
        for (let i = 0; i < spawnCount; i++) {
          const angle = (i / spawnCount) * Math.PI * 8 + Math.random() * 0.5;
          const distance = (Math.random() * 0.6 + 0.4) * spawnRadius * (1 - i/spawnCount);
          const x = chargePosition.value.x + Math.cos(angle) * distance;
          const y = chargePosition.value.y + Math.sin(angle) * distance;
          
          const p = ParticleLogic.createParticle(x, y, config);
          p.speedX += Math.cos(angle) * (2 + finalChargeLevel * 3);
          p.speedY += Math.sin(angle) * (2 + finalChargeLevel * 3);
          particles.push(p);
        }
        
        
        if (finalChargeLevel > 0.5) {
          particles.forEach(p => {
            const dx = p.x - chargePosition.value.x;
            const dy = p.y - chargePosition.value.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 0) {
              const angle = Math.atan2(dy, dx);
              const boostFactor = 1 + finalChargeLevel * 2;
              
              p.speedX += Math.cos(angle) * boostFactor * (1 - Math.min(1, distance / 800));
              p.speedY += Math.sin(angle) * boostFactor * (1 - Math.min(1, distance / 800));
              p.energy = Math.min(1.0, p.energy + finalChargeLevel * 0.5);
            }
          });
        }
      }
      
      
      isCharging.value = false;
      chargeLevel.value = 0;
      chargeType.value = null;
    }
  } else {
    
    let sumX = 0;
    let sumY = 0;
    
    for (let i = 0; i < e.touches.length; i++) {
      sumX += e.touches[i].clientX;
      sumY += e.touches[i].clientY;
    }
    
    const centerX = sumX / remainingTouches;
    const centerY = sumY / remainingTouches;
    
    
    mouseX = centerX;
    mouseY = centerY;
    chargePosition.value = { x: centerX, y: centerY };
    
    
    chargeType.value = remainingTouches === 2 ? 'left' : 'right';
  }
};


const handleTouchCancel = (e) => {
  handleTouchEnd(e);
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
  
  
  if (isShaking.value && shakeIntensity.value > 0.1) {
    const shakeOffsetX = (Math.random() - 0.5) * shakeIntensity.value;
    const shakeOffsetY = (Math.random() - 0.5) * shakeIntensity.value;
    ctx.save();
    ctx.translate(shakeOffsetX, shakeOffsetY);
    shakeIntensity.value *= shakeDecay; 
  }
  
  currentParticleCount.value = particles.length;
  
  
  clickEffects.forEach((effect, index) => {
    
    if (effect.isCharging) {
      effect.alpha -= 0.05;
      effect.radius = effect.maxRadius * (1 - Math.abs(Math.sin(Date.now() / 100) * 0.3));
    } else {
      effect.alpha -= 0.02;
      
      if (effect.isExplosion) {
        
        if (effect.growthExponent) {
          
          const progress = effect.radius / effect.maxRadius;
          
          const targetProgress = Math.pow(progress, 1/effect.growthExponent);
          const targetRadius = effect.maxRadius * targetProgress;
          
          effect.radius += (targetRadius - effect.radius) * 0.3;
        } else {
          
          effect.radius += (effect.maxRadius - effect.radius) * 0.3;
        }
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
  
  
  const chargeInfo = isCharging.value ? {
    isCharging: true,
    type: chargeType.value,
    level: chargeLevel.value,
    position: chargePosition.value
  } : null;
  
  
  const now = Date.now();
  particles = particles.filter(p => {
    
    if (p.expiresAt) {
      
      const timeLeft = p.expiresAt - now;
      if (timeLeft <= 0) {
        
        return false;
      }
      
      
      if (p.expiring) {
        const fadeFactor = Math.min(1, timeLeft / 1000); 
        p.opacity = p.initialOpacity ? p.initialOpacity * fadeFactor : p.opacity * fadeFactor;
        
        
        p.speedX *= 0.98;
        p.speedY *= 0.98;
      }
    }
    return true;
  });
  
  
  
  particles = ParticleLogic.updateAndDrawParticles(
    ctx, 
    particles, 
    mouseX, 
    mouseY, 
    scrollFactor, 
    canvas.value, 
    true, 
    chargeInfo
  );
  
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
  window.addEventListener('mousedown', handleMouseDown);  
  window.addEventListener('mouseup', handleMouseUp);      
  window.addEventListener('contextmenu', handleRightClick);
  
  
  window.addEventListener('touchstart', handleTouchStart, { passive: false });
  window.addEventListener('touchmove', handleTouchMove, { passive: true });
  window.addEventListener('touchend', handleTouchEnd);
  window.addEventListener('touchcancel', handleTouchCancel);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('mousemove', handleMouseMove);
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('click', handleClick);
  window.removeEventListener('mousedown', handleMouseDown);
  window.removeEventListener('mouseup', handleMouseUp);
  window.removeEventListener('contextmenu', handleRightClick);
  
  
  window.removeEventListener('touchstart', handleTouchStart);
  window.removeEventListener('touchmove', handleTouchMove);
  window.removeEventListener('touchend', handleTouchEnd);
  window.removeEventListener('touchcancel', handleTouchCancel);
  
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }
  
  clearTimeout(scrollTimeout);
  clearInterval(autoSpawnInterval);
  clearInterval(shootingStarInterval);
  clearInterval(chargeInterval);  
  clearTimeout(shakingTimeout);    
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
    <p class="mt-1">✨ On desktop: Hold mouse buttons to charge powerful effects!</p>
    <p class="mt-1">📱 On mobile: Use two fingers for push effect, three for black hole!</p>
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

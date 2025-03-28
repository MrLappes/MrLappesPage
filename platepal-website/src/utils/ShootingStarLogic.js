export function createShootingStar() {
  
  const side = Math.floor(Math.random() * 4); 
  let x, y;
  
  switch(side) {
    case 0: 
      x = Math.random() * window.innerWidth;
      y = -20;
      break;
    case 1: 
      x = window.innerWidth + 20;
      y = Math.random() * window.innerHeight;
      break;
    case 2: 
      x = Math.random() * window.innerWidth;
      y = window.innerHeight + 20;
      break;
    case 3: 
      x = -20;
      y = Math.random() * window.innerHeight;
      break;
  }
  
  
  const exitSide = (side + 2) % 4;
  let targetX, targetY;
  
  switch(exitSide) {
    case 0: 
      targetX = Math.random() * window.innerWidth;
      targetY = -20;
      break;
    case 1: 
      targetX = window.innerWidth + 20;
      targetY = Math.random() * window.innerHeight;
      break;
    case 2: 
      targetX = Math.random() * window.innerWidth;
      targetY = window.innerHeight + 20;
      break;
    case 3: 
      targetX = -20;
      targetY = Math.random() * window.innerHeight;
      break;
  }
  
  
  const angle = Math.atan2(targetY - y, targetX - x);
  const speed = 6 + Math.random() * 12; 
  
  
  const willExplode = Math.random() < 0.3;
  
  return {
    x,
    y,
    targetX,
    targetY,
    size: 1 + Math.random() * 1.5, 
    speedX: Math.cos(angle) * speed,
    speedY: Math.sin(angle) * speed,
    baseSpeedX: Math.cos(angle) * speed,
    baseSpeedY: Math.sin(angle) * speed,
    color: document.documentElement.classList.contains('dark') ? '#ffffff' : '#111111',
    trail: [],
    maxTrailLength: 15 + Math.random() * 25, 
    life: 1, 
    lifeDecrement: willExplode ? 0.01 + Math.random() * 0.015 : 0.002, 
    willExplode,
    distanceTraveled: 0,
    totalDistance: Math.sqrt(Math.pow(targetX - x, 2) + Math.pow(targetY - y, 2)),
    explosionTriggered: false
  };
}

export function createExplosion(x, y, color, particles, getParticleConfig, createParticle, isDarkMode, maxParticles) {
  const clickEffects = [];
  
  
  clickEffects.push({
    x,
    y,
    radius: 1,
    maxRadius: 40 + Math.random() * 20,
    alpha: 0.8,
    color,
    isExplosion: true
  });
  
  
  const particleCount = 5 + Math.floor(Math.random() * 8);
  const config = getParticleConfig(isDarkMode, maxParticles);
  
  for (let i = 0; i < particleCount; i++) {
    const angle = Math.random() * Math.PI * 2;
    const distance = Math.random() * 30;
    const speed = 1 + Math.random() * 3;
    
    
    const particle = createParticle(x, y, config);
    particle.speedX = Math.cos(angle) * speed;
    particle.speedY = Math.sin(angle) * speed;
    particle.baseSpeedX = Math.cos(angle) * (speed * 0.2);
    particle.baseSpeedY = Math.sin(angle) * (speed * 0.2);
    particle.rotationSpeed = (Math.random() - 0.5) * 6;
    
    
    if (particles.length >= maxParticles) {
      const randomIndex = Math.floor(Math.random() * (particles.length - 1));
      particles.splice(randomIndex, 1);
    }
    
    particles.push(particle);
  }
  
  return { particles, clickEffects };
}

export function updateAndDrawShootingStars(ctx, shootingStars, mouseX, mouseY, isDarkMode, createExplosion, getParticleConfig, createParticle, particles, maxParticles, incrementDestroyedStars) {
  shootingStars.forEach((star, index) => {
    
    const lastX = star.x;
    const lastY = star.y;
    
    
    const dx = mouseX - star.x;
    const dy = mouseY - star.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const maxDistance = 300;
    
    if (distance < maxDistance) {
      const force = (maxDistance - distance) / maxDistance;
      
      star.speedX += (dx / distance) * force * 0.1;
      star.speedY += (dy / distance) * force * 0.1;
      
      
      star.baseSpeedX = star.baseSpeedX * 0.9 + star.speedX * 0.1;
      star.baseSpeedY = star.baseSpeedY * 0.9 + star.speedY * 0.1;
    }
    
    
    star.x += star.speedX;
    star.y += star.speedY;
    
    
    star.distanceTraveled += Math.sqrt(
      Math.pow(star.x - lastX, 2) + Math.pow(star.y - lastY, 2)
    );
    
    
    if (star.willExplode && !star.explosionTriggered && 
        (star.distanceTraveled / star.totalDistance > 0.4 + Math.random() * 0.3)) {
      star.explosionTriggered = true;
      star.lifeDecrement = 0.05 + Math.random() * 0.05; 
    }
    
    
    if (star.life <= 0) {
      
      if (star.willExplode) {
        const result = createExplosion(star.x, star.y, star.color, particles, getParticleConfig, createParticle, isDarkMode, maxParticles);
        particles = result.particles;
        incrementDestroyedStars();
      }
      shootingStars.splice(index, 1);
      return;
    }
    
    
    star.life -= star.lifeDecrement;
    
    
    star.speedX = star.speedX * 0.98 + star.baseSpeedX * 0.02;
    star.speedY = star.speedY * 0.98 + star.baseSpeedY * 0.02;
    
    
    star.trail.push({ x: star.x, y: star.y });
    
    
    if (star.trail.length > star.maxTrailLength) {
      star.trail.shift();
    }
    
    
    if (star.trail.length > 1) {
      ctx.beginPath();
      for (let i = 0; i < star.trail.length; i++) {
        const pos = star.trail[i];
        const alpha = (i / star.trail.length) * star.life;
        
        if (i === 0) {
          ctx.moveTo(pos.x, pos.y);
        } else {
          ctx.lineTo(pos.x, pos.y);
        }
      }
      
      
      const gradient = ctx.createLinearGradient(
        star.trail[0].x, star.trail[0].y,
        star.x, star.y
      );
      
      gradient.addColorStop(0, 'rgba(0,0,0,0)'); 
      gradient.addColorStop(1, star.color);
      
      ctx.strokeStyle = gradient;
      ctx.lineWidth = star.size * 0.8; 
      ctx.lineCap = 'round';
      ctx.stroke();
    }
    
    
    ctx.beginPath();
    ctx.arc(star.x, star.y, star.size * 1.5, 0, Math.PI * 2);
    ctx.fillStyle = star.color;
    ctx.globalAlpha = star.life;
    ctx.fill();
    ctx.globalAlpha = 1;
    
    
    if (
      star.x < -100 || 
      star.x > ctx.canvas.width + 100 || 
      star.y < -100 || 
      star.y > ctx.canvas.height + 100
    ) {
      shootingStars.splice(index, 1);
    }
  });

  return { shootingStars, particles };
}

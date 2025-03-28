export function getParticleConfig(isDark, maxParticles) {
  return {
    particleCount: Math.min(100, maxParticles / 2), 
    colors: isDark 
      ? ['#e384c7', '#9e6593', '#ffffff', '#ff9edb', '#b76ba3']
      : ['#e384c7', '#9e6593', '#ffcef3', '#ff9edb', '#b76ba3'],
    baseSize: 2,
    variantSize: 3,
    baseSpeed: 0.5,
    variantSpeed: 1,
    opacity: isDark ? 0.7 : 0.5,
  };
}

export function createParticle(x, y, config) {
  return {
    x,
    y,
    size: config.baseSize + Math.random() * config.variantSize,
    speedX: (Math.random() - 0.5) * config.variantSpeed,
    speedY: (Math.random() - 0.5) * config.variantSpeed,
    baseSpeedX: (Math.random() - 0.5) * config.variantSpeed,
    baseSpeedY: (Math.random() - 0.5) * config.variantSpeed,
    color: config.colors[Math.floor(Math.random() * config.colors.length)],
    opacity: 0.1 + Math.random() * config.opacity,
    rotation: Math.random() * 360,
    rotationSpeed: (Math.random() - 0.5) * 2,
  };
}

export function createParticles(config) {
  const particles = [];
  for (let i = 0; i < config.particleCount; i++) {
    particles.push(createParticle(
      Math.random() * window.innerWidth,
      Math.random() * window.innerHeight,
      config
    ));
  }
  return particles;
}

export function updateAndDrawParticles(ctx, particles, mouseX, mouseY, scrollFactor, canvas) {
  particles.forEach((p) => {
    
    const dx = mouseX - p.x;
    const dy = mouseY - p.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const maxDistance = 200;
    
    if (distance < maxDistance) {
      const force = (maxDistance - distance) / maxDistance;
      p.speedX += (dx / distance) * force * 0.2;
      p.speedY += (dy / distance) * force * 0.2;
    }
    
    
    p.x += (p.speedX + p.baseSpeedX) * scrollFactor;
    p.y += (p.speedY + p.baseSpeedY) * scrollFactor;
    
    
    p.speedX *= 0.96;
    p.speedY *= 0.96;
    
    
    p.rotation += p.rotationSpeed * scrollFactor;
    
    
    if (p.x < -p.size) p.x = canvas.width + p.size;
    if (p.x > canvas.width + p.size) p.x = -p.size;
    if (p.y < -p.size) p.y = canvas.height + p.size;
    if (p.y > canvas.height + p.size) p.y = -p.size;
    
    
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate((p.rotation * Math.PI) / 180);
    ctx.globalAlpha = p.opacity;
    ctx.fillStyle = p.color;
    
    
    const spikes = 5;
    const outerRadius = p.size;
    const innerRadius = p.size / 2;
    
    ctx.beginPath();
    let rot = (Math.PI / 2) * 3;
    let x = 0;
    let y = 0;
    const step = Math.PI / spikes;
    
    for (let i = 0; i < spikes; i++) {
      x = Math.cos(rot) * outerRadius;
      y = Math.sin(rot) * outerRadius;
      ctx.lineTo(x, y);
      rot += step;
      
      x = Math.cos(rot) * innerRadius;
      y = Math.sin(rot) * innerRadius;
      ctx.lineTo(x, y);
      rot += step;
    }
    
    ctx.lineTo(0, -outerRadius);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  });

  return particles;
}

export function handleParticleClick(particles, clickX, clickY, repelRadius, repelStrength) {
  particles.forEach(p => {
    const dx = p.x - clickX;
    const dy = p.y - clickY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance < repelRadius) {
      const force = (repelRadius - distance) / repelRadius;
      const angle = Math.atan2(dy, dx);
      
      p.speedX += Math.cos(angle) * force * repelStrength;
      p.speedY += Math.sin(angle) * force * repelStrength;
      p.rotationSpeed += (Math.random() - 0.5) * 5;
    }
  });
  
  return particles;
}

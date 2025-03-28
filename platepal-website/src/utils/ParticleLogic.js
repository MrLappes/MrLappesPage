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
    // New properties for enhanced effects
    energy: 1.0, // For energy-based effects
    trail: [], // For trailing effect
    maxTrailLength: Math.floor(Math.random() * 5) // Random trail length
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
    // Store previous position for trail detection
    const prevX = p.x;
    const prevY = p.y;
    
    // Add current position to trail with reduced capacity
    if (Math.random() > 0.7 && p.maxTrailLength > 0) {
      p.trail.push({ x: p.x, y: p.y });
      if (p.trail.length > p.maxTrailLength) {
        p.trail.shift();
      }
    }
    
    // Mouse attraction/repulsion
    const dx = mouseX - p.x;
    const dy = mouseY - p.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const maxDistance = 200;
    
    if (distance < maxDistance) {
      const force = (maxDistance - distance) / maxDistance;
      p.speedX += (dx / distance) * force * 0.2;
      p.speedY += (dy / distance) * force * 0.2;
    }
    
    // Update position with enhanced physics
    p.x += (p.speedX + p.baseSpeedX) * scrollFactor * (1 + p.energy * 0.2);
    p.y += (p.speedY + p.baseSpeedY) * scrollFactor * (1 + p.energy * 0.2);
    
    // Gradual speed reduction (air resistance)
    p.speedX *= 0.96;
    p.speedY *= 0.96;
    
    // Energy dissipation
    p.energy = Math.max(0, p.energy * 0.99);
    
    // Update rotation based on movement and energy
    p.rotation += p.rotationSpeed * scrollFactor * (1 + p.energy * 0.5);
    
    // Screen wrapping with slight randomness for natural look
    let wrapped = false;
    if (p.x < -p.size) { p.x = canvas.width + p.size + Math.random() * 10; wrapped = true; }
    if (p.x > canvas.width + p.size) { p.x = -p.size - Math.random() * 10; wrapped = true; }
    if (p.y < -p.size) { p.y = canvas.height + p.size + Math.random() * 10; wrapped = true; }
    if (p.y > canvas.height + p.size) { p.y = -p.size - Math.random() * 10; wrapped = true; }
    
    // Clear trail if wrapped to prevent lines across screen
    if (wrapped || Math.abs(p.x - prevX) > canvas.width/2 || Math.abs(p.y - prevY) > canvas.height/2) {
      p.trail = [];
    }
    
    // Draw trail if it exists
    if (p.trail.length > 0) {
      ctx.beginPath();
      ctx.moveTo(p.trail[0].x, p.trail[0].y);
      for (let i = 1; i < p.trail.length; i++) {
        ctx.lineTo(p.trail[i].x, p.trail[i].y);
      }
      ctx.lineTo(p.x, p.y);
      ctx.strokeStyle = p.color;
      ctx.globalAlpha = p.opacity * 0.3;
      ctx.lineWidth = p.size / 3;
      ctx.stroke();
    }
    
    // Draw the particle with energy-based glow
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate((p.rotation * Math.PI) / 180);
    ctx.globalAlpha = p.opacity;
    
    // Enhanced glow for energized particles
    if (p.energy > 0.5) {
      ctx.shadowBlur = p.size * p.energy * 2;
      ctx.shadowColor = p.color;
    }
    
    ctx.fillStyle = p.color;
    
    // Draw star shape
    const spikes = 5;
    const outerRadius = p.size * (1 + p.energy * 0.5);
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
      
      // Enhanced push physics based on distance from center
      const pushStrength = repelStrength * force;
      p.speedX += Math.cos(angle) * pushStrength;
      p.speedY += Math.sin(angle) * pushStrength;
      
      // Increased rotation based on push force
      p.rotationSpeed += (Math.random() - 0.5) * 5 * force;
      
      // Add energy to particle for visual effect
      p.energy = Math.min(1.0, p.energy + force);
      
      // Clear trail for more dynamic visual effect
      p.trail = [];
    }
  });
  
  return particles;
}

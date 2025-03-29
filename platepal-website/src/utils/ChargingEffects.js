/**
 * Renders the charging effect with different visuals for left and right click
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} position - Position {x,y} of the charging effect
 * @param {Number} level - Charge level (0-1)
 * @param {String} type - 'left' or 'right' to indicate click type
 * @param {Boolean} isDark - Whether dark mode is enabled
 */
export const renderChargingEffect = (ctx, position, level, type, isDark) => {
  const { x, y } = position;
  
  if (type === 'left') {
    
    const baseColor = isDark ? '#e384c7' : '#9e6593';
    
    
    const pulseRate = 100 - (level * 50); 
    const pulseSize = 1 + Math.sin(Date.now() / pulseRate) * 0.2 * (1 + level * 2);
    const ringSize = 30 * pulseSize;
    
    
    ctx.beginPath();
    ctx.arc(x, y, ringSize, 0, Math.PI * 2);
    ctx.strokeStyle = baseColor;
    ctx.lineWidth = 2 + level * 3;
    ctx.globalAlpha = 0.4 + level * 0.4;
    ctx.stroke();
    
    
    const attractRadius = 200 + (level * 600);
    ctx.beginPath();
    ctx.arc(x, y, attractRadius, 0, Math.PI * 2);
    ctx.strokeStyle = baseColor;
    ctx.lineWidth = 1;
    ctx.globalAlpha = 0.1 + level * 0.1;
    ctx.stroke();
    
    
    ctx.beginPath();
    ctx.arc(x, y, ringSize, -Math.PI/2, Math.PI * 2 * level - Math.PI/2);
    ctx.strokeStyle = baseColor;
    ctx.lineWidth = 4 + level * 4;
    ctx.globalAlpha = 0.7 + level * 0.3;
    ctx.stroke();
    
    
    if (level > 0.7) {
      
      const boltCount = Math.floor(level * 5) + 2;
      const radius = ringSize * 1.2;
      
      for (let i = 0; i < boltCount; i++) {
        const angle = (i / boltCount) * Math.PI * 2 + (Date.now() / 500);
        const startX = x + Math.cos(angle) * radius;
        const startY = y + Math.sin(angle) * radius;
        
        
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        
        
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
      
      
      if (level > 0.9) {
        
        ctx.beginPath();
        ctx.arc(x, y, ringSize * 1.5, 0, Math.PI * 2);
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 2;
        ctx.globalAlpha = 0.3 + Math.sin(Date.now() / 50) * 0.2;
        ctx.stroke();
        
        
        const markerCount = 8;
        for (let i = 0; i < markerCount; i++) {
          const markerAngle = (i / markerCount) * Math.PI * 2;
          const markerX = x + Math.cos(markerAngle) * (ringSize * 1.5);
          const markerY = y + Math.sin(markerAngle) * (ringSize * 1.5);
          
          
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
    
    
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, ringSize * 0.7);
    gradient.addColorStop(0, `rgba(227, 132, 199, ${0.3 + level * 0.5})`);
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

    ctx.beginPath();
    ctx.arc(x, y, ringSize * 0.7, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.globalAlpha = 0.5 + level * 0.5;
    ctx.fill();
  } 
  else {
    
    const baseSize = 40;
    const maxSize = baseSize * (1 + level);
    
    
    const timeWarpRadius = 300 + level * 500;
    const warpIntensity = level * 0.5;
    
    
    for (let i = 0; i < 3; i++) {
      const ringProgress = (Date.now() / (1000 + i * 200)) % 1;
      const ringRadius = timeWarpRadius * ringProgress;
      
      ctx.beginPath();
      ctx.arc(x, y, ringRadius, 0, Math.PI * 2);
      ctx.strokeStyle = isDark ? 'rgba(138, 43, 226, 0.2)' : 'rgba(227, 132, 199, 0.2)';
      ctx.lineWidth = 2 - ringProgress; 
      ctx.globalAlpha = 0.3 * warpIntensity * (1 - ringProgress);
      ctx.stroke();
    }
    
    
    const galaxyColors = isDark 
      ? ['#9e6593', '#8a2be2', '#4b0082', '#000000', '#3a015c'] 
      : ['#e384c7', '#9370db', '#8a2be2', '#4b0082', '#483d8b']; 
    
    
    const outerGlow = ctx.createRadialGradient(x, y, 0, x, y, maxSize * 1.5);
    outerGlow.addColorStop(0, isDark ? 'rgba(158, 101, 147, 0.4)' : 'rgba(227, 132, 199, 0.4)');
    outerGlow.addColorStop(0.5, isDark ? 'rgba(138, 43, 226, 0.2)' : 'rgba(147, 112, 219, 0.2)');
    outerGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
    
    ctx.beginPath();
    ctx.arc(x, y, maxSize * 1.5, 0, Math.PI * 2);
    ctx.fillStyle = outerGlow;
    ctx.fill();
    
    
    const armCount = 3 + Math.floor(level * 2);
    const rotationSpeed = Date.now() / 2000;
    const maxRevolutions = 2 + level;
    
    for (let arm = 0; arm < armCount; arm++) {
      const armColor = galaxyColors[arm % galaxyColors.length];
      const armPhase = (arm / armCount) * Math.PI * 2;
      
      ctx.beginPath();
      
      
      for (let t = 0; t <= maxRevolutions * Math.PI * 2; t += 0.1) {
        const spiralRadius = 5 + (t / (Math.PI * 2)) * maxSize * 0.8;
        const spiralAngle = t + armPhase + rotationSpeed;
        const pointX = x + Math.cos(spiralAngle) * spiralRadius;
        const pointY = y + Math.sin(spiralAngle) * spiralRadius;
        
        
        if (t === 0) {
          ctx.moveTo(pointX, pointY);
        } else {
          ctx.lineTo(pointX, pointY);
        }
      }
      
      ctx.strokeStyle = armColor;
      ctx.lineWidth = 2 + level * 3;
      ctx.globalAlpha = 0.6 + level * 0.4;
      ctx.stroke();
    }
    
    
    const particleCount = Math.floor(20 + level * 60);
    const time = Date.now() / 1000;
    
    for (let i = 0; i < particleCount; i++) {
      const particlePhase = (i / particleCount) * Math.PI * 2;
      const orbitSpeed = 0.5 + (i % 5) * 0.2 + level; 
      const orbitSize = (i % 10) * 3 + 10;
      const distance = orbitSize + (maxSize * 0.7) * (i / particleCount);
      
      
      const spiralFactor = level * 0.3; 
      const angle = particlePhase + time * orbitSpeed + (distance * spiralFactor);
      const distanceMod = Math.max(5, distance - (level * distance * 0.3)); 
      
      const px = x + Math.cos(angle) * distanceMod;
      const py = y + Math.sin(angle) * distanceMod;
      
      
      const starSize = 1 + Math.random() * 2;
      const brightness = 0.5 + Math.random() * 0.5 + (level * 0.3);
      
      ctx.beginPath();
      ctx.arc(px, py, starSize, 0, Math.PI * 2);
      ctx.fillStyle = galaxyColors[i % galaxyColors.length];
      ctx.globalAlpha = brightness;
      ctx.fill();
    }
    
    
    const coreGradient = ctx.createRadialGradient(x, y, 0, x, y, 20 * (0.5 + level * 0.5));
    
    if (isDark) {
      coreGradient.addColorStop(0, '#ffffff');
      coreGradient.addColorStop(0.2, '#9e6593');
      coreGradient.addColorStop(0.5, '#4b0082');
      coreGradient.addColorStop(1, '#000000');
    } else {
      coreGradient.addColorStop(0, '#ffffff');
      coreGradient.addColorStop(0.2, '#e384c7');
      coreGradient.addColorStop(0.5, '#9370db');
      coreGradient.addColorStop(1, '#4b0082');
    }
    
    ctx.beginPath();
    ctx.arc(x, y, 20 * (0.5 + level * 0.5), 0, Math.PI * 2);
    ctx.fillStyle = coreGradient;
    ctx.globalAlpha = 0.8 + level * 0.2;
    ctx.fill();
    
    
    ctx.beginPath();
    ctx.arc(x, y, maxSize, 0, Math.PI * 2 * level);
    ctx.strokeStyle = isDark ? '#ffffff' : '#e384c7';
    ctx.lineWidth = 2;
    ctx.globalAlpha = 0.6;
    ctx.stroke();
  }
  
  
  ctx.globalAlpha = 1;
};

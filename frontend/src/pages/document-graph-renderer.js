export const relationStyles = {
  AMENDS:{color:'#b82436', label:'Sửa đổi', opacity:0.77, dash:[]},
  SUPPLEMENTS:{color:'#aa5100', label:'Bổ sung', opacity:0.79, dash:[8, 4]},
  REPEALS:{color:'#772cb1', label:'Bãi bỏ', opacity:0.83, dash:[2, 4]},
  CITES:{color:'#1256af', label:'Dẫn chiếu', opacity:0.46, dash:[9, 3, 2, 3]},
  BASIS:{color:'#087662', label:'Căn cứ', opacity:0.42, dash:[4, 4]},
};

const drawOrder = ['BASIS', 'CITES', 'SUPPLEMENTS', 'REPEALS', 'AMENDS'];
const edgePath = (path, edge) => {
  path.moveTo(edge.ax, edge.ay);
  path.quadraticCurveTo(edge.mx, edge.my, edge.bx, edge.by);
};

export function createGraphRenderer(ctx, mapCtx, layout, geometry, nodes) {
  const edgeBuckets = new Map(drawOrder.map(type => [type, []]));
  const incident = nodes.map(() => []);
  const nodeBuckets = new Map();
  const cell = 32;
  const key = (x, y) => Math.floor(x / cell) + ':' + Math.floor(y / cell);
  const bounds = {left:0, top:0, right:layout.width, bottom:layout.height};
  for (const edge of geometry) {
    edge.left = Math.min(edge.ax, edge.mx, edge.bx);
    edge.right = Math.max(edge.ax, edge.mx, edge.bx);
    edge.top = Math.min(edge.ay, edge.my, edge.by);
    edge.bottom = Math.max(edge.ay, edge.my, edge.by);
    bounds.left = Math.min(bounds.left, edge.left);
    bounds.top = Math.min(bounds.top, edge.top);
    bounds.right = Math.max(bounds.right, edge.right);
    bounds.bottom = Math.max(bounds.bottom, edge.bottom);
    edgeBuckets.get(edge.type).push(edge);
    incident[edge.from].push(edge);
    if (edge.from !== edge.to) incident[edge.to].push(edge);
  }
  layout.positions.forEach(([x, y], index) => {
    const k = key(x, y);
    if (!nodeBuckets.has(k)) nodeBuckets.set(k, []);
    nodeBuckets.get(k).push(index);
  });
  const worldWidth = bounds.right - bounds.left;
  const worldHeight = bounds.bottom - bounds.top;
  const allPaths = new Map(drawOrder.map(type => {
    const path = new Path2D();
    for (const edge of edgeBuckets.get(type)) edgePath(path, edge);
    return [type, path];
  }));
  const cache = document.createElement('canvas');
  const resolution = Math.min(1.5, Math.sqrt(3800000 / (worldWidth * worldHeight)));
  cache.width = Math.ceil(worldWidth * resolution);
  cache.height = Math.ceil(worldHeight * resolution);
  const cacheCtx = cache.getContext('2d');
  let cachedTypes;
  const markerSize = index => 2.5 + Math.min(3, Math.log1p(incident[index].length) * 0.45);
  const intersects = (edge, view) => edge.right >= view.left && edge.left <= view.right &&
    edge.bottom >= view.top && edge.top <= view.bottom;

  function paintEdges(target, paths, enabled, scale, patterned = false, opacity = 1) {
    for (const type of drawOrder) {
      if (!enabled.has(type)) continue;
      const style = relationStyles[type];
      target.strokeStyle = style.color;
      target.globalAlpha = style.opacity * opacity;
      target.lineWidth = (type === 'AMENDS' || type === 'REPEALS' ? 1.15 : 0.85) / scale;
      if (patterned) target.setLineDash(style.dash.map(length => length / scale));
      target.stroke(paths.get(type));
    }
    target.setLineDash([]);
    target.globalAlpha = 1;
  }

  function paintNodes(target, view = bounds) {
    const available = new Path2D();
    const missing = new Path2D();
    layout.positions.forEach(([x, y], index) => {
      if (x < view.left || x > view.right || y < view.top || y > view.bottom) return;
      const radius = markerSize(index);
      const path = nodes[index].full_text_status === 'AVAILABLE' ? available : missing;
      path.moveTo(x + radius, y);
      path.arc(x, y, radius, 0, 2 * Math.PI);
    });
    target.fillStyle = '#243c56';
    target.fill(available);
    target.fillStyle = '#8e9faf';
    target.fill(missing);
  }

  function refreshCache(enabled) {
    const signature = drawOrder.filter(type => enabled.has(type)).join(',');
    if (signature === cachedTypes) return;
    cacheCtx.setTransform(resolution, 0, 0, resolution, -bounds.left * resolution, -bounds.top * resolution);
    cacheCtx.clearRect(bounds.left, bounds.top, worldWidth + 1, worldHeight + 1);
    paintEdges(cacheCtx, allPaths, enabled, resolution);
    paintNodes(cacheCtx);
    cachedTypes = signature;
  }

  function paintHighlight(index, enabled, scale, view) {
    if (index === null) return;
    ctx.lineWidth = 2.4 / scale;
    for (const edge of incident[index]) {
      if (!enabled.has(edge.type) || !intersects(edge, view)) continue;
      const style = relationStyles[edge.type];
      ctx.beginPath();
      edgePath(ctx, edge);
      ctx.strokeStyle = style.color;
      ctx.setLineDash(style.dash.map(length => length / scale));
      ctx.stroke();
      const angle = Math.atan2(edge.by - edge.ay, edge.bx - edge.ax);
      const px = (edge.ax + 2 * edge.mx + edge.bx) / 4;
      const py = (edge.ay + 2 * edge.my + edge.by) / 4;
      const size = 6 / scale;
      ctx.beginPath();
      ctx.moveTo(px + size * Math.cos(angle), py + size * Math.sin(angle));
      ctx.lineTo(px + size * Math.cos(angle + 2.45), py + size * Math.sin(angle + 2.45));
      ctx.lineTo(px + size * Math.cos(angle - 2.45), py + size * Math.sin(angle - 2.45));
      ctx.closePath();
      ctx.fillStyle = style.color;
      ctx.fill();
    }
    ctx.setLineDash([]);
    const [px, py] = layout.positions[index];
    ctx.beginPath();
    ctx.arc(px, py, Math.max(7 / scale, markerSize(index) + 1), 0, 2 * Math.PI);
    ctx.fillStyle = '#132848';
    ctx.fill();
    ctx.strokeStyle = 'white';
    ctx.stroke();
  }

  function draw({width, height, dpr, x, y, scale, enabled, active, detailed}) {
    refreshCache(enabled);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    ctx.translate(x, y);
    ctx.scale(scale, scale);
    const view = {left:-x/scale-8, right:(width-x)/scale+8,
      top:-y/scale-8, bottom:(height-y)/scale+8};
    if (detailed) {
      const visiblePaths = new Map(drawOrder.map(type => {
        const path = new Path2D();
        if (enabled.has(type)) {
          for (const edge of edgeBuckets.get(type)) if (intersects(edge, view)) edgePath(path, edge);
        }
        return [type, path];
      }));
      paintEdges(ctx, visiblePaths, enabled, scale, true, active === null ? 1 : 0.32);
      paintNodes(ctx, view);
    } else {
      ctx.globalAlpha = active === null ? 1 : 0.38;
      ctx.drawImage(cache, bounds.left, bounds.top, cache.width / resolution, cache.height / resolution);
      ctx.globalAlpha = 1;
    }
    paintHighlight(active, enabled, scale, view);
  }

  function drawMap(width, height, view, dpr) {
    const scale = Math.min(width/worldWidth, height/worldHeight);
    const x = (width-worldWidth*scale)/2 - bounds.left*scale;
    const y = (height-worldHeight*scale)/2 - bounds.top*scale;
    mapCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
    mapCtx.clearRect(0, 0, width, height);
    mapCtx.drawImage(cache, x+bounds.left*scale, y+bounds.top*scale, worldWidth*scale, worldHeight*scale);
    mapCtx.strokeStyle = '#203e6b';
    mapCtx.lineWidth = 1.5;
    mapCtx.strokeRect(x+view.left*scale, y+view.top*scale, view.width*scale, view.height*scale);
    return {x, y, scale};
  }

  function hit(px, py, radius) {
    let nearest = null;
    let limit = radius;
    for (let x = Math.floor((px-radius)/cell); x <= Math.floor((px+radius)/cell); x++) {
      for (let y = Math.floor((py-radius)/cell); y <= Math.floor((py+radius)/cell); y++) {
        for (const index of nodeBuckets.get(x+':'+y) || []) {
          const [nx, ny] = layout.positions[index];
          const distance = Math.hypot(nx-px, ny-py);
          if (distance < limit) {
            nearest = index;
            limit = distance;
          }
        }
      }
    }
    return nearest;
  }

  return {bounds, worldWidth, worldHeight, incident, edgeBuckets, draw, drawMap, hit};
}

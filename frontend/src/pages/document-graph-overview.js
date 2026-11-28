import {createGraphRenderer, relationStyles} from './document-graph-renderer.js';
const spacing = 23;

export function arrange(nodes, edges) {
  const adjacency = nodes.map(() => new Set());
  for (const [from, to] of edges) {
    adjacency[from].add(to);
    adjacency[to].add(from);
  }
  const order = nodes.map((_, i) => i).sort((a, b) => adjacency[b].size - adjacency[a].size);
  const groupIndex = new Int32Array(nodes.length).fill(-1);
  const seeds = [];
  const groups = [];
  const queue = [];
  function startGroup(node) {
    groupIndex[node] = groups.length;
    groups.push([node]);
    queue.push(node);
  }
  for (const node of order) {
    if (seeds.length >= Math.ceil(Math.sqrt(nodes.length) / 2) || adjacency[node].size < 4) break;
    if (seeds.some(seed => adjacency[node].has(seed))) continue;
    seeds.push(node);
    startGroup(node);
  }
  function spread() {
    for (let i = 0; i < queue.length; i++) {
      const node = queue[i];
      for (const peer of adjacency[node]) {
        if (groupIndex[peer] !== -1) continue;
        groupIndex[peer] = groupIndex[node];
        groups[groupIndex[node]].push(peer);
        queue.push(peer);
      }
    }
    queue.length = 0;
  }
  spread();
  const isolates = [];
  for (const node of order) {
    if (groupIndex[node] !== -1) continue;
    if (adjacency[node].size === 0) {
      isolates.push(node);
      continue;
    }
    startGroup(node);
    spread();
  }
  groups.sort((a, b) => b.length - a.length);
  if (isolates.length) groups.push(isolates);

  const positions = new Array(nodes.length);
  const shelfWidth = Math.ceil(Math.sqrt(nodes.length) * 1.6);
  let left = 1;
  let top = 1;
  let shelfHeight = 0;
  let extentX = 2;
  for (const group of groups) {
    const cols = Math.ceil(Math.sqrt(group.length * 1.45));
    const rows = Math.ceil(group.length / cols);
    if (left > 1 && left + cols > shelfWidth) {
      left = 1;
      top += shelfHeight + 1;
      shelfHeight = 0;
    }
    group.forEach((node, i) => {
      const dx = ((node * 19) % 13 - 6) / 35;
      const dy = ((node * 29) % 11 - 5) / 35;
      positions[node] = [(left + i % cols + dx) * spacing, (top + Math.floor(i / cols) + dy) * spacing];
    });
    left += cols + 1;
    extentX = Math.max(extentX, left);
    shelfHeight = Math.max(shelfHeight, rows);
  }
  return {positions, width:extentX * spacing, height:(top + shelfHeight + 1) * spacing};
}

export function edgeGeometry(positions, edges) {
  const parallel = new Map();
  const totals = new Map();
  const pair = (from, to) => Math.min(from, to) + ':' + Math.max(from, to);
  for (const [from, to] of edges) {
    const key = pair(from, to);
    totals.set(key, (totals.get(key) || 0) + 1);
  }
  return edges.map(([from, to, type]) => {
    const key = pair(from, to);
    const lane = parallel.get(key) || 0;
    parallel.set(key, lane + 1);
    const [ax, ay] = positions[from];
    const [bx, by] = positions[to];
    const dx = bx - ax;
    const dy = by - ay;
    const length = Math.hypot(dx, dy) || 1;
    const offset = (lane - (totals.get(key) - 1) / 2) * 5 * (from < to ? 1 : -1);
    return {from, to, type, ax, ay, bx, by,
      mx:(ax + bx) / 2 - dy / length * offset, my:(ay + by) / 2 + dx / length * offset};
  });
}

export function createGraphOverview(container, make, request, openNeighborhood) {
  const toolbar = make('div', undefined, 'graph-overview-tools');
  const message = make('p', undefined, 'meta');
  message.setAttribute('role', 'status');
  const stage = make('div', undefined, 'graph-overview-stage');
  const canvas = make('canvas', undefined, 'graph-overview-canvas');
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', 'Sơ đồ toàn bộ đồ thị văn bản');
  const map = make('canvas', undefined, 'graph-minimap');
  map.setAttribute('aria-label', 'Bản đồ nhỏ của khung đang xem');
  const tooltip = make('div', '', 'graph-overview-tooltip');
  tooltip.hidden = true;
  stage.append(canvas, map, tooltip);
  const selected = make('div', undefined, 'graph-overview-selection');
  selected.setAttribute('aria-live', 'polite');
  const filters = make('fieldset', undefined, 'graph-edge-filters');
  filters.append(make('legend', 'Loại quan hệ'));
  const number = new Intl.NumberFormat('vi-VN');
  const ctx = canvas.getContext('2d');
  const mapCtx = map.getContext('2d');
  const enabled = new Set(Object.keys(relationStyles));
  const inputs = new Map();
  const counts = new Map();
  let data, renderer, layout, identities, pending, mapTransform;
  let width = 1, height = 1, dpr = 1, fitScale = 1;
  let scale = 1, x = 0, y = 0, frame = 0, idleTimer = 0;
  let active = null, pointer = null, detailed = false;

  function button(label, action) {
    const control = make('button', label, 'secondary');
    control.type = 'button';
    control.addEventListener('click', action);
    return control;
  }

  function updateSelection() {
    if (active === null) {
      selected.replaceChildren();
      return;
    }
    const node = data.nodes[active];
    const edges = renderer.incident[active].filter(edge => enabled.has(edge.type));
    const outgoing = edges.filter(edge => edge.from === active).length;
    const label = node.number || node.title || node.id;
    selected.replaceChildren(make('strong', label),
      make('span', number.format(outgoing) + ' đi · ' + number.format(edges.length - outgoing) + ' đến', 'meta'),
      button('Xem bằng chứng quanh nút', () => openNeighborhood(node.id)),
      button('Bỏ chọn', () => { active = null; updateSelection(); redraw(); }));
  }

  function changeFilters() {
    if (!data) return;
    for (const [type, input] of inputs) input.checked = enabled.has(type);
    const visible = [...enabled].reduce((sum, type) => sum + renderer.edgeBuckets.get(type).length, 0);
    message.textContent = 'Đang hiện ' + number.format(data.nodes.length) + ' nút · ' + number.format(visible) +
      (visible === data.edges.length ? ' cạnh' : ' / ' + number.format(data.edges.length) + ' cạnh đang hiện');
    updateSelection();
    redraw(true);
  }

  for (const [type, style] of Object.entries(relationStyles)) {
    const item = make('label');
    item.style.setProperty('--relation-color', style.color);
    const input = make('input');
    input.type = 'checkbox';
    input.checked = true;
    input.disabled = true;
    inputs.set(type, input);
    const count = make('span', '', 'graph-filter-count');
    count.setAttribute('aria-hidden', 'true');
    counts.set(type, count);
    input.addEventListener('change', () => {
      if (input.checked) enabled.add(type);
      else enabled.delete(type);
      changeFilters();
    });
    item.append(input, make('span', '', 'graph-filter-swatch'), make('span', style.label), count);
    filters.append(item);
  }
  const clearEdges = button('Chỉ hiện nút', () => { enabled.clear(); changeFilters(); });
  const resetEdges = button('Hiện tất cả cạnh', () => {
    for (const type of inputs.keys()) enabled.add(type);
    changeFilters();
  });
  filters.append(clearEdges, resetEdges);
  filters.disabled = true;

  const percent = new Intl.NumberFormat('vi-VN', {style:'percent'});
  const zoomValue = make('output', '100%', 'graph-zoom-value');
  zoomValue.setAttribute('aria-label', 'Mức thu phóng');
  const panel = container.closest('.document-graph');
  const expand = button('Toàn màn hình', () => {
    setExpanded(!panel.classList.contains('graph-expanded'));
  });
  expand.setAttribute('aria-pressed', 'false');
  function setExpanded(expanded) {
    panel.classList.toggle('graph-expanded', expanded);
    expand.textContent = expanded ? 'Thoát toàn màn hình' : 'Toàn màn hình';
    expand.setAttribute('aria-pressed', String(expanded));
    expand.focus();
  }
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && panel.classList.contains('graph-expanded')) setExpanded(false);
  });
  toolbar.append(button('Thu nhỏ', () => zoom(1/1.4)), zoomValue,
    button('Phóng to', () => zoom(1.4)), button('Vừa khung', fit), expand);
  container.append(filters, toolbar, message, stage, selected,
    make('p', 'Kéo để di chuyển. Chọn nút để hiện chiều cạnh. Bấm bản đồ nhỏ để chuyển vùng.', 'meta'));

  function paint() {
    frame = 0;
    if (!renderer || container.hidden) return;
    renderer.draw({width, height, dpr, x, y, scale, enabled, active,
      detailed:detailed && scale >= fitScale * 2.5});
    if (mapCtx) {
      const mw = map.clientWidth, mh = map.clientHeight;
      mapTransform = renderer.drawMap(mw, mh,
        {left:-x/scale, top:-y/scale, width:width/scale, height:height/scale}, dpr);
    }
  }

  function redraw(interacting = false) {
    if (interacting) {
      detailed = false;
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => { detailed = true; redraw(); }, 140);
    }
    if (!frame) frame = requestAnimationFrame(paint);
  }

  function updateZoom() {
    zoomValue.textContent = percent.format(scale/fitScale);
  }

  function fit() {
    if (!renderer) return;
    scale = fitScale;
    x = (width - renderer.worldWidth * scale) / 2 - renderer.bounds.left * scale;
    y = (height - renderer.worldHeight * scale) / 2 - renderer.bounds.top * scale;
    tooltip.hidden = true;
    updateZoom();
    redraw(true);
  }

  function resize() {
    if (container.hidden || !renderer) return;
    const resized = width !== canvas.clientWidth || height !== canvas.clientHeight;
    const centerX = (width / 2 - x) / scale;
    const centerY = (height / 2 - y) / scale;
    const ratio = scale / fitScale;
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    if (!width || !height) return;
    dpr = Math.min(2, window.devicePixelRatio || 1);
    function buffer(surface, w, h) {
      const bw = Math.max(1, Math.round(w*dpr));
      const bh = Math.max(1, Math.round(h*dpr));
      if (surface.width !== bw) surface.width = bw;
      if (surface.height !== bh) surface.height = bh;
    }
    buffer(canvas, width, height);
    buffer(map, map.clientWidth, map.clientHeight);
    fitScale = Math.min(width/renderer.worldWidth, height/renderer.worldHeight)*0.96;
    if (resized && ratio > 1.01) {
      scale = fitScale * ratio;
      x = width/2 - centerX * scale;
      y = height/2 - centerY * scale;
      updateZoom();
      redraw(true);
    } else if (resized) fit();
    else redraw();
  }

  function zoom(factor, aroundX = width/2, aroundY = height/2) {
    if (!renderer) return;
    const next = Math.min(Math.max(scale*factor, fitScale*0.6), fitScale*32);
    x = aroundX - (aroundX - x)*next/scale;
    y = aroundY - (aroundY - y)*next/scale;
    scale = next;
    tooltip.hidden = true;
    updateZoom();
    redraw(true);
  }

  function moveTo(px, py) {
    x = width/2-px*scale;
    y = height/2-py*scale;
    tooltip.hidden = true;
    redraw(true);
  }

  function select(index, center = false) {
    active = index;
    if (center) {
      scale = Math.max(scale, fitScale*4);
      updateZoom();
      moveTo(...layout.positions[index]);
    }
    updateSelection();
    redraw();
  }

  function load() {
    if (data) {
      resize();
      return Promise.resolve(data);
    }
    if (!ctx) {
      message.textContent = 'Trình duyệt này chưa hỗ trợ Canvas.';
      return Promise.resolve();
    }
    if (pending) return pending;
    message.textContent = 'Đang tải toàn bộ đồ thị…';
    pending = request('/api/demo/document-graph/overview').then(result => {
      layout = arrange(result.nodes, result.edges);
      const geometry = edgeGeometry(layout.positions, result.edges);
      identities = new Map(result.nodes.map((node, index) => [node.id, index]));
      renderer = createGraphRenderer(ctx, mapCtx, layout, geometry, result.nodes);
      for (const [type, input] of inputs) {
        input.disabled = false;
        counts.get(type).textContent = number.format(renderer.edgeBuckets.get(type).length);
      }
      filters.disabled = false;
      data = result;
      resize();
      changeFilters();
      return data;
    }).catch(error => {
      message.textContent = error.message;
    }).finally(() => { pending = null; });
    return pending;
  }

  function hit(event) {
    const rect = canvas.getBoundingClientRect();
    return renderer.hit((event.clientX-rect.left-x)/scale, (event.clientY-rect.top-y)/scale,
      Math.max(9/scale, 6));
  }

  function showTooltip(event) {
    const index = hit(event);
    tooltip.hidden = index === null;
    if (index === null) return;
    const node = data.nodes[index];
    tooltip.textContent = (node.number || node.title || node.id) +
      ' · ' + number.format(renderer.incident[index].length) + ' cạnh';
    const box = stage.getBoundingClientRect();
    tooltip.style.left = Math.max(4, Math.min(event.clientX-box.left+12, box.width-tooltip.offsetWidth-5)) + 'px';
    tooltip.style.top = Math.max(4, event.clientY-box.top-32) + 'px';
  }

  new ResizeObserver(resize).observe(canvas);
  canvas.addEventListener('wheel', event => {
    if (document.activeElement !== canvas) return;
    event.preventDefault();
    zoom(event.deltaY < 0 ? 1.2 : 1/1.2, event.offsetX, event.offsetY);
  }, {passive:false});
  canvas.addEventListener('pointerdown', event => {
    if (!renderer || !event.isPrimary || event.button !== 0) return;
    canvas.setPointerCapture(event.pointerId);
    tooltip.hidden = true;
    pointer = {id:event.pointerId, startX:event.clientX, startY:event.clientY, x, y, moved:false};
  });
  canvas.addEventListener('pointermove', event => {
    if (!renderer) return;
    if (!pointer) {
      if (event.pointerType === 'mouse') showTooltip(event);
      return;
    }
    if (pointer.id !== event.pointerId) return;
    const dx = event.clientX - pointer.startX;
    const dy = event.clientY - pointer.startY;
    if (Math.hypot(dx, dy) < 4 && !pointer.moved) return;
    pointer.moved = true;
    x = pointer.x + dx;
    y = pointer.y + dy;
    redraw(true);
  });
  canvas.addEventListener('pointerleave', () => { tooltip.hidden = true; });
  canvas.addEventListener('pointerup', event => {
    if (pointer?.id !== event.pointerId) return;
    if (!pointer.moved) {
      const index = hit(event);
      if (index !== null) select(index);
    }
    pointer = null;
  });
  canvas.addEventListener('lostpointercapture', () => { pointer = null; });
  canvas.addEventListener('keydown', event => {
    const keys = {ArrowLeft:[40,0], ArrowRight:[-40,0], ArrowUp:[0,40], ArrowDown:[0,-40]};
    if (!renderer) return;
    if (event.key in keys) {
      event.preventDefault();
      x += keys[event.key][0];
      y += keys[event.key][1];
      redraw(true);
    } else if (['+', '=', '-', '0'].includes(event.key)) {
      event.preventDefault();
      if (event.key === '0') fit();
      else zoom(event.key === '-' ? 1/1.4 : 1.4);
    }
  });
  map.addEventListener('click', event => {
    if (!mapTransform) return;
    moveTo((event.offsetX-mapTransform.x)/mapTransform.scale, (event.offsetY-mapTransform.y)/mapTransform.scale);
  });

  return {load, async focus(id) {
    await load();
    const index = identities?.get(id);
    if (index !== undefined) select(index, true);
  }};
}

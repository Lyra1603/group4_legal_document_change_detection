import {createGraphOverview} from './document-graph-overview.js';

import {relationStyles} from './document-graph-renderer.js';

const labels = Object.fromEntries(Object.entries(relationStyles).map(([key, value]) => [key, value.label]));
const statuses = {AVAILABLE:'Có toàn văn DOCX', MISSING_FULL_TEXT:'Chưa có toàn văn', READ_ERROR:'Không đọc được DOCX'};
const endpoint = '/api/demo/document-graph';

export function mountDocumentGraph(make, request) {
  const panel = make('section', undefined, 'workspace document-graph');
  const heading = make('h2', 'Đồ thị quan hệ văn bản pháp luật');
  heading.id = 'document-graph-title';
  panel.setAttribute('aria-labelledby', heading.id);
  const totals = make('p', 'Đang tải đồ thị…', 'meta');
  totals.setAttribute('role', 'status');
  const form = make('form', undefined, 'graph-search');
  form.hidden = true;
  const label = make('label', 'Tìm theo số hiệu hoặc tên văn bản');
  label.htmlFor = 'graph-search';
  const input = make('input');
  input.id = 'graph-search';
  input.type = 'search';
  input.maxLength = 240;
  input.placeholder = 'Ví dụ 08/2014/TT-BTP';
  form.append(label, input, make('button', 'Tìm văn bản', 'secondary'));
  const results = make('div', undefined, 'graph-results');
  results.setAttribute('aria-live', 'polite');
  const neighborhood = make('div', undefined, 'graph-neighborhood');
  neighborhood.setAttribute('aria-live', 'polite');
  const evidence = make('section', undefined, 'graph-evidence');
  evidence.tabIndex = -1;
  evidence.hidden = true;
  const switcher = make('div', undefined, 'graph-overview-tools graph-view-controls');
  const fullView = make('div', undefined, 'graph-overview');
  panel.append(heading, totals, switcher, form, results, fullView, neighborhood, evidence);
  document.querySelector('[aria-labelledby="upload-title"]').before(panel);

  const number = new Intl.NumberFormat('vi-VN');
  const title = node => node.number || node.number_raw || node.title || node.id;
  const status = node => statuses[node.full_text_status] || 'Chưa xác định nguồn';
  let selectionRun = 0;
  let searchRun = 0;
  let selectionId;
  let fullMode = true;

  function button(text, action, css = 'secondary') {
    const control = make('button', text, css);
    control.type = 'button';
    control.addEventListener('click', action);
    return control;
  }

  const overview = createGraphOverview(fullView, make, request, id => setMode(false, id));
  const fullButton = button('Toàn bộ đồ thị', () => setMode(true));
  const detailButton = button('Quanh một văn bản', () => setMode(false));
  switcher.append(fullButton, detailButton);

  function showTotals(nodes, edges) {
    totals.textContent = number.format(nodes) + ' nút · ' + number.format(edges) + ' cạnh';
    form.hidden = !nodes;
  }

  async function setMode(full, id = selectionId) {
    fullMode = full;
    fullView.hidden = !full;
    neighborhood.hidden = full;
    evidence.hidden = true;
    fullButton.setAttribute('aria-pressed', String(full));
    detailButton.setAttribute('aria-pressed', String(!full));
    if (full) {
      const snapshot = await overview.load();
      if (fullMode && snapshot) showTotals(snapshot.node_count, snapshot.edge_count);
      else if (fullMode) totals.textContent = '';
    } else {
      select(id);
    }
  }

  function addPaging(parent, data, update) {
    if (data.total <= data.limit) return;
    const nav = make('div', undefined, 'graph-paging');
    const previous = button('Trang trước', () => update(data.offset - data.limit));
    previous.disabled = data.offset === 0;
    const next = button('Trang sau', () => update(data.offset + data.limit));
    next.disabled = data.offset + data.limit >= data.total;
    const range = (data.offset + 1) + '–' + Math.min(data.offset + data.limit, data.total);
    nav.append(previous, make('span', range + ' / ' + number.format(data.total)), next);
    parent.append(nav);
  }

  function showEvidence(edge, source, target) {
    evidence.hidden = false;
    evidence.replaceChildren(make('h3', title(source) + ' → ' + title(target)),
      make('p', labels[edge.relation] || edge.relation));
    if (edge.scope?.length) evidence.append(make('p', 'Phạm vi ' + edge.scope.join(' · '), 'meta'));
    if (edge.target_resolution === 'OUTSIDE_CATALOG') {
      evidence.append(make('p', 'Đích ngoài danh mục. Số hiệu được giữ theo đoạn nguồn.', 'meta'));
    }
    evidence.append(make('p', 'Nguồn ' + (source.source?.path || source.id), 'meta'));
    for (const entry of edge.evidence) {
      evidence.append(make('p', entry.document_id + ' · ' + entry.source_refs.join(', '), 'meta'),
        make('blockquote', entry.quote, 'instruction'));
    }
    evidence.focus();
    evidence.scrollIntoView({block:'nearest'});
  }

  function drawNetwork(node, neighbors, byNeighbor) {
    const ns = 'http://www.w3.org/2000/svg';
    function svgElement(tag, attrs, text) {
      const element = document.createElementNS(ns, tag);
      for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, value);
      if (text) element.textContent = text;
      return element;
    }
    function interactive(element, label, action) {
      element.setAttribute('tabindex', '0');
      element.setAttribute('role', 'button');
      element.setAttribute('aria-label', label);
      element.addEventListener('click', action);
      element.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          action();
        }
      });
    }

    const network = svgElement('svg', {viewBox:'0 0 1000 530', class:'graph-network',
      role:'group', 'aria-label':'Sơ đồ nút và mũi tên quan hệ văn bản'});
    const defs = svgElement('defs', {});
    for (const [type, style] of Object.entries(relationStyles)) {
      const marker = svgElement('marker', {id:'document-graph-arrow-' + type, viewBox:'0 0 10 10',
        refX:9, refY:5, markerWidth:7, markerHeight:7, orient:'auto-start-reverse'});
      marker.append(svgElement('path', {d:'M 0 0 L 10 5 L 0 10 z', fill:style.color}));
      defs.append(marker);
    }
    network.append(defs);
    const cx = 500;
    const cy = 265;
    const points = neighbors.map((peer, i) => {
      const angle = 2 * Math.PI * i / neighbors.length - Math.PI / 2;
      return {peer, x:cx + 362 * Math.cos(angle), y:cy + 196 * Math.sin(angle)};
    });

    for (const {peer, x, y} of points) {
      const dx = x - cx;
      const dy = y - cy;
      const length = Math.hypot(dx, dy);
      const ux = dx / length;
      const uy = dy / length;
      const edges = byNeighbor.get(peer.id);
      const outgoing = edges.find(edge => edge.source_id === node.id);
      const incoming = edges.find(edge => edge.target_id === node.id);
      for (const edge of [outgoing, incoming].filter(Boolean)) {
        const fromCurrent = edge === outgoing;
        const offset = outgoing && incoming ? (fromCurrent ? -9 : 9) : 0;
        const shiftX = -uy * offset;
        const shiftY = ux * offset;
        const a = [cx + ux * 46 + shiftX, cy + uy * 46 + shiftY];
        const b = [x - ux * 30 + shiftX, y - uy * 30 + shiftY];
        const [from, to] = fromCurrent ? [a, b] : [b, a];
        const group = svgElement('g', {class:'graph-network-link'});
        const coords = {x1:from[0], y1:from[1], x2:to[0], y2:to[1]};
        const edgeLabel = labels[edge.relation] || edge.relation;
        const style = relationStyles[edge.relation];
        if (style) group.style.setProperty('--relation-color', style.color);
        group.append(svgElement('line', {...coords, class:'graph-link-hit'}),
          svgElement('line', {...coords, class:'graph-link-stroke',
            'stroke-dasharray':style?.dash.join(' ') || 'none',
            'marker-end':'url(#document-graph-arrow-' + edge.relation + ')'}),
          svgElement('title', {}, title(fromCurrent ? node : peer) + ' → ' + title(fromCurrent ? peer : node) + ' · ' + edgeLabel));
        const mx = (a[0] + b[0]) / 2 - uy * (offset ? Math.sign(offset) * 8 : 0);
        const my = (a[1] + b[1]) / 2 + ux * (offset ? Math.sign(offset) * 8 : 0);
        const count = edges.filter(item => (item.source_id === node.id) === fromCurrent).length;
        group.append(svgElement('text', {x:mx, y:my - 5, 'text-anchor':'middle', class:'graph-link-label'},
          edgeLabel + (count > 1 ? ' +' + (count - 1) : '')));
        interactive(group, edgeLabel + ' · ' + title(peer),
          () => showEvidence(edge, fromCurrent ? node : peer, fromCurrent ? peer : node));
        network.append(group);
      }
    }

    for (const {peer, x, y} of points) {
      const label = title(peer);
      const group = svgElement('g', {class:'graph-network-node'});
      group.append(svgElement('circle', {cx:x, cy:y, r:28}),
        svgElement('text', {x, y:y + 45, 'text-anchor':'middle'}, label.length > 32 ? label.slice(0, 30) + '…' : label),
        svgElement('title', {}, label + ' · ' + status(peer)));
      interactive(group, 'Chọn ' + label, () => select(peer.id));
      network.append(group);
    }
    network.append(svgElement('circle', {cx, cy, r:42, class:'graph-network-focus'}),
      svgElement('text', {x:cx, y:cy + 60, 'text-anchor':'middle', class:'graph-network-title'}, title(node)));
    const viewport = make('div', undefined, 'graph-network-viewport');
    viewport.append(network);
    return viewport;
  }

  function renderNeighborhood(data) {
    neighborhood.replaceChildren();
    const {node} = data;
    if (!node) {
      neighborhood.append(make('p', 'Đồ thị chưa có văn bản.'));
      return;
    }
    const current = make('div', undefined, 'graph-current');
    current.append(make('h3', title(node)));
    if (node.title && node.title !== title(node)) current.append(make('p', node.title));
    current.append(make('p', status(node) + ' · ' + number.format(data.total) + ' cạnh đi/đến', 'meta'));
    current.append(make('p', [node.id, node.source?.path].filter(Boolean).join(' · '), 'meta'));
    neighborhood.append(current);
    if (!data.total) {
      neighborhood.append(drawNetwork(node, [], new Map()), make('p', 'Văn bản này chưa có cạnh trong đồ thị.'));
      return;
    }
    const connections = make('div', undefined, 'graph-connections');
    const byNeighbor = new Map(data.neighbors.map(neighbor => [neighbor.id, []]));
    for (const edge of data.edges) {
      const neighbor = edge.source_id === node.id ? edge.target_id : edge.source_id;
      byNeighbor.get(neighbor).push(edge);
    }
    neighborhood.append(drawNetwork(node, data.neighbors, byNeighbor));
    for (const other of data.neighbors) {
      const card = make('div', undefined, 'graph-neighbor');
      const linked = button(title(other), () => select(other.id), 'graph-node');
      linked.title = other.title || title(other);
      card.append(linked, make('span', status(other), 'meta'));
      const relations = make('div', undefined, 'graph-relations');
      for (const edge of byNeighbor.get(other.id)) {
        const fromCurrent = edge.source_id === node.id;
        const name = labels[edge.relation] || edge.relation;
        const relation = button(fromCurrent ? '→ ' + name : name + ' →',
          () => showEvidence(edge, fromCurrent ? node : other, fromCurrent ? other : node), 'graph-edge');
        const style = relationStyles[edge.relation];
        if (style) relation.style.setProperty('--relation-color', style.color);
        relation.title = (fromCurrent ? 'Cạnh đi' : 'Cạnh đến') +
          (edge.scope?.length ? ' · ' + edge.scope.join(' · ') : '');
        relations.append(relation);
      }
      card.append(relations);
      connections.append(card);
    }
    neighborhood.append(make('p', '→ Nhãn là cạnh đi · Nhãn → là cạnh đến', 'meta'), connections);
    addPaging(neighborhood, data, next => select(node.id, next));
  }

  async function select(id, offset = 0) {
    const run = ++selectionRun;
    const params = new URLSearchParams({offset});
    if (id) params.set('node_id', id);
    evidence.hidden = true;
    neighborhood.replaceChildren(make('p', 'Đang đọc quan hệ…', 'meta'));
    try {
      const data = await request(endpoint + '?' + params);
      if (run !== selectionRun) return;
      selectionId = data.node?.id;
      if (!fullMode) showTotals(data.node_count, data.edge_count);
      renderNeighborhood(data);
    } catch (error) {
      if (run !== selectionRun) return;
      if (!id) totals.textContent = '';
      neighborhood.replaceChildren(make('p', error.message, 'message error'));
    }
  }

  async function search(query, offset = 0) {
    const run = ++searchRun;
    results.replaceChildren(make('p', 'Đang tìm…', 'meta'));
    try {
      const params = new URLSearchParams({q:query, offset, limit:12});
      const data = await request(endpoint + '?' + params);
      if (run !== searchRun) return;
      results.replaceChildren();
      if (!data.total) {
        results.append(make('p', 'Không tìm thấy văn bản phù hợp.'));
        return;
      }
      results.append(make('p', number.format(data.total) + ' văn bản tìm thấy', 'meta'));
      const list = make('ul');
      for (const node of data.matches) {
        const row = make('li');
        const text = [...new Set([title(node), node.title, status(node)].filter(Boolean))].join(' · ');
        row.append(button(text, () => {
          selectionId = node.id;
          if (fullMode) overview.focus(node.id);
          else select(node.id);
        }, 'graph-node'));
        list.append(row);
      }
      results.append(list);
      addPaging(results, data, next => search(query, next));
    } catch (error) {
      if (run === searchRun) results.replaceChildren(make('p', error.message, 'message error'));
    }
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    search(input.value.trim());
  });
  setMode(true);
}

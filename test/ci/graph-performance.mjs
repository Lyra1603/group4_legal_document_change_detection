import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {performance} from 'node:perf_hooks';
import {arrange, edgeGeometry} from '../../frontend/src/pages/document-graph-overview.js';
import {createGraphRenderer, relationStyles} from '../../frontend/src/pages/document-graph-renderer.js';

// Observe drawing calls on the real topology. Browser rendering is verified separately.
class Path {
  moveTo() {}
  quadraticCurveTo() {}
  arc() {}
}
function context() {
  const calls = {stroke:0, drawImage:0};
  return {calls, stroke() {calls.stroke++;}, drawImage() {calls.drawImage++;},
    setTransform() {}, clearRect() {}, translate() {}, scale() {}, setLineDash() {}, fill() {}};
}
const [, , graphPath, reportPath] = process.argv;
const graph = JSON.parse(await readFile(graphPath, 'utf-8'));
const started = performance.now();
globalThis.Path2D = Path;
const cache = context();
globalThis.document = {createElement: () => ({getContext: () => cache})};
const indices = new Map(graph.nodes.map((node, i) => [node.id, i]));
const topology = graph.edges.map(edge => [indices.get(edge.source_id), indices.get(edge.target_id), edge.relation]);
const layout = arrange(graph.nodes, topology);
const canvas = context();
const renderer = createGraphRenderer(canvas, context(), layout, edgeGeometry(layout.positions, topology), graph.nodes);
const enabled = new Set(Object.keys(relationStyles));
const viewport = {width:900, height:560, dpr:1, x:0, y:0, scale:0.5, enabled, active:null, detailed:false};
renderer.draw(viewport);
const cachedStrokes = cache.calls.stroke;
assert.equal(cachedStrokes, enabled.size);
const ready = performance.now();
for (let i = 0; i < 120; i++) renderer.draw({...viewport, x:i, y:i/2, scale:0.5+i/400});
const finished = performance.now();
assert.equal(cache.calls.stroke, cachedStrokes, 'Pan/zoom rebuilt the cached edge layer');
assert.equal(canvas.calls.stroke, 0, 'Pan/zoom re-rasterized vector edges');
assert.equal(canvas.calls.drawImage, 121);
enabled.clear();
enabled.add('AMENDS');
renderer.draw(viewport);
assert.equal(cache.calls.stroke, cachedStrokes + 1, 'Changing filters must rebuild cached edges');
renderer.draw({...viewport, detailed:true, scale:4});
assert.equal(canvas.calls.stroke, 1, 'Still viewport must be redrawn in detail');
assert.equal(renderer.hit(...layout.positions[0], 1), 0);
const report = {nodes:graph.nodes.length, edges:topology.length, simulated_frames:120,
  vector_restrokes_during_pan:0, setup_ms:Math.round(ready-started),
  simulated_cpu_ms:Math.round(finished-ready), graphics_backend:'CALL_COUNT_DOUBLE'};
await writeFile(reportPath, JSON.stringify(report) + '\n');
console.log(report);

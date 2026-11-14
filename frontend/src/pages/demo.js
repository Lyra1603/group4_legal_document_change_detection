// Small same-origin demo UI. All document text is rendered as text nodes, never HTML.
const $ = selector => document.querySelector(selector);
const state = {v1: [], s: [], references: [], busy: false, config: null, report: null};
const labels = {SUCCESS: 'Hoàn thành', PARTIAL: 'Cần kiểm tra thêm', FAILED: 'Xử lý thất bại'};
const statusDetails = {
  SUCCESS: 'Các mục đã có thể hiển thị theo dữ liệu backend trả về.',
  PARTIAL: 'Một số mục hoặc căn cứ chưa đủ để kết luận; không đồng nghĩa không có thay đổi.',
  FAILED: 'Không tạo được phân tích hoàn chỉnh; hãy đọc lỗi và cảnh báo bên dưới.'
};
const operations = {AMEND: 'Sửa đổi', ADD: 'Bổ sung', REPEAL: 'Bãi bỏ', UNRESOLVED: 'Chưa xác định thao tác'};
const groups = {TIME_QUANTITY:'Thời gian / số lượng', SUBJECT_OBJECT:'Chủ thể / đối tượng',
  RIGHTS_DUTIES_ACTIONS:'Quyền / nghĩa vụ', CONDITIONS_EXCEPTIONS:'Điều kiện / ngoại lệ',
  PROCEDURE_AUTHORITY:'Thủ tục / thẩm quyền', CONSEQUENCES_SANCTIONS:'Hậu quả / chế tài',
  DEFINITIONS_REFERENCES:'Định nghĩa / dẫn chiếu', SCOPE_EFFECT_TRANSITION:'Phạm vi / hiệu lực', WORDING_ONLY:'Chỉ đổi diễn đạt'};

function node(tag, text, className) {
  const result = document.createElement(tag);
  if (text !== undefined && text !== null) result.textContent = String(text);
  if (className) result.className = className;
  return result;
}
function message(text = '', error = false) {
  const box = $('#form-message');
  box.textContent = text; box.className = `message${error ? ' error' : ''}`; box.hidden = !text;
}
function setBusy(busy) {
  state.busy = busy;
  $('#compare-form').querySelectorAll('button,input,select').forEach(el => {el.disabled = busy;});
  $('#submit-button').disabled = busy || !state.config || !state.v1.length || !state.s.length;
  $('#processing').hidden = !busy;
  $('#compare-form').setAttribute('aria-busy', String(busy));
}
function clearReport() {
  state.report = null; $('#results').hidden = true;
}
function size(bytes) {return `${(bytes / 1024).toFixed(1)} KB`;}
function renderFiles() {
  for (const [role, id] of [['v1','v1-list'],['s','s-list'],['references','references-list']]) {
    const list = document.getElementById(id); list.replaceChildren();
    state[role].forEach((file, index) => {
      const row = node('li'); row.append(node('span', file.name, 'file-name'), node('span',size(file.size),'file-size'));
      const remove = node('button', '×', 'remove'); remove.type = 'button';
      remove.setAttribute('aria-label',`Bỏ file ${file.name}`); remove.disabled = state.busy;
      remove.addEventListener('click', () => {state[role].splice(index,1); clearReport(); renderFiles();});
      row.append(remove); list.append(row);
    });
  }
  setBusy(state.busy);
}
function validateFiles(selection) {
  if (!state.config) throw new Error('Chưa lấy được cấu hình từ máy chủ. Hãy tải lại trang.');
  const all = [...selection.v1,...selection.s,...selection.references];
  if (selection.references.length > state.config.max_reference_files) throw new Error(`Chỉ nhận tối đa ${state.config.max_reference_files} tài liệu tham chiếu.`);
  let total = 0;
  for (const file of all) {
    if (!/\.(docx|pdf)$/i.test(file.name)) throw new Error(`File ${file.name}: chỉ nhận DOCX hoặc PDF có lớp chữ.`);
    if (!file.size) throw new Error(`File ${file.name} đang rỗng.`);
    if (file.size > state.config.max_file_bytes) throw new Error(`File ${file.name} vượt giới hạn ${Math.round(state.config.max_file_bytes/1048576)} MB.`);
    total += file.size;
  }
  if (total > state.config.max_total_bytes) throw new Error('Tổng dung lượng các file vượt giới hạn cho phép.');
}
function choose(role, files) {
  if (state.busy) return;
  const incoming = Array.from(files);
  if (!incoming.length) return;
  if (role !== 'references' && incoming.length !== 1) {message('Mỗi ô V1 hoặc S chỉ nhận một file.',true); return;}
  const next = {...state, [role]: role === 'references' ? [...state.references] : incoming};
  if (role === 'references') {
    for (const file of incoming) if (!next.references.some(f => f.name === file.name && f.size === file.size && f.lastModified === file.lastModified)) next.references.push(file);
  }
  try {validateFiles(next); state[role] = next[role]; clearReport(); message(); renderFiles();}
  catch (error) {message(error.message, true);}
}
for (const [id, role] of [['v1-file','v1'],['s-file','s'],['reference-files','references']]) {
  document.getElementById(id).addEventListener('change', event => {choose(role,event.target.files); event.target.value = '';});
}
document.querySelectorAll('.upload-slot').forEach(slot => {
  const drop = slot.querySelector('.dropzone');
  for (const type of ['dragenter','dragover']) drop.addEventListener(type,event => {event.preventDefault(); if (!state.busy) drop.classList.add('dragover');});
  drop.addEventListener('dragleave',()=>drop.classList.remove('dragover'));
  drop.addEventListener('drop',event=>{event.preventDefault();drop.classList.remove('dragover');choose(slot.dataset.role,event.dataTransfer.files);});
});

function sourceLabel(evidence, identities) {
  const file = identities[evidence.document_id]?.filename || evidence.document_id;
  return `${file} · ${evidence.document_id} · ${(evidence.source_refs || []).join(', ')}`;
}
function addIssue(container, issue, error = false) {
  const box = node('div', undefined, `report-issue${error ? ' error' : ''}`);
  box.append(node('strong',issue.message || issue.code || 'Chưa xử lý được.'));
  const metadata = [issue.stage, issue.code].filter(Boolean).join(' · ');
  if (metadata) box.append(node('div',metadata,'source'));
  container.append(box);
}
function pane(title, text, changes, side) {
  const box = node('div',undefined,'text-pane'); box.append(node('div',title,'pane-title'));
  const content = node('pre',undefined,'text-content');
  let cursor = 0;
  for (const change of changes || []) {
    const start = change[`${side}_start`], end = change[`${side}_end`];
    // Python offsets count Unicode code points; use Array.from, not JS UTF-16 indexing.
    const characters = Array.from(text || '');
    if (!Number.isInteger(start) || !Number.isInteger(end) || start < cursor || end > characters.length) continue;
    content.append(document.createTextNode(characters.slice(cursor,start).join('')));
    if (end > start) content.append(node('mark',characters.slice(start,end).join(''),side === 'old' ? 'old-mark' : 'new-mark'));
    cursor = end;
  }
  content.append(document.createTextNode(Array.from(text || '').slice(cursor).join('')));
  box.append(content); return box;
}
function renderItem(result, warnings, identities, index) {
  const item = result.amendment;
  const card = node('article',undefined,'result-card');
  const header = node('div',undefined,'item-header');
  header.append(node('h3',`${String(index+1).padStart(2,'0')} · ${item.target_locator || 'Chưa xác định đích'}`));
  const badges = node('div'); badges.append(node('span',operations[item.operation] || item.operation,'badge'));
  if (item.applicability === 'OTHER_DOCUMENT') badges.append(node('span','Văn bản khác','badge warning'));
  else if (item.applicability === 'UNRESOLVED') badges.append(node('span','Đích chưa rõ','badge error'));
  else badges.append(node('span','Cần kiểm tra','badge warning'));
  header.append(badges); card.append(header);
  card.append(node('blockquote',item.instruction.quote,'instruction'), node('p',sourceLabel(item.instruction,identities),'source'));
  const local = warnings.filter(w=>w.amendment_id === item.amendment_id);
  if (result.text_diff === null) {
    if (local.length) for (const warning of local) addIssue(card,warning);
    else addIssue(card,{message:item.review_reason || 'Chưa xử lý được chỉ dẫn này.',code:'NOT_ANALYZED'});
  } else {
    for (const warning of local) addIssue(card,warning);
    const diff = node('div',undefined,'diff-grid');
    diff.append(pane('V1 · Nội dung trước sửa đổi',item.before_text,result.text_diff.changes,'old'),
      pane(item.after_basis === 'DERIVED' ? 'Sau sửa đổi · Suy ra từ chỉ dẫn (DERIVED)' : 'S · Nội dung thay thế trích nguyên văn',item.after_text,result.text_diff.changes,'new'));
    card.append(diff);
    const analysis = node('div',undefined,'analysis-grid');
    const semantic = node('div'); semantic.append(node('h4','Phân tích ý nghĩa'));
    const changes = result.semantic_diff?.changes || [];
    if (!changes.length) semantic.append(node('p','Chưa có kết luận ngữ nghĩa để hiển thị.'));
    for (const change of changes) {
      const meaningLabel = change.is_meaningful_change === null
        ? 'Chưa biết: thiếu căn cứ'
        : change.is_meaningful_change ? 'Có đổi nghĩa' : 'Không đổi nghĩa';
      semantic.append(node('span', meaningLabel, `badge ${change.is_meaningful_change === false ? '' : 'warning'}`));
      semantic.append(node('p',change.diff_details));
      if (change.review_reason) semantic.append(node('p',change.review_reason));
    }
    const score = node('div'); score.append(node('h4','Phân loại & mức tác động'));
    for (const entry of result.scoring || []) {
      score.append(node('span',entry.significance || 'Chưa chấm mức tác động','badge warning'));
      score.append(node('p',entry.category ? groups[entry.category] || entry.category : 'Chưa xác định nhóm tác động.'));
      score.append(node('p',entry.reason));
    }
    analysis.append(semantic,score); card.append(analysis);
  }
  const all = [...item.evidence,...(item.context?.evidence || [])];
  const unique = [...new Map(all.map(e=>[JSON.stringify(e),e])).values()];
  const details = node('details'); details.append(node('summary',`${unique.length} bằng chứng nguồn · xem nguyên văn`));
  for (const evidence of unique) {
    const block = node('div',undefined,'evidence');
    block.append(node('div',sourceLabel(evidence,identities),'source'),node('p',evidence.quote)); details.append(block);
  }
  card.append(details); return card;
}
function renderReport(report) {
  state.report = report;
  const identities = Object.fromEntries([report.base_document,report.amendment_document,...(report.reference_documents||[])].filter(Boolean).map(d=>[d.document_id,d]));
  const meta = $('#report-meta'); meta.replaceChildren();
  meta.append(node('span',labels[report.status] || report.status,`badge ${report.status === 'FAILED' ? 'error' : 'warning'}`));
  meta.append(node('p',statusDetails[report.status] || 'Trạng thái do backend trả về.','status-description'));
  meta.append(node('p',`V1: ${report.base_document?.filename || ''} · S: ${report.amendment_document?.filename || ''}`,'meta'));
  meta.append(node('p',`Mã đối chiếu: ${report.comparison_id}`,'source'));
  const results = report.results || [], summary = $('#report-summary'); summary.replaceChildren();
  for (const [value,label] of [[results.length,'Chỉ dẫn được ghi nhận'],[results.filter(r=>r.text_diff !== null).length,'Mục đã so sánh chữ'],[results.filter(r=>r.text_diff === null).length,'Mục chưa phân tích được']]) {
    const stat = node('div',undefined,'stat'); stat.append(node('strong',value),node('span',label)); summary.append(stat);
  }
  const issues = $('#report-issues'); issues.replaceChildren();
  for (const error of report.errors || []) addIssue(issues,error,true);
  const parserWarnings = (report.warnings || []).filter(w=>!w.amendment_id && w.stage === 'parser');
  for (const warning of report.warnings || []) if (!warning.amendment_id && warning.stage !== 'parser') addIssue(issues,warning);
  if (parserWarnings.length) {
    const details = node('details');
    details.append(node('summary',`${parserWarnings.length} cảnh báo đọc tài liệu · mở để kiểm tra giới hạn nguồn`));
    const grouped = new Map();
    for (const warning of parserWarnings) {
      const key = `${warning.code}:${warning.message}`;
      if (grouped.has(key)) grouped.get(key).count++;
      else grouped.set(key,{...warning,count:1});
    }
    for (const warning of grouped.values()) addIssue(details,{...warning,message:warning.count > 1 ? `${warning.message} (${warning.count} lần)` : warning.message});
    issues.append(details);
  }
  const items = $('#report-items'); items.replaceChildren();
  if (!results.length) addIssue(items,{message:'Chưa tạo được mục phân tích. Hãy xem lỗi/cảnh báo phía trên; kết quả này không có nghĩa là văn bản không thay đổi.'});
  results.forEach((result,index)=>items.append(renderItem(result,report.warnings || [],identities,index)));
  $('#results').hidden = false;
  $('#results').scrollIntoView({behavior:'smooth',block:'start'});
}

$('#compare-form').addEventListener('submit', async event => {
  event.preventDefault(); if (state.busy) return;
  try {validateFiles(state); if (!state.v1.length || !state.s.length) throw new Error('Cần chọn đủ V1 và S.');}
  catch(error) {message(error.message,true); return;}
  clearReport(); message(); setBusy(true);
  const data = new FormData(); data.append('doc_v1',state.v1[0]); data.append('doc_s',state.s[0]);
  for (const file of state.references) data.append('reference_files',file);
  const controller = new AbortController();
  const timer = setTimeout(()=>controller.abort(),(state.config.deadline_seconds+30)*1000);
  try {
    const response = await fetch('/api/compare',{method:'POST',body:data,signal:controller.signal});
    const report = await response.json();
    if (Array.isArray(report.results) && report.comparison_id) renderReport(report);
    else {
      const detail = report.detail;
      const category = response.status >= 400 && response.status < 500 ? 'Lỗi đầu vào'
        : response.status >= 500 ? 'Lỗi máy chủ' : 'Phản hồi không hợp lệ';
      const detailMessage = Array.isArray(detail) ? 'Thiếu hoặc sai file bắt buộc.'
        : typeof detail === 'string' ? detail : detail?.message || 'Máy chủ chưa trả được kết quả.';
      throw new Error(`${category} (HTTP ${response.status}): ${detailMessage}`);
    }
  } catch(error) {
    message(error.name === 'AbortError' ? 'Hết thời gian chờ phản hồi. Máy chủ có thể vẫn đang kết thúc xử lý; hãy kiểm tra lại trước khi gửi tiếp.'
      : error.message === 'Failed to fetch' ? 'Lỗi kết nối: không kết nối được máy chủ. Kiểm tra dịch vụ rồi thử lại.'
      : error.message,true);
  } finally {clearTimeout(timer); setBusy(false);}
});

$('#load-sample').addEventListener('click',async()=>{
  const sample = state.config?.samples.find(s=>s.id === $('#sample-select').value);
  if (!sample || state.busy) {message('Hãy chọn một bộ dữ liệu mẫu trước.'); return;}
  setBusy(true); message();
  try {
    const files = await Promise.all(['v1','s'].map(async role=>{
      const response = await fetch(`/api/demo/files/${encodeURIComponent(sample.id)}/${role}`);
      if (!response.ok) throw new Error('Không tải được bộ dữ liệu trong data/raw.');
      return new File([await response.blob()],sample[role],{type:'application/vnd.openxmlformats-officedocument.wordprocessingml.document'});
    }));
    const next = {v1:[files[0]],s:[files[1]],references:[]}; validateFiles(next);
    Object.assign(state,next); clearReport(); renderFiles();
    message('Đã nạp V1 và S từ data/raw. Đây là tài liệu trong repo; chưa xác minh hiệu lực hiện tại.');
  } catch(error) {message(error.message,true);} finally {setBusy(false);}
});
$('#download-json').addEventListener('click',()=>{
  if (!state.report) return;
  const url = URL.createObjectURL(new Blob([JSON.stringify(state.report,null,2)],{type:'application/json;charset=utf-8'}));
  const anchor = node('a'); anchor.href = url; anchor.download = `pocs-${state.report.comparison_id}.json`;
  document.body.append(anchor); anchor.click(); anchor.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
});

try {
  const response = await fetch('/api/demo/config');
  if (!response.ok) throw new Error('Không lấy được cấu hình demo.');
  state.config = await response.json();
  for (const sample of state.config.samples) {
    const option = node('option',sample.label); option.value = sample.id; $('#sample-select').append(option);
  }
  $('#limits').textContent = `Tối đa ${Math.round(state.config.max_file_bytes/1048576)} MB/file · ${state.config.max_reference_files} file tham chiếu`;
  renderFiles();
} catch(error) {message('Không kết nối được API demo. Hãy chạy backend.demo:app rồi tải lại trang.',true);}

// Team-facing UI. Only talks to our backend; never requests/stores an API key.
import {mountDocumentGraph} from './document-graph.js';

const make = (tag, text, cls) => {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (cls) el.className = cls;
  return el;
};
async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 190000);
  try {
    const response = await fetch(path, {...options, signal:controller.signal});
    const text = await response.text();
    let body;
    try { body = JSON.parse(text); }
    catch { throw new Error(`HTTP ${response.status}: máy chủ trả dữ liệu không phải JSON.`); }
    if (!response.ok) throw new Error(`${body.detail?.code || response.status}: ${body.detail?.message || 'Dịch vụ chưa sẵn sàng.'}`);
    return body;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Hết thời gian chờ. Máy chủ có thể vẫn đang xử lý; kiểm tra trạng thái trước khi gửi lại.');
    throw error;
  } finally { clearTimeout(timer); }
}
function evidenceList(parent, entries = []) {
  for (const item of entries) {
    const box = make('details');
    box.append(make('summary', `${item.document_id} · ${(item.source_refs || []).join(', ')}`), make('pre',item.quote || ''));
    parent.append(box);
  }
}
function showRetrievalSources(container, graph) {
  container.replaceChildren();
  if (!graph?.nodes?.length) return;
  const parent=make('details');
  parent.append(make('summary','Nguồn thực thể và liên hệ LightRAG'));
  container.append(parent);
  for (const node of graph.nodes) {
    const detail=make('details');detail.append(make('summary',node.id),make('p',node.description));
    evidenceList(detail,node.sources);parent.append(detail);
  }
  const edgeDetails=make('details');edgeDetails.append(make('summary','Các cạnh và nguồn đối chiếu'));
  for(const edge of graph.edges){edgeDetails.append(make('h4',`${edge.source} → ${edge.target}`),make('p',edge.description));evidenceList(edgeDetails,edge.sources);}
  parent.append(edgeDetails);
  const audit=make('details');audit.append(make('summary','Kiểm tra nguồn graph và giới hạn'),make('pre',JSON.stringify(graph.audit,null,2)));parent.append(audit);
}

const config=await request('/api/demo/config');
if(config.mode==='SHARED_CONTEXT'){
  mountDocumentGraph(make, request);
  document.querySelector('.version').textContent='Demo máy chủ chung';
  const scope=document.querySelector('.scope');scope.replaceChildren(make('strong','LightRAG do máy chủ quản lý'),make('span','Không nhập API key trên trình duyệt. Có thể nộp S trước để tìm V1; truy xuất chưa tự xác nhận hiệu lực. Semantic/Scorer hiện là baseline quy tắc cục bộ.'));
  const panel=make('section',undefined,'workspace shared-context');
  panel.append(make('h2','Truy xuất LightRAG trên metadata mẫu'),make('p','Hai bản ghi Bộ luật Dân sự 2005 và 2015 từ th1nhng0; chưa nạp toàn văn, chưa xác minh tình trạng hiệu lực hiện tại. Kết quả truy xuất đi kèm vị trí nguồn.'),make('p','Toàn nhóm dùng chung kho demo này. Nút index chỉ nạp bộ metadata đã chọn trên máy chủ.'));
  const status=make('p','Đang đọc trạng thái…'),error=make('p','','message error');error.setAttribute('role','alert');
  const start=make('button','Index metadata thật','primary'),refresh=make('button','Cập nhật trạng thái','secondary');
  const sourceBox=make('div'),graphBox=make('div'),results=make('div');
  const form=make('form'),label=make('label','Câu hỏi truy xuất metadata'),input=make('textarea');
  input.id='metadata-query';label.htmlFor=input.id;input.maxLength=8000;input.rows=3;
  input.value='Bộ luật Dân sự số 91/2015/QH13 do cơ quan nào ban hành, ngày có hiệu lực ghi trong metadata là gì?';
  const submit=make('button','Truy xuất thật','primary');submit.type='submit';
  form.append(label,input,submit);panel.append(status,error,start,refresh,sourceBox,form,results,graphBox);
  const metadata = make('details',undefined,'workspace shared-context');
  metadata.append(make('summary','Thử truy xuất LightRAG trên kho metadata mẫu'),panel);
  document.querySelector('footer').before(metadata);
  let polling=null,alive=true,operationError='';
  function render(data){
    status.textContent=`Kho: ${data.state} · nguồn: ${data.source_kind} · toàn văn: chưa nạp`;
    error.textContent=operationError || (data.issues||[]).join(' · ');
    if (data.state === 'FAILED' && !operationError) {
      const hints = {
        INDEX_PROVIDER_RATE_LIMITED: 'Dịch vụ AI đã chạm hạn mức. Quản trị kiểm tra quota trước khi thử lại.',
        INDEX_PROVIDER_ACCESS_DENIED: 'Dịch vụ AI từ chối truy cập. Quản trị kiểm tra key, quyền model và số dư.',
        INDEX_PROVIDER_UNAVAILABLE: 'Dịch vụ AI tạm thời không phản hồi. Quản trị kiểm tra lại sau.',
        REAL_SERVICE_CONFIGURATION_REQUIRED: 'Máy chủ thiếu cấu hình model hoặc embedding.',
      };
      const hint = (data.issues || []).map(code => hints[code]).find(Boolean);
      error.textContent += ' — ' + (hint || 'Chưa lập được chỉ mục. Quản trị kiểm tra cấu hình dịch vụ AI.');
    }
    start.disabled=!config.provider_configured||data.state!=='IDLE';submit.disabled=data.state!=='READY';
    if(!config.provider_configured)error.textContent='Máy chủ chưa cấu hình đủ provider. Thành viên không cần nhập key trên UI.';
    sourceBox.replaceChildren();
    for(const [id,source] of Object.entries(data.sources||{})){
      const d=make('details');d.append(make('summary',`${id} · ${source.metadata.title} · ID ${source.dataset_id}`),make('pre',JSON.stringify(source,null,2)));sourceBox.append(d);
    }
    showRetrievalSources(graphBox,data.graph);
    if(data.state==='INDEXING'&&!polling)polling=setInterval(()=>load().catch(e=>{error.textContent=e.message;}),2500);
    if(data.state!=='INDEXING'&&polling){clearInterval(polling);polling=null;}
  }
  async function load(){if(alive)render(await request('/api/demo/corpus'));}
  start.addEventListener('click',async()=>{start.disabled=true;operationError='';error.textContent='';try{render(await request('/api/demo/corpus/index',{method:'POST'}));}catch(e){operationError=e.message;error.textContent=e.message;await load();}});
  refresh.addEventListener('click',()=>load().catch(e=>{error.textContent=e.message;}));
  form.addEventListener('submit',async event=>{
    event.preventDefault();submit.disabled=true;operationError='';error.textContent='';
    try{const data=await request('/api/demo/corpus/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:input.value})});
      results.replaceChildren(make('h3','Bằng chứng truy xuất thật — không phải kết luận tác động'));evidenceList(results,data.evidence);showRetrievalSources(graphBox,data.graph);
    }catch(e){operationError=e.message;error.textContent=e.message;}finally{await load();}
  });
  window.addEventListener('pagehide',()=>{alive=false;if(polling)clearInterval(polling);});
  const contextPanel=make('section',undefined,'workspace shared-context');contextPanel.hidden=true;
  document.querySelector('#results').after(contextPanel);
  let activeComparison = null;
  window.addEventListener('pocs:clear-report',()=>{
    activeComparison = null;
    contextPanel.hidden = true;
  });
  window.addEventListener('pocs:report',async event=>{
    const comparison = event.detail.comparison_id;
    activeComparison = comparison;
    contextPanel.hidden=false;contextPanel.replaceChildren(make('h2','LightRAG của lượt đối chiếu'));
    try{const data=await request('/api/demo/contexts/'+encodeURIComponent(comparison));
      if (activeComparison !== comparison) return;
      contextPanel.append(make('p',`Trạng thái: ${data.state} · phạm vi: các block được dẫn làm bằng chứng và tài liệu tham chiếu đã nộp.`));
      if(data.issues.length)contextPanel.append(make('p',data.issues.join(' · '),'message error'));
      for(const item of data.items){contextPanel.append(make('h3',item.amendment_id),make('p',item.verified?'Truy xuất đã kiểm tra nguồn':'Truy xuất chưa được xác minh'),make('pre',item.general_context));evidenceList(contextPanel,item.evidence);}
      const graph=make('div');contextPanel.append(graph);showRetrievalSources(graph,data.graph);
    }catch(e){if (activeComparison === comparison) contextPanel.append(make('p',e.message,'message error'));}
  });
  await load();
}

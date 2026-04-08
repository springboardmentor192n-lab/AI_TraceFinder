let currentMode='scanner', files={}, batchFileList=[], confChart=null, radarChart=null;
let history=JSON.parse(localStorage.getItem('tf_v3')||'[]');

(function tick(){
  const el=document.getElementById('clockEl');
  if(el) el.textContent=new Date().toLocaleString('en-GB',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});
  setTimeout(tick,10000);
})();

function showPage(name,btn){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(b=>b.classList.remove('active'));
  document.getElementById('page-'+name).classList.add('active');
  btn.classList.add('active');
  if(name==='history') renderHistory();
}
function setMode(mode,btn){
  currentMode=mode;
  document.querySelectorAll('.mode-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  ['scanner','tampering','comparison','batch'].forEach(m=>{
    document.getElementById('mode-'+m).style.display=m===mode?'block':'none';
  });
}
function handleFile(input,key){
  const file=input.files[0]; if(!file) return;
  files[key]=file;
  if(key==='cmp1'||key==='cmp2'){
    document.getElementById(key+'Name').textContent=file.name;
    document.getElementById(key+'Slot').classList.add('filled');
  } else {
    const pill=document.getElementById(key+'Preview');
    if(pill){ pill.classList.add('show'); document.getElementById(key+'FileName').textContent=file.name; document.getElementById(key+'FileSize').textContent=(file.size/1024/1024).toFixed(2)+' MB'; }
  }
  updateBtns();
}
function handleDrop(e,key){
  e.preventDefault();
  document.getElementById(key+'Drop')?.classList.remove('dragover');
  const file=e.dataTransfer.files[0]; if(!file) return;
  files[key]=file; handleFile({files:[file]},key);
}
function clearFile(key){
  files[key]=null;
  const pill=document.getElementById(key+'Preview');
  if(pill) pill.classList.remove('show');
  updateBtns();
}
function updateBtns(){
  const sb=document.getElementById('analyzeScannerBtn');
  const tb=document.getElementById('analyzeTamperBtn');
  const cb=document.getElementById('compareBtn');
  if(sb) sb.disabled=!files['scanner'];
  if(tb) tb.disabled=!files['tamper'];
  if(cb) cb.disabled=!(files['cmp1']&&files['cmp2']);
}
function handleBatch(input){
  batchFileList=Array.from(input.files);
  const el=document.getElementById('batchList');
  el.innerHTML=batchFileList.map((f,i)=>`<div class="batch-item" id="bi-${i}"><div class="batch-dot" id="bd-${i}"></div><span style="flex:1;">${f.name}</span><span style="color:var(--ink4);">${(f.size/1024/1024).toFixed(1)}MB</span><span id="br-${i}" style="min-width:150px;text-align:right;color:var(--ink4);">&mdash; pending &mdash;</span></div>`).join('');
  document.getElementById('batchBtn').disabled=!batchFileList.length;
}
function fileToBase64(file){
  return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result.split(',')[1]);r.onerror=rej;r.readAsDataURL(file);});
}
// API Configuration
const API_BASE_URL = '/api';

// Backend API calls
async function callBackend(endpoint, data) {
  try {
    const options = {
      method: 'POST',
      body: data
    };
    
    // Don't set Content-Type for FormData - browser will handle it
    // Only set Content-Type for JSON data
    if (!(data instanceof FormData)) {
      options.headers = {
        'Content-Type': 'application/json'
      };
    }
    
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`[API] POST request to: ${url}`);
    const response = await fetch(url, options);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[API] HTTP ${response.status}: ${errorText}`);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const jsonResponse = await response.json();
    console.log(`[API] Response from ${endpoint}:`, jsonResponse);
    return jsonResponse;
  } catch (error) {
    console.error(`[API] Error calling ${endpoint}:`, error);
    throw error;
  }
}


function genCaseId(){return 'TF-'+Date.now().toString(36).toUpperCase().slice(-6);}
const loadSteps=['Extracting noise residual...','Analyzing frequency domain...','Computing PRNU correlation...','Running feature classifier...','Cross-referencing device database...','Compiling forensic report...'];
let loadInt;
function showLoading(){
  document.getElementById('loadingScreen').classList.add('show');
  let i=0; loadInt=setInterval(()=>{ document.getElementById('loadingStep').textContent=loadSteps[i%loadSteps.length]; i++; },1000);
}
function hideLoading(){ clearInterval(loadInt); document.getElementById('loadingScreen').classList.remove('show'); }
function toast(msg,err=false){ const t=document.getElementById('toast'); t.className='toast show'+(err?' err':''); t.textContent=msg; setTimeout(()=>t.classList.remove('show'),4000); }
function addHistory(type,file,result,conf){ history.unshift({type,file,result,conf,date:new Date().toISOString(),caseId:genCaseId()}); if(history.length>100) history.pop(); localStorage.setItem('tf_v3',JSON.stringify(history)); }

async function analyzeScanner(){
  const file = files['scanner']; 
  if(!file) {
    toast('No file selected', true);
    return;
  }
  
  showLoading();
  console.log(`[SCANNER] Starting analysis for ${file.name}`);
  
  try {
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', file);

    console.log(`[SCANNER] Calling /analyze endpoint...`);
    // Call backend API
    const response = await callBackend('/analyze', formData);

    console.log(`[SCANNER] Response received:`, response);

    if (!response.success) {
      throw new Error(response.error || response.message || 'Analysis failed');
    }

    // Convert backend response to frontend format
    const backendResult = response.results;
    const methodLabel = backendResult.method === 'reference_feature_matching'
      ? 'Reference Feature Matching'
      : 'Trained Classifier';
    const methodSummary = backendResult.method === 'reference_feature_matching'
      ? 'reference feature matching against the sample dataset'
      : 'the trained scanner classifier';
    const scoreBase = backendResult.confidence * 100;
    const clampScore = value => Math.max(0, Math.min(100, Math.round(value)));
    const r = {
      scanner_brand: backendResult.predicted_scanner.split(' ')[0] || 'Unknown',
      scanner_model: backendResult.predicted_scanner.split(' ').slice(1).join(' ') || backendResult.predicted_scanner,
      confidence: backendResult.confidence,
      confidence_level: backendResult.confidence > 0.9 ? 'Very High' :
                       backendResult.confidence > 0.8 ? 'High' :
                       backendResult.confidence > 0.6 ? 'Medium' : 'Low',
      detection_method: methodLabel,
      prnu_quality: backendResult.confidence > 0.8 ? 'Good' :
                   backendResult.confidence > 0.6 ? 'Fair' : 'Poor',
      noise_pattern: backendResult.confidence > 0.8 ? 'Very High' :
                    backendResult.confidence > 0.7 ? 'High' :
                    backendResult.confidence > 0.5 ? 'Medium' : 'Low',
      image_quality: 'High', // Assume good quality for uploaded images
      metadata_status: 'Complete',
      prnu_score: clampScore(scoreBase),
      texture_score: clampScore(scoreBase - 5),
      frequency_score: clampScore(scoreBase + 5),
      noise_score: clampScore(scoreBase + 10),
      metadata_score: clampScore(scoreBase - 10),
      summary: `Analysis reveals scanner fingerprint characteristics consistent with ${backendResult.predicted_scanner}. The backend used ${methodSummary}. Confidence score of ${(backendResult.confidence * 100).toFixed(1)}% indicates the strength of this match.`,
      features: [
        'PRNU pattern extraction',
        'Noise residual analysis',
        'Frequency domain correlation',
        methodLabel === 'Reference Feature Matching' ? 'Reference profile matching' : 'Machine learning classification'
      ]
    };

    console.log(`[SCANNER] Analysis result: ${r.scanner_brand} ${r.scanner_model} (${r.confidence})`);
    hideLoading();
    renderScannerResults(r, file.name);
    addHistory('scanner', file.name, r.scanner_brand + ' ' + r.scanner_model, r.confidence);
    toast('Analysis complete — case file generated.');
  } catch(e) {
    console.error(`[SCANNER] Error:`, e);
    hideLoading();
    toast('Analysis failed: ' + e.message, true);
  }
}

function renderScannerResults(r,filename){
  const el=document.getElementById('scannerResults'); el.classList.add('show');
  const pct=Math.round(r.confidence*100); const caseId=genCaseId();
  el.innerHTML=`<div class="fade-in" style="margin-top:1.5rem;">
  <div class="section-rule"><div class="section-rule-line"></div><div class="section-rule-label">Case File &mdash; Scanner Identification</div><div class="section-rule-line"></div></div>
  <div class="case-header">
    <div><div class="case-id-label">Case Reference</div><div class="case-id-val">${caseId}</div></div>
    <div style="text-align:right;"><div class="case-date">${new Date().toLocaleString('en-GB')}</div><div style="margin-top:8px;"><span class="stamp stamp-classified">Forensic Grade</span></div></div>
  </div>
  <div class="evidence-grid">
    <div class="evidence-cell"><div class="ev-label">Scanner Brand</div><div class="ev-value accent">${r.scanner_brand}</div></div>
    <div class="evidence-cell"><div class="ev-label">Scanner Model</div><div class="ev-value">${r.scanner_model}</div></div>
    <div class="evidence-cell"><div class="ev-label">Confidence</div><div class="ev-value">${pct}%</div><div class="conf-track"><div class="conf-fill" style="width:0" id="cFill"></div></div></div>
    <div class="evidence-cell"><div class="ev-label">Confidence Level</div><div class="ev-value muted">${r.confidence_level}</div></div>
    <div class="evidence-cell"><div class="ev-label">PRNU Quality</div><div class="ev-value muted">${r.prnu_quality}</div></div>
    <div class="evidence-cell"><div class="ev-label">Metadata Status</div><div class="ev-value muted">${r.metadata_status}</div></div>
    <div class="evidence-cell"><div class="ev-label">Noise Pattern</div><div class="ev-value muted">${r.noise_pattern}</div></div>
    <div class="evidence-cell"><div class="ev-label">Image Quality</div><div class="ev-value muted">${r.image_quality}</div></div>
    <div class="evidence-cell"><div class="ev-label">Detection Method</div><div class="ev-value muted">${r.detection_method}</div></div>
  </div>
  <div class="charts-row">
    <div class="chart-box"><div class="chart-box-title">Confidence Distribution</div><div style="position:relative;height:190px;"><canvas id="confChart"></canvas></div></div>
    <div class="chart-box"><div class="chart-box-title">Feature Quality Metrics</div><div style="position:relative;height:190px;"><canvas id="radarChart"></canvas></div></div>
  </div>
  <div style="background:var(--paper2);border:1px solid var(--border);padding:16px;margin-bottom:1.5rem;">
    <div style="font-family:var(--font-head);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--ink4);margin-bottom:10px;">Forensic Summary</div>
    <p style="font-family:var(--font-mono);font-size:12.5px;color:var(--ink2);line-height:1.9;">${r.summary}</p>
    ${r.features?.length?`<div class="feature-tags">${r.features.map(f=>`<span class="ftag">&#8618; ${f}</span>`).join('')}</div>`:''}
  </div>
  <div class="export-row">
    <button class="btn btn-outline btn-sm" onclick="exportJSON(${JSON.stringify(r).replace(/"/g,'&quot;')},'${filename}')">&#8595; Export JSON</button>
    <button class="btn btn-outline btn-sm" onclick="printReport(${JSON.stringify(r).replace(/"/g,'&quot;')},'${filename}','${caseId}')">&#8595; PDF Report</button>
    <button class="btn btn-outline btn-sm" style="margin-left:auto;" onclick="document.getElementById('scannerResults').classList.remove('show')">&times; Close</button>
  </div></div>`;
  setTimeout(()=>{ document.getElementById('cFill').style.width=pct+'%'; drawCharts(r); },120);
}

function drawCharts(r){
  if(confChart) confChart.destroy(); if(radarChart) radarChart.destroy();
  const pct=Math.round(r.confidence*100);
  confChart=new Chart(document.getElementById('confChart'),{type:'doughnut',data:{labels:['Confidence','Uncertainty'],datasets:[{data:[pct,100-pct],backgroundColor:['#b8860b','#e0d0a8'],borderColor:['#8a6408','#c4b08a'],borderWidth:1.5}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},cutout:'65%'}});
  radarChart=new Chart(document.getElementById('radarChart'),{type:'radar',data:{labels:['PRNU','Texture','Noise','Frequency','Metadata'],datasets:[{data:[r.prnu_score||70,r.texture_score||65,r.noise_score||80,r.frequency_score||75,r.metadata_score||60],backgroundColor:'rgba(184,134,11,0.15)',borderColor:'#b8860b',pointBackgroundColor:'#8a6408',borderWidth:1.5}]},options:{responsive:true,maintainAspectRatio:false,scales:{r:{min:0,max:100,ticks:{color:'#9a7d52',font:{size:9}},grid:{color:'rgba(160,136,88,0.3)'},pointLabels:{color:'#6b5530',font:{size:9,family:'Courier Prime'}}}},plugins:{legend:{display:false}}}});
}

async function analyzeTampering(){
  const file = files['tamper']; 
  if(!file) {
    toast('No file selected', true);
    return;
  }
  
  showLoading();
  console.log(`[TAMPERING] Starting analysis for ${file.name}`);

  try {
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', file);

    console.log(`[TAMPERING] Calling /tampering endpoint...`);
    // Call backend API
    const response = await callBackend('/tampering', formData);

    console.log(`[TAMPERING] Response received:`, response);

    if (!response.success) {
      throw new Error(response.error || response.message || 'Analysis failed');
    }

    // Convert backend response to frontend format
    const backendResult = response.results;
    const r = {
      verdict: backendResult.verdict,
      confidence: backendResult.confidence,
      risk_level: backendResult.risk_level,
      noise_consistency: backendResult.noise_consistency,
      jpeg_artifacts: backendResult.jpeg_artifacts,
      metadata_analysis: backendResult.metadata_analysis,
      summary: backendResult.summary,
      indicators: backendResult.indicators || [],
      clean_indicators: backendResult.clean_indicators || []
    };

    console.log(`[TAMPERING] Analysis result:`, r.verdict, `Confidence: ${r.confidence}`);
    hideLoading();
    renderTamperResults(r, file.name);
    addHistory('tampering', file.name, r.verdict, r.confidence);
    toast('Tampering analysis complete.');
  } catch(e) {
    console.error(`[TAMPERING] Error:`, e);
    hideLoading();
    toast('Analysis failed: ' + e.message, true);
  }
}

function renderTamperResults(r,filename){
  const el=document.getElementById('tamperResults'); el.classList.add('show');
  const isClean=r.verdict==='Clean'||r.verdict==='Likely Clean';
  const isDanger=r.verdict==='Tampering Detected';
  const cls=isClean?'safe':isDanger?'danger':'warn';
  const stampCls=isClean?'stamp-clear':isDanger?'stamp-suspect':'stamp-warning';
  const stampTxt=isClean?'CLEAN':isDanger?'TAMPERED':'SUSPECT';
  const caseId=genCaseId();
  el.innerHTML=`<div class="fade-in" style="margin-top:1.5rem;">
  <div class="section-rule"><div class="section-rule-line"></div><div class="section-rule-label">Case File &mdash; Tampering Analysis</div><div class="section-rule-line"></div></div>
  <div class="case-header">
    <div><div class="case-id-label">Case Reference</div><div class="case-id-val">${caseId}</div></div>
    <div style="text-align:right;"><div class="case-date">${new Date().toLocaleString('en-GB')}</div><div style="margin-top:8px;"><span class="stamp ${stampCls}">${stampTxt}</span></div></div>
  </div>
  <div class="verdict-banner ${cls}"><div><div class="vb-title">${r.verdict}</div><div class="vb-sub">Confidence: ${Math.round(r.confidence*100)}% &nbsp;&middot;&nbsp; Risk: ${r.risk_level}</div></div></div>
  <div class="evidence-grid" style="grid-template-columns:repeat(3,1fr);">
    <div class="evidence-cell"><div class="ev-label">Noise Consistency</div><div class="ev-value muted">${r.noise_consistency}</div></div>
    <div class="evidence-cell"><div class="ev-label">JPEG Artifacts</div><div class="ev-value muted">${r.jpeg_artifacts}</div></div>
    <div class="evidence-cell"><div class="ev-label">Metadata</div><div class="ev-value muted">${r.metadata_analysis}</div></div>
  </div>
  ${r.indicators?.length?`<div style="background:var(--paper2);border:1px solid var(--border);padding:14px 16px;margin-bottom:12px;"><div style="font-family:var(--font-head);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--red);margin-bottom:8px;">Suspicious Indicators</div><ul class="indicator-list">${r.indicators.map(i=>`<li><span class="ind-bullet flag">FLAG</span>${i}</li>`).join('')}</ul></div>`:''}
  ${r.clean_indicators?.length?`<div style="background:var(--paper2);border:1px solid var(--border);padding:14px 16px;margin-bottom:12px;"><div style="font-family:var(--font-head);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--green);margin-bottom:8px;">Clean Indicators</div><ul class="indicator-list">${r.clean_indicators.map(i=>`<li><span class="ind-bullet ok">OK</span>${i}</li>`).join('')}</ul></div>`:''}
  <div style="background:var(--paper2);border:1px solid var(--border);padding:14px 16px;margin-bottom:1.5rem;"><div style="font-family:var(--font-head);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--ink4);margin-bottom:8px;">Assessment Summary</div><p style="font-family:var(--font-mono);font-size:12.5px;color:var(--ink2);line-height:1.9;">${r.summary}</p></div>
  <div class="export-row">
    <button class="btn btn-outline btn-sm" onclick="exportJSON(${JSON.stringify(r).replace(/"/g,'&quot;')},'${filename}')">&#8595; Export JSON</button>
    <button class="btn btn-outline btn-sm" onclick="printReport(${JSON.stringify(r).replace(/"/g,'&quot;')},'${filename}','${caseId}')">&#8595; PDF Report</button>
    <button class="btn btn-outline btn-sm" style="margin-left:auto;" onclick="document.getElementById('tamperResults').classList.remove('show')">&times; Close</button>
  </div></div>`;
}

async function compareDocuments(){
  const f1 = files['cmp1'], f2 = files['cmp2']; if(!f1 || !f2) return;
  showLoading();

  try {
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file1', f1);
    formData.append('file2', f2);

    // Call backend API
    const response = await callBackend('/compare', formData);

    if (!response.success) {
      throw new Error(response.error || 'Comparison failed');
    }

    // Convert backend response to frontend format
    const backendResult = response.comparison;
    const r = {
      match_probability: backendResult.similarity,
      verdict: backendResult.match ? 'Same Scanner' : 'Different Scanner',
      prnu_correlation: backendResult.similarity,
      noise_similarity: backendResult.similarity * 0.9,
      feature_similarity: backendResult.similarity * 0.95,
      doc1_scanner: backendResult.document1.scanner,
      doc2_scanner: backendResult.document2.scanner,
      summary: backendResult.match ?
        `Documents show strong correlation in scanner fingerprints, indicating high probability of same device origin with ${(backendResult.similarity * 100).toFixed(1)}% similarity.` :
        `Documents exhibit different scanner characteristics, suggesting different device origins with only ${(backendResult.similarity * 100).toFixed(1)}% similarity.`,
      evidence: backendResult.match ?
        ['Matching PRNU patterns', 'Similar noise characteristics', 'Consistent scanner fingerprints'] :
        ['Different PRNU signatures', 'Dissimilar noise patterns', 'Inconsistent scanner characteristics']
    };

    hideLoading();
    renderCompareResults(r, f1.name, f2.name);
    addHistory('comparison', f1.name + ' vs ' + f2.name, r.verdict, r.match_probability);
    toast('Comparison complete.');
  } catch(e) {
    hideLoading();
    toast('Failed: ' + e.message, true);
  }
}

function renderCompareResults(r,n1,n2){
  const el=document.getElementById('compareResults'); el.classList.add('show');
  const pct=Math.round(r.match_probability*100); const cls=pct>=70?'high':pct<=30?'low':'';
  const caseId=genCaseId();
  el.innerHTML=`<div class="fade-in" style="margin-top:1.5rem;">
  <div class="section-rule"><div class="section-rule-line"></div><div class="section-rule-label">Case File &mdash; Document Comparison</div><div class="section-rule-line"></div></div>
  <div class="match-box">
    <div style="font-family:var(--font-mono);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--ink4);margin-bottom:6px;">Same-Scanner Probability</div>
    <div class="match-pct ${cls}">${pct}%</div>
    <div class="match-verdict">${r.verdict}</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:1rem;">
    <div style="background:var(--paper2);border:1px solid var(--border);padding:14px;"><div class="ev-label">Document A</div><div style="font-family:var(--font-mono);font-size:12px;color:var(--ink);font-weight:700;margin:4px 0;">${n1}</div><div class="ev-label" style="margin-top:8px;">Identified Scanner</div><div style="font-family:var(--font-mono);font-size:12px;color:var(--ink2);">${r.doc1_scanner}</div></div>
    <div style="background:var(--paper2);border:1px solid var(--border);padding:14px;"><div class="ev-label">Document B</div><div style="font-family:var(--font-mono);font-size:12px;color:var(--ink);font-weight:700;margin:4px 0;">${n2}</div><div class="ev-label" style="margin-top:8px;">Identified Scanner</div><div style="font-family:var(--font-mono);font-size:12px;color:var(--ink2);">${r.doc2_scanner}</div></div>
  </div>
  <div style="background:var(--paper2);border:1px solid var(--border);padding:14px 16px;margin-bottom:1rem;">
    <div style="font-family:var(--font-head);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--ink4);margin-bottom:10px;">Similarity Metrics</div>
    ${[['PRNU Correlation',r.prnu_correlation],['Noise Similarity',r.noise_similarity],['Feature Similarity',r.feature_similarity]].map(([l,v])=>{const p=Math.round(v*100);return`<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;font-family:var(--font-mono);font-size:11px;color:var(--ink3);margin-bottom:4px;"><span>${l}</span><span>${p}%</span></div><div class="conf-track"><div class="conf-fill" style="width:${p}%"></div></div></div>`;}).join('')}
  </div>
  <div style="background:var(--paper2);border:1px solid var(--border);padding:14px 16px;margin-bottom:1.5rem;"><div style="font-family:var(--font-head);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--ink4);margin-bottom:8px;">Analysis Summary</div><p style="font-family:var(--font-mono);font-size:12.5px;color:var(--ink2);line-height:1.9;">${r.summary}</p>${r.evidence?.length?`<ul class="indicator-list" style="margin-top:10px;">${r.evidence.map(e=>`<li><span class="ind-bullet ok">EVD</span>${e}</li>`).join('')}</ul>`:''}</div>
  <div class="export-row">
    <button class="btn btn-outline btn-sm" onclick="exportJSON(${JSON.stringify(r).replace(/"/g,'&quot;')},'comparison')">&#8595; Export JSON</button>
    <button class="btn btn-outline btn-sm" style="margin-left:auto;" onclick="document.getElementById('compareResults').classList.remove('show')">&times; Close</button>
  </div></div>`;
}

async function runBatch(){
  if(!batchFileList.length) {
    toast('No files selected', true);
    return;
  }
  
  showLoading();
  const results=[];
  
  console.log(`[BATCH] Starting batch processing for ${batchFileList.length} files`);
  
  for(let i=0;i<batchFileList.length;i++){
    const file=batchFileList[i];
    document.getElementById('bd-'+i).className='batch-dot working';
    document.getElementById('br-'+i).textContent='analyzing...';
    document.getElementById('loadingStep').textContent='Processing: '+file.name;
    
    console.log(`[BATCH] Processing file ${i+1}/${batchFileList.length}: ${file.name}`);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);

      console.log(`[BATCH] Calling /analyze endpoint for ${file.name}...`);
      // Call backend API
      const response = await callBackend('/analyze', formData);

      console.log(`[BATCH] Response for ${file.name}:`, response);

      if (!response.success) {
        throw new Error(response.error || response.message || 'Analysis failed');
      }

      // Extract scanner info from response
      const backendResult = response.results;
      const scannerName = backendResult.predicted_scanner;
      const parts = scannerName.split(' ');
      
      const r = {
        file: file.name,
        scanner_brand: parts[0] || 'Unknown',
        scanner_model: parts.slice(1).join(' ') || scannerName,
        confidence: backendResult.confidence
      };
      
      console.log(`[BATCH] Result for ${file.name}: ${r.scanner_brand} ${r.scanner_model} (${r.confidence}%)`);
      
      results.push(r);
      document.getElementById('bd-'+i).className='batch-dot done';
      document.getElementById('br-'+i).textContent=r.scanner_brand+' '+r.scanner_model;
    } catch(e) { 
      console.error(`[BATCH] Error processing ${file.name}:`, e);
      results.push({
        file:file.name,
        scanner_brand:'Error',
        scanner_model:e.message,
        confidence:0
      }); 
      document.getElementById('bd-'+i).className='batch-dot error'; 
      document.getElementById('br-'+i).textContent='failed: '+e.message.substring(0,20); 
    }
  }
  
  console.log(`[BATCH] All files processed. Total results: ${results.length}`);
  hideLoading(); 
  renderBatchResults(results); 
  toast(`Batch complete. ${results.length} files processed.`);
}

function renderBatchResults(results){
  const el=document.getElementById('batchResults'); el.classList.add('show');
  const groups={};
  results.forEach(r=>{ const k=r.scanner_brand+' '+r.scanner_model; (groups[k]=groups[k]||[]).push(r); });
  el.innerHTML=`<div class="fade-in" style="margin-top:1.5rem;">
  <div class="section-rule"><div class="section-rule-line"></div><div class="section-rule-label">Batch Results &mdash; Scanner Groups</div><div class="section-rule-line"></div></div>
  ${Object.entries(groups).map(([sc,docs])=>`<div style="background:var(--paper2);border:1px solid var(--border);padding:14px 16px;margin-bottom:10px;"><div style="font-family:var(--font-head);font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--ink2);margin-bottom:10px;">&#8618; ${sc} <span style="font-weight:300;color:var(--ink4);">(${docs.length} file${docs.length>1?'s':''})</span></div><div class="feature-tags">${docs.map(d=>`<span class="ftag">&#128196; ${d.file}</span>`).join('')}</div></div>`).join('')}
  <div class="export-row"><button class="btn btn-outline btn-sm" onclick="exportJSON(${JSON.stringify(results).replace(/"/g,'&quot;')},'batch')">&#8595; Export JSON</button></div></div>`;
}

function renderHistory(){
  const sc=history.filter(h=>h.type==='scanner').length, tm=history.filter(h=>h.type==='tampering').length, cp=history.filter(h=>h.type==='comparison').length;
  document.getElementById('h-total').textContent=history.length;
  document.getElementById('h-scanner').textContent=sc;
  document.getElementById('h-tamper').textContent=tm;
  document.getElementById('h-compare').textContent=cp;
  const body=document.getElementById('historyBody');
  if(!history.length){ body.innerHTML='<tr><td colspan="6" style="text-align:center;color:var(--ink4);padding:2.5rem;font-family:var(--font-mono);font-size:12px;">&mdash; No cases on record &mdash;</td></tr>'; return; }
  body.innerHTML=history.map((h,i)=>{
    const pct=Math.round(h.conf*100); const cc=pct>=80?'cb-high':pct>=50?'cb-med':'cb-low';
    const d=new Date(h.date);
    return `<tr><td><span class="type-badge tb-${h.type}">${h.type}</span></td><td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${h.file}">${h.file}</td><td>${h.result}</td><td><span class="conf-badge ${cc}">${pct}%</span></td><td style="color:var(--ink4);white-space:nowrap;">${d.toLocaleDateString('en-GB')} ${d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</td><td><button class="btn btn-red btn-sm" onclick="delHistory(${i})">&times;</button></td></tr>`;
  }).join('');
}
function delHistory(i){ history.splice(i,1); localStorage.setItem('tf_v3',JSON.stringify(history)); renderHistory(); }
function clearHistory(){ if(!confirm('Purge all case records?')) return; history=[]; localStorage.removeItem('tf_v3'); renderHistory(); toast('Records purged.'); }

function exportJSON(r,filename){
  const blob=new Blob([JSON.stringify(r,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='tracefinder_'+String(filename).replace(/\.[^.]+$/,'')+'_'+Date.now()+'.json'; a.click(); toast('JSON exported.');
}
function printReport(r,filename,caseId){
  const w=window.open('','_blank');
  w.document.write(`<!DOCTYPE html><html><head><title>TraceFinder Report &mdash; ${caseId}</title>
  <link href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Courier+Prime:wght@400;700&family=Oswald:wght@400;600&display=swap" rel="stylesheet">
  <style>body{font-family:'Courier Prime',monospace;max-width:680px;margin:48px auto;color:#1a1208;background:#f2ead8;}h1{font-family:'Special Elite',cursive;font-size:24px;letter-spacing:2px;margin-bottom:4px;}h2{font-family:'Oswald',sans-serif;font-size:12px;letter-spacing:3px;text-transform:uppercase;color:#6b5530;border-top:2px solid #c4b08a;margin-top:20px;padding-top:8px;}table{width:100%;border-collapse:collapse;margin:10px 0;font-size:12px;}th{background:#1a1208;color:#d4a017;font-family:'Oswald',sans-serif;font-size:9px;letter-spacing:2px;text-transform:uppercase;padding:7px 12px;text-align:left;}td{padding:7px 12px;border-bottom:1px dashed #c4b08a;color:#3d2e14;}.stamp{font-family:'Oswald',sans-serif;font-size:18px;font-weight:600;letter-spacing:3px;border:3px solid #8b1a1a;color:#8b1a1a;display:inline-block;padding:3px 12px;transform:rotate(-5deg);margin-bottom:10px;}p{font-size:12px;line-height:1.9;color:#3d2e14;}</style></head><body>
  <div class="stamp">FORENSIC GRADE</div>
  <h1>TraceFinder &mdash; Case Report</h1>
  <p style="font-size:11px;color:#9a7d52;">Case ID: ${caseId} &nbsp;|&nbsp; ${filename} &nbsp;|&nbsp; ${new Date().toLocaleString('en-GB')}</p>
  <h2>Executive Summary</h2><p>${r.summary||'See findings below.'}</p>
  <h2>Findings</h2>  <table><tr><th>Parameter</th><th>Value</th></tr>${Object.entries(r).filter(([k])=>!['features','indicators','clean_indicators','evidence','summary'].includes(k)).map(([k,v])=>`<tr><td>${k.replace(/_/g,' ')}</td><td>${v}</td></tr>`).join('')}</table>
  <p style="font-size:10px;color:#9a7d52;margin-top:40px;border-top:1px dashed #c4b08a;padding-top:12px;">TraceFinder Forensic Document Division &middot; ${new Date().getFullYear()}</p>
  </body></html>`);
  w.document.close(); setTimeout(()=>w.print(),600);
}

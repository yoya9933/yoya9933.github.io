const SYNTHETIC_DATA_ONLY = true;
const seedAttendees = [
  ["DEMO-001","林沐晴","南岸科技大學","環境工程系","A-01","registered",true,true],
  ["DEMO-002","陳以安","海灣研究院","資料科學中心","A-02","registered",true,false],
  ["DEMO-003","黃書妍","島嶼設計學院","互動設計系","A-03","registered",false,false],
  ["DEMO-004","張承宇","城市工程中心","智慧系統組","A-04","registered",true,true],
  ["DEMO-005","許庭瑋","南岸科技大學","資訊工程系","A-05","registered",false,false],
  ["DEMO-006","吳芷寧","海灣研究院","海洋科技中心","A-06","registered",true,true],
  ["DEMO-007","李昀澤","島嶼設計學院","服務設計系","B-01","registered",true,false],
  ["DEMO-008","周品妤","城市工程中心","營運管理組","B-02","registered",false,false],
  ["DEMO-009","蔡子恆","南岸科技大學","水資源學程","B-03","registered",true,true],
  ["DEMO-010","鄭雨彤","海灣研究院","永續政策中心","B-04","registered",false,false],
  ["DEMO-011","何宇辰","島嶼設計學院","數位媒體系","B-05","registered",true,true],
  ["DEMO-012","沈佳恩","城市工程中心","資料治理組","B-06","registered",true,false],
  ["DEMO-013","宋柏勳","南岸科技大學","機械工程系","C-01","registered",false,false],
  ["DEMO-014","高語宸","海灣研究院","氣候風險中心","C-02","registered",true,true],
  ["DEMO-015","羅心妍","島嶼設計學院","產品設計系","C-03","registered",false,false],
  ["DEMO-016","彭睿哲","城市工程中心","場務規劃組","C-04","registered",true,true],
  ["DEMO-017","江采潔","南岸科技大學","工業管理系","C-05","registered",true,false],
  ["DEMO-018","葉冠廷","海灣研究院","AI 應用中心","C-06","registered",false,false],
  ["DEMO-019","簡若寧","島嶼設計學院","視覺傳達系","D-01","onsite",true,true],
  ["DEMO-020","方信宇","城市工程中心","系統維運組","D-02","onsite",true,false],
  ["DEMO-021","邱芮安","南岸科技大學","建築學系","D-03","registered",false,false],
  ["DEMO-022","曾品皓","海灣研究院","地理資訊中心","D-04","registered",true,true],
  ["DEMO-023","蘇婕寧","島嶼設計學院","創新管理系","D-05","registered",false,false],
  ["DEMO-024","梁浩軒","城市工程中心","專案管理組","D-06","onsite",true,true]
].map(([id,name,org,department,seat,source,checkedIn,seated])=>({id,name,org,department,seat,source,checkedIn,seated,checkInTime:checkedIn?new Date(Date.now()-Math.floor(Math.random()*55)*60000):null}));

let attendees = seedAttendees.map(item=>({...item}));
const $ = selector => document.querySelector(selector);
const escapeHtml = value => String(value).replace(/[&<>'"]/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[char]));
const formatTime = value => value ? new Intl.DateTimeFormat("zh-TW",{hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false}).format(value) : "—";

function organizations(){return ["全部機構",...new Set(attendees.map(item=>item.org))];}
function visibleAttendees(){
  const q=$("#search").value.trim().toLowerCase();
  const org=$("#orgFilter").value;
  const status=$("#statusFilter").value;
  const seated=$("#seatFilter").value;
  return attendees.filter(item=>{
    const hay=[item.id,item.name,item.org,item.department,item.seat].join(" ").toLowerCase();
    return (!q||hay.includes(q)) && (org==="全部機構"||item.org===org) && (status==="all"||(status==="checked"&&item.checkedIn)||(status==="waiting"&&!item.checkedIn)) && (seated==="all"||(seated==="seated"&&item.seated)||(seated==="not-seated"&&!item.seated));
  });
}

function renderStats(){
  const total=attendees.length;
  const checked=attendees.filter(x=>x.checkedIn).length;
  const seated=attendees.filter(x=>x.seated).length;
  const onsite=attendees.filter(x=>x.source==="onsite").length;
  $("#totalStat").textContent=total;
  $("#checkedStat").textContent=checked;
  $("#seatedStat").textContent=seated;
  $("#onsiteStat").textContent=onsite;
  $("#rateText").textContent=`${Math.round(checked/total*100)}% 已報到`;
}

function renderFilters(){
  const select=$("#orgFilter");
  const current=select.value||"全部機構";
  select.innerHTML=organizations().map(item=>`<option>${escapeHtml(item)}</option>`).join("");
  select.value=organizations().includes(current)?current:"全部機構";
}

function renderTokenOptions(){
  const select=$("#tokenSelect");
  const current=select.value;
  select.innerHTML=attendees.map(item=>`<option value="${item.id}">${item.id} · ${escapeHtml(item.name)}${item.checkedIn?"（已報到）":""}</option>`).join("");
  if(attendees.some(item=>item.id===current)) select.value=current;
}

function renderTable(){
  const list=visibleAttendees();
  $("#resultCount").textContent=`顯示 ${list.length} / ${attendees.length} 位`;
  const body=$("#attendeeBody");
  if(!list.length){body.innerHTML='<tr><td colspan="8" class="empty">沒有符合條件的虛構資料</td></tr>';return;}
  body.innerHTML=list.map(item=>`<tr>
    <td class="person"><strong>${escapeHtml(item.name)}</strong><span>${item.id}</span></td>
    <td>${escapeHtml(item.org)}</td><td>${escapeHtml(item.department)}</td><td>${escapeHtml(item.seat)}</td>
    <td><span class="pill ${item.source==="onsite"?"wait":"source"}">${item.source==="onsite"?"現場報名":"事前報名"}</span></td>
    <td><span class="pill ${item.checkedIn?"ok":"wait"}">${item.checkedIn?"已報到":"未報到"}</span></td>
    <td><span class="pill ${item.seated?"ok":"wait"}">${item.seated?"已入席":"未入席"}</span></td>
    <td>${formatTime(item.checkInTime)}</td></tr>`).join("");
}

function render(){renderStats();renderFilters();renderTokenOptions();renderTable();$("#updatedAt").textContent=`最後更新 ${formatTime(new Date())}`;}

function simulateScan(){
  const id=$("#tokenSelect").value;
  const item=attendees.find(person=>person.id===id);
  if(!item)return;
  if(item.checkedIn){$("#scanResult").innerHTML=`<strong>${escapeHtml(item.name)}</strong> 已完成報到，座位 ${escapeHtml(item.seat)}。`;return;}
  item.checkedIn=true;item.checkInTime=new Date();
  $("#scanResult").innerHTML=`<strong>報到成功：</strong>${escapeHtml(item.name)} · ${escapeHtml(item.org)} · 座位 ${escapeHtml(item.seat)}。<br><small>此變更只存在目前瀏覽器記憶體，重新整理後會重置。</small>`;
  render();
}

function resetDemo(){attendees=seedAttendees.map(item=>({...item}));$("#scanResult").textContent="示範資料已重置。選擇一組虛構 QR token 後即可模擬報到。";render();}

["#search","#orgFilter","#statusFilter","#seatFilter"].forEach(selector=>$(selector).addEventListener(selector==="#search"?"input":"change",renderTable));
$("#scanButton").addEventListener("click",simulateScan);
$("#resetButton").addEventListener("click",resetDemo);
render();
setInterval(()=>{$("#updatedAt").textContent=`最後更新 ${formatTime(new Date())} · 30 秒輪詢模擬`;},30000);

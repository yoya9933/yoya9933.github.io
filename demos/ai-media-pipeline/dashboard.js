const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];

const toast = $('#toast');
let toastTimer;
function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2400);
}

$$('.nav-item').forEach((button) => {
  button.addEventListener('click', () => {
    $$('.nav-item').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const target = document.getElementById(button.dataset.nav);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

const pauseButton = $('#pauseButton');
const systemState = $('#systemState');
let paused = false;
pauseButton.addEventListener('click', () => {
  paused = !paused;
  pauseButton.textContent = paused ? '恢復管線' : '暫停管線';
  systemState.textContent = paused ? '已暫停' : '自動運行中';
  showToast(paused ? 'Demo 管線已暫停。' : 'Demo 管線已恢復。');
});

$('#runButton').addEventListener('click', () => {
  if (paused) {
    showToast('目前為暫停狀態，請先恢復管線。');
    return;
  }

  const jobs = $('#jobsMetric');
  const content = $('#contentMetric');
  jobs.textContent = String(Number(jobs.textContent) + 1);
  content.textContent = String(Number(content.textContent) + 1);

  const row = document.createElement('tr');
  row.innerHTML = '<td>現在</td><td>手動觸發的示範任務</td><td>科技新知</td><td><span class="pill queued">生成中</span></td><td>YouTube</td><td>—</td>';
  $('#jobRows').prepend(row);
  showToast('已建立一筆新的 Demo 任務。');
});

function updateRecoveryCount() {
  const count = $$('[data-recover]').filter((button) => !button.disabled).length;
  $('#recoveryCount').textContent = String(count);
  $('#pendingMetric').textContent = String(count);
}

$$('[data-recover]').forEach((button) => {
  button.addEventListener('click', () => {
    if (button.disabled) return;
    button.disabled = true;
    button.textContent = '已恢復';
    button.closest('article').classList.add('recovered');
    updateRecoveryCount();
    showToast('已將任務移回發布佇列。');
  });
});

updateRecoveryCount();

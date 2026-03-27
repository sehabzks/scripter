// ── DOM Referansları ──
const resultText = document.getElementById('resultText');
const loadingOverlay = document.getElementById('loadingOverlay');
const copyBtn = document.getElementById('copyBtn');
const clearBtn = document.getElementById('clearBtn');
const downloadSrtBtn = document.getElementById('downloadSrtBtn');
const statsBar = document.getElementById('statsBar');
const statWords = document.getElementById('statWords');
const statChars = document.getElementById('statChars');
const statChunks = document.getElementById('statChunks');

// Sekme elemanları
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const youtubeBtn = document.getElementById('youtubeBtn');
const youtubeUrlInput = document.getElementById('youtubeUrl');
const filepathBtn = document.getElementById('filepathBtn');
const filepathInput = document.getElementById('filepathInput');
const fileDropText = document.getElementById('fileDropText');

// Son alınan chunk'ları tut (SRT için)
let lastChunks = [];
let lastFilename = 'transkripsiyon';

// Model seçimi (Whisper) backend üzerinde sabitlendiği için kaldırıldı.

// ── Sekme Geçişi ──
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => { c.style.display = 'none'; c.classList.remove('active'); });
        btn.classList.add('active');
        const targetId = btn.getAttribute('data-tab');
        const target = document.getElementById(targetId);
        if (target) {
            target.style.display = 'block';
            target.classList.add('active');
        }
    });
});


// ── Dosya seçilince label güncelle ──
filepathInput.addEventListener('change', () => {
    if (filepathInput.files.length > 0) {
        fileDropText.textContent = filepathInput.files[0].name;
        lastFilename = filepathInput.files[0].name.replace(/\.[^.]+$/, '');
    } else {
        fileDropText.textContent = 'Dosya Seçmek İçin Tıkla';
    }
});

// ── Event Listeners ──
document.addEventListener('DOMContentLoaded', () => {
    if (copyBtn) copyBtn.addEventListener('click', copyToClipboard);
    if (clearBtn) clearBtn.addEventListener('click', clearResult);
    if (youtubeBtn) youtubeBtn.addEventListener('click', processYouTube);
    if (filepathBtn) filepathBtn.addEventListener('click', processFilepath);
    if (downloadSrtBtn) downloadSrtBtn.addEventListener('click', downloadSrt);
    if (youtubeUrlInput) youtubeUrlInput.addEventListener('keydown', e => { if (e.key === 'Enter') processYouTube(); });
});
// MİKROFON FONKSİYONLARI KALDIRILDI



// ── YouTube ──
async function processYouTube() {
    console.log("YouTube işlemine başlandı...");
    const url = youtubeUrlInput.value.trim();
    if (!url) { alert("Lütfen geçerli bir YouTube URL'si girin."); return; }
    setLoading(true, 'Video indiriliyor ve işleniyor...');
    lastFilename = 'youtube_video';
    const fd = new FormData();
    fd.append('url', url);
    console.log("YouTube form verisi hazırlandı, fetch atılıyor.");
    await callTranscribe(fd);
}

// ── Dosya Seçimi ──
async function processFilepath() {
    console.log("Dosya işleme (Upload) başlandı...");
    if (!filepathInput.files || filepathInput.files.length === 0) {
        alert('Lütfen önce bir dosya seçin.'); return;
    }
    const file = filepathInput.files[0];
    lastFilename = file.name.replace(/\.[^.]+$/, '');
    setLoading(true, `"${file.name}" işleniyor...`);
    const fd = new FormData();
    fd.append('file', file, file.name);
    console.log("Dosya formData'ya eklendi, sunucuya fetch gönderiliyor.");
    await callTranscribe(fd);
}

// ── Ortak Transkripsiyon İsteği ──
async function callTranscribe(formData) {
    try {
        const res = await fetch('/transcribe', { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok) {
            resultText.value = data.text;
            lastChunks = data.chunks || [];
            updateStats(data.text, lastChunks);
            downloadSrtBtn.disabled = lastChunks.length === 0;
            // Kredi göstergesini dinamik olarak güncelle
            if (data.new_credits_seconds !== undefined) {
                updateCreditBadge(data.new_credits_seconds);
            }
        } else {
            resultText.value = 'Hata: ' + (data.error || 'Bilinmeyen hata');
            lastChunks = [];
            downloadSrtBtn.disabled = true;
        }
    } catch (err) {
        resultText.value = 'Sunucu bağlantı hatası!';
        lastChunks = [];
        downloadSrtBtn.disabled = true;
    } finally {
        setLoading(false);
    }
}

// ── Kredi Göstergesini Güncelle ──
function updateCreditBadge(seconds) {
    const badge = document.getElementById('creditBadge');
    const text = document.getElementById('creditText');
    if (!badge || !text) return;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (seconds <= 0) {
        text.textContent = 'Krediniz Bitti';
        badge.classList.add('danger');
    } else {
        text.textContent = `${mins} Dk ${secs} Sn Kredi`;
        badge.classList.remove('danger');
        // Kısa bir vurgu animasyonu ekle
        badge.style.transform = 'scale(1.08)';
        badge.style.transition = 'transform 0.3s ease';
        setTimeout(() => badge.style.transform = 'scale(1)', 400);
    }
}

// ── İstatistik Güncelle ──
function updateStats(text, chunks) {
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    statWords.innerHTML = `<i class="fa-solid fa-font"></i> ${words.toLocaleString('tr')} kelime`;
    statChars.innerHTML = `<i class="fa-solid fa-keyboard"></i> ${text.length.toLocaleString('tr')} karakter`;
    statChunks.innerHTML = `<i class="fa-solid fa-closed-captioning"></i> ${chunks.length} segment`;
    statsBar.style.display = words > 0 ? 'flex' : 'none';
}

// ── SRT Üretici & İndir ──
function formatSrtTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.round((seconds - Math.floor(seconds)) * 1000);
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')},${String(ms).padStart(3, '0')}`;
}

function generateSrt(chunks) {
    return chunks
        .filter(c => c.text && c.text.trim())
        .map((c, i) => `${i + 1}\n${formatSrtTime(c.start)} --> ${formatSrtTime(c.end)}\n${c.text.trim()}`)
        .join('\n\n') + '\n';
}

function downloadSrt() {
    if (!lastChunks.length) return;
    const srt = generateSrt(lastChunks);
    const blob = new Blob([srt], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${lastFilename}.srt`;
    a.click();
    URL.revokeObjectURL(url);
}

// ── Yardımcılar ──
function setLoading(active, msg = 'Dönüştürülüyor...') {
    loadingOverlay.querySelector('p').textContent = msg;
    loadingOverlay.classList.toggle('active', active);
}

function clearResult() {
    resultText.value = '';
    lastChunks = [];
    downloadSrtBtn.disabled = true;
    statsBar.style.display = 'none';
}

function copyToClipboard() {
    if (!resultText.value) return;
    navigator.clipboard.writeText(resultText.value).catch(() => {
        resultText.select();
        document.execCommand('copy');
    });
    const i = copyBtn.querySelector('i');
    i.className = 'fa-solid fa-check';
    setTimeout(() => i.className = 'fa-regular fa-copy', 2000);
}

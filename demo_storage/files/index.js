const uploadForm = {
  modal:     document.getElementById('modal'),
  openBtn:   document.getElementById('openUpload'),
  closeBtn:  document.getElementById('closeUpload'),
  backdrop:  document.getElementById('modalBackdrop'),
  dropZone:  document.getElementById('uploadArea'),
  fileInput: document.getElementById('fileInput'),
  fileInfo:  document.getElementById('fileInfo'),
  fileName:  document.getElementById('displayFileName'),
  fileSize:  document.getElementById('displayFileSize'),
  nameInput: document.getElementById('filename'),
  submitBtn: document.getElementById('uploadButton'),
  progress:  document.getElementById('progressBar'),
  fill:      document.getElementById('progressFill'),

  init() {
    this.openBtn.addEventListener('click', () => this.open());
    this.closeBtn.addEventListener('click', () => this.close());
    this.backdrop.addEventListener('click', () => this.close());
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') this.close(); });

    this.dropZone.addEventListener('click', () => {
      if (!this.dropZone.classList.contains('locked')) this.fileInput.click();
    });
    this.dropZone.addEventListener('dragover', (e) => {
      if (this.dropZone.classList.contains('locked')) return;
      e.preventDefault();
      this.dropZone.classList.add('dragover');
    });
    this.dropZone.addEventListener('dragleave', () => this.dropZone.classList.remove('dragover'));
    this.dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      this.dropZone.classList.remove('dragover');
      if (this.dropZone.classList.contains('locked')) return;
      const file = e.dataTransfer.files[0];
      if (file) {
        this.fileInput.files = e.dataTransfer.files;
        this.updateFileInfo();
      }
    });

    this.fileInput.addEventListener('change', () => this.updateFileInfo());
    this.submitBtn.addEventListener('click', () => this.upload());
  },

  open() {
    this.modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  },

  close() {
    this.modal.classList.add('hidden');
    document.body.style.overflow = '';
    this.dropZone.classList.remove('locked');
    this.fileInfo.classList.add('hidden');
    this.fileInput.value = '';
  },

  updateFileInfo() {
    const file = this.fileInput.files[0];
    if (!file) return;
    this.nameInput.value = file.name;
    this.fileName.textContent = file.name;
    this.fileSize.textContent = fmtSize(file.size);
    this.fileInfo.classList.remove('hidden');
    this.dropZone.classList.add('locked');
  },

  resetUI() {
    this.submitBtn.disabled = false;
    this.submitBtn.textContent = 'Upload';
    this.progress.classList.add('hidden');
    this.fill.style.width = '0';
  },

  upload() {
    const file = this.fileInput.files[0];
    if (!file) { notify('Please select a file', 'error'); return; }

    const name = this.nameInput.value.trim() || file.name;
    this.submitBtn.disabled = true;
    this.submitBtn.textContent = 'Uploading\u2026';
    this.progress.classList.remove('hidden');

    const xhr = new XMLHttpRequest();
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) this.fill.style.width = `${(e.loaded / e.total) * 100}%`;
    });
    xhr.onload = () => {
      this.resetUI();
      if (xhr.status < 300) {
        notify('File uploaded successfully', 'success');
        setTimeout(() => { this.close(); globalThis.location.reload(); }, 1200);
      } else {
        notify('Upload failed', 'error');
      }
    };
    xhr.onerror = () => {
      this.resetUI();
      notify('Network error', 'error');
    };
    xhr.open('PUT', new URL(encodeURIComponent(name), globalThis.location.href).href);
    xhr.send(file);
  },
};

const fileList = {
  tbody:   document.querySelector('tbody'),
  headers: document.querySelectorAll('thead th[data-col]'),
  sortCol: 'name',
  sortAsc: true,

  init() {
    this.headers.forEach(th => {
      th.addEventListener('click', () => {
        if (this.sortCol === th.dataset.col) {
          this.sortAsc = !this.sortAsc;
        } else {
          this.sortCol = th.dataset.col;
          this.sortAsc = true;
        }
        this.applySort();
      });
    });

    this.tbody.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-del');
      if (!btn) return;
      const name = btn.dataset.name;
      if (!globalThis.confirm(`Delete "${name}"?`)) return;
      fetch(new URL(encodeURIComponent(name), globalThis.location.href).href, { method: 'DELETE' })
        .then(r => {
          if (r.ok) {
            globalThis.location.reload();
          } else {
            notify('Delete failed', 'error');
          }
        })
        .catch(() => notify('Network error', 'error'));
    });
  },

  applySort() {
    const rows = Array.from(this.tbody.querySelectorAll('tr:not(.empty)'));
    rows.sort((a, b) => {
      const va = a.dataset[this.sortCol], vb = b.dataset[this.sortCol];
      const cmp = this.sortCol === 'size' ? Number.parseInt(va, 10) - Number.parseInt(vb, 10) : va.localeCompare(vb);
      return this.sortAsc ? cmp : -cmp;
    });
    rows.forEach(r => this.tbody.appendChild(r));

    this.headers.forEach(th => {
      th.classList.toggle('sort-asc',  th.dataset.col === this.sortCol &&  this.sortAsc);
      th.classList.toggle('sort-desc', th.dataset.col === this.sortCol && !this.sortAsc);
    });
  },
};

uploadForm.init();
fileList.init();

function notify(msg, type) {
  const el = document.createElement('div');
  el.className = `notification ${type}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => {
    el.style.transition = 'opacity 0.35s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 360);
  }, 2600);
}

function fmtSize(n) {
  if (n >= 1024 * 1024) return `${(n / (1024 * 1024)).toFixed(1)} MB`;
  if (n >= 1024)        return `${(n / 1024).toFixed(1)} KB`;
  return `${n} B`;
}

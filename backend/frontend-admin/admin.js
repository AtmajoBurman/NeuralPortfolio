/**
 * admin.js
 * Modular Admin Logic for Portfolio Admin Portal
 */

const API_BASE_URL = '';

// ------------------------------------------------------------------
// 0. Utilities & UI Elements
// ------------------------------------------------------------------

function showToast(message, type = 'success') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('fadeOut');
    toast.addEventListener('animationend', () => {
      toast.remove();
    });
  }, 3000);
}

function initSidebarToggle() {
  const hamburger = document.getElementById('adminHamburger');
  const sidebar = document.getElementById('adminSidebar');

  if (hamburger && sidebar) {
    hamburger.addEventListener('click', (e) => {
      e.stopPropagation();
      if (window.innerWidth <= 768) {
        sidebar.classList.toggle('open');
      } else {
        document.body.classList.toggle('sidebar-collapsed');
      }
    });

    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 768 && !sidebar.contains(e.target) && !hamburger.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }
}

function formatProjectDates(startStr, endStr) {
  if (!startStr) return '';
  const options = { month: 'short', year: 'numeric' };
  const parseParts = (dateStr) => {
    const parts = dateStr.split('-');
    return new Date(parts[0], parts[1] - 1, parts[2] || 1);
  };
  const startDate = parseParts(startStr);
  const startFormatted = startDate.toLocaleString('en-US', options);
  if (!endStr) return `${startFormatted} — Present`;
  const endDate = parseParts(endStr);
  const endFormatted = endDate.toLocaleString('en-US', options);
  return `${startFormatted} — ${endFormatted}`;
}

// ------------------------------------------------------------------
// 1. Core Error Handling & Fetch Wrapper
// ------------------------------------------------------------------
async function adminFetch(endpoint, options = {}) {
  const fetchOptions = {
    ...options,
    credentials: 'include',
  };

  if (!fetchOptions.headers) {
    fetchOptions.headers = {};
  }

  if (!(fetchOptions.body instanceof FormData)) {
    fetchOptions.headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, fetchOptions);
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        window.location.href = '/login';
        return;
      }
      let errorMsg = 'Server Error';
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorMsg;
      } catch (e) {
        errorMsg = response.statusText || 'Unknown Error';
      }
      throw new Error(errorMsg);
    }

    if (response.status === 204) return null;
    return await response.json();
  } catch (error) {
    throw error;
  }
}

function showError(containerId, message) {
  const container = document.getElementById(containerId);
  if (container) {
    container.textContent = message;
    container.style.display = 'block';
  } else {
    showToast(message, 'error');
  }
}

function clearError(containerId) {
  const container = document.getElementById(containerId);
  if (container) {
    container.textContent = '';
    container.style.display = 'none';
  }
}

// ------------------------------------------------------------------
// 2. Character Limit Live Tracking
// ------------------------------------------------------------------
function initCharacterCounters() {
  const inputs = document.querySelectorAll('input[maxlength], textarea[maxlength]');
  inputs.forEach(input => {
    const counterSpan = input.parentElement.querySelector('.char-counter span');
    if (counterSpan && !input.dataset.counterInitialized) {
      input.dataset.counterInitialized = 'true';
      counterSpan.textContent = input.value.length;
      input.addEventListener('input', () => {
        counterSpan.textContent = input.value.length;
      });
    }
  });
}

// ------------------------------------------------------------------
// 3. Dynamic Modal Factory
// ------------------------------------------------------------------
class ModalManager {
  static createModal(id, title, formFieldsHTML, onSubmit) {
    const existing = document.getElementById(id);
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = id;

    overlay.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">${title}</h2>
          <button type="button" class="modal-close" aria-label="Close modal">&times;</button>
        </div>
        <div class="modal-body">
          <div id="${id}-error" class="error-message" style="display: none;"></div>
          <form id="${id}-form">
            ${formFieldsHTML}
            <button type="submit" class="btn-primary" style="width: 100%; margin-top: 1rem;">Save Changes</button>
          </form>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    const closeBtn = overlay.querySelector('.modal-close');
    const form = overlay.querySelector('form');

    closeBtn.addEventListener('click', () => {
      overlay.classList.remove('active');
    });

    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('active');
      }
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearError(`${id}-error`);

      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());

      Object.keys(data).forEach(key => {
        if (data[key] === '') data[key] = null;
      });

      try {
        const btn = form.querySelector('button[type="submit"]');
        const prevText = btn.textContent;
        btn.textContent = 'Saving...';
        btn.disabled = true;

        await onSubmit(data);

        btn.textContent = prevText;
        btn.disabled = false;

        overlay.classList.remove('active');
        form.reset();
        showToast('Saved successfully!', 'success');
      } catch (err) {
        form.querySelector('button[type="submit"]').textContent = 'Save Changes';
        form.querySelector('button[type="submit"]').disabled = false;
        showError(`${id}-error`, err.message);
      }
    });

    initCharacterCounters();
    return overlay;
  }

  static showModal(id, data = null) {
    const overlay = document.getElementById(id);
    if (!overlay) return;
    clearError(`${id}-error`);
    const form = overlay.querySelector('form');
    form.reset();

    if (data) {
      Object.keys(data).forEach(key => {
        const input = form.elements[key];
        if (input && data[key] !== null) {
          input.value = data[key];
          input.dispatchEvent(new Event('input'));
        }
      });
      form.dataset.editId = data.id || '1';
    } else {
      delete form.dataset.editId;
    }

    overlay.classList.add('active');
  }
}

// ------------------------------------------------------------------
// 4. Admin Modules
// ------------------------------------------------------------------

const AdminStudentDetails = {
  containerId: 'admin-student-container',
  modalId: 'studentModal',

  async init() {
    const btn = document.getElementById('editStudentBtn');
    if (!btn || !document.getElementById(this.containerId)) return;

    const fields = `
      <div class="form-group">
        <label class="form-label">Name *</label>
        <input type="text" name="name" class="form-input" required maxlength="100">
        <div class="char-counter"><span>0</span>/100</div>
      </div>
      <div class="form-group">
        <label class="form-label">Bio / Professional Summary *</label>
        <textarea name="bio" class="form-textarea" required maxlength="2000"></textarea>
        <div class="char-counter"><span>0</span>/2000</div>
      </div>
      <div class="form-group">
        <label class="form-label">Gmail *</label>
        <input type="email" name="gmail" class="form-input" required maxlength="100">
        <div class="char-counter"><span>0</span>/100</div>
      </div>
      <div class="form-group">
        <label class="form-label">Profile Picture Link</label>
        <input type="url" name="profile_pic" class="form-input" maxlength="255">
        <div class="char-counter"><span>0</span>/255</div>
      </div>
    `;

    ModalManager.createModal(this.modalId, 'Edit Student Details', fields, this.save.bind(this));

    btn.addEventListener('click', () => {
      if (this.currentData) {
        ModalManager.showModal(this.modalId, this.currentData);
      }
    });
    this.render();
  },

  async render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;
    try {
      container.innerHTML = `
        <div class="admin-card">
           <div class="skeleton skeleton-title"></div>
           <div class="skeleton skeleton-text"></div>
           <div class="skeleton skeleton-text short"></div>
        </div>
      `;
      const data = await adminFetch('/api/student_details');
      this.currentData = data;
      container.innerHTML = `
        <div class="admin-card">
          <div class="card-header" style="border-bottom: none; margin-bottom: 0; padding-bottom: 0;">
            <div>
              <h3 class="card-title">${data.name}</h3>
              <p class="card-subtitle">${data.gmail}</p>
            </div>
          </div>
          <div class="card-body" style="margin-top: 1.5rem;">
            <p><strong>Bio:</strong><br>${data.bio}</p>
            <p style="margin-top: 1rem;"><a href="${data.profile_pic}" target="_blank" class="btn-link" style="padding: 0.4rem 1rem;">View Profile Picture</a></p>
          </div>
        </div>
      `;
    } catch (err) {
      container.innerHTML = `<div class="error-message">Failed to load details: ${err.message}</div>`;
    }
  },

  async save(data) {
    await adminFetch('/api/student_details', {
      method: 'PUT',
      body: JSON.stringify(data)
    });
    this.render();
  }
};

const AdminProjects = {
  containerId: 'admin-projects-container',
  modalId: 'projectModal',

  async init() {
    const btn = document.getElementById('addProjectBtn');
    if (!btn || !document.getElementById(this.containerId)) return;

    const fields = `
      <div class="form-group">
        <label class="form-label">Project Name *</label>
        <input type="text" name="project_name" class="form-input" required maxlength="100">
        <div class="char-counter"><span>0</span>/100</div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Category *</label>
          <input type="text" name="project_category" class="form-input" required maxlength="50">
          <div class="char-counter"><span>0</span>/50</div>
        </div>
        <div class="form-group">
          <label class="form-label">Tech Stack *</label>
          <input type="text" name="tech_stack" class="form-input" required maxlength="200">
          <div class="char-counter"><span>0</span>/200</div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Start Date *</label>
          <input type="date" name="start_date" class="form-input" required>
        </div>
        <div class="form-group">
          <label class="form-label">End Date</label>
          <input type="date" name="end_date" class="form-input">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Description *</label>
        <textarea name="project_description" class="form-textarea" required maxlength="1000"></textarea>
        <div class="char-counter"><span>0</span>/1000</div>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Video Link</label><input type="url" name="video_link" class="form-input" maxlength="200"><div class="char-counter"><span>0</span>/200</div></div>
        <div class="form-group"><label class="form-label">GitHub Repo</label><input type="url" name="github_repo" class="form-input" maxlength="200"><div class="char-counter"><span>0</span>/200</div></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Live Demo</label><input type="url" name="deployed_link" class="form-input" maxlength="200"><div class="char-counter"><span>0</span>/200</div></div>
        <div class="form-group"><label class="form-label">LinkedIn Post</label><input type="url" name="linkedin_post" class="form-input" maxlength="200"><div class="char-counter"><span>0</span>/200</div></div>
      </div>
    `;

    ModalManager.createModal(this.modalId, 'Project Details', fields, this.save.bind(this));

    btn.addEventListener('click', () => ModalManager.showModal(this.modalId));
    this.render();
  },

  async render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;
    try {
      container.innerHTML = `
        <div class="admin-card"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-text"></div></div>
        <div class="admin-card"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-text"></div></div>
      `;
      const data = await adminFetch('/api/projects');
      container.innerHTML = '';

      if (data.length === 0) {
        container.innerHTML = '<p style="color: #94a3b8;">No projects found.</p>';
        return;
      }

      data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'admin-card';
        card.innerHTML = `
          <div class="card-header">
            <div>
              <h3 class="card-title">${item.project_name} <span style="font-size:0.8rem; background:rgba(59,130,246,0.2); padding:0.2rem 0.6rem; border-radius:12px; margin-left:0.5rem; color:#93c5fd;">${item.project_category}</span></h3>
              <p class="card-subtitle">${formatProjectDates(item.start_date, item.end_date)}</p>
            </div>
            <div class="card-actions">
              <button class="btn-action btn-move-up" title="Move Up">↑</button>
              <button class="btn-action btn-move-down" title="Move Down">↓</button>
              <button class="btn-action btn-edit">Edit</button>
              <button class="btn-action btn-delete">Delete</button>
            </div>
          </div>
          <div class="card-body">
            <p>${item.project_description}</p>
            <p style="font-size:0.85rem; color:#a855f7;">Tech Stack: ${item.tech_stack}</p>
          </div>
        `;

        card.querySelector('.btn-edit').addEventListener('click', () => ModalManager.showModal(this.modalId, item));
        card.querySelector('.btn-delete').addEventListener('click', () => this.delete(item.id));
        card.querySelector('.btn-move-up').addEventListener('click', () => this.moveItem(item.id, -1));
        card.querySelector('.btn-move-down').addEventListener('click', () => this.moveItem(item.id, 1));

        container.appendChild(card);
      });
    } catch (err) {
      container.innerHTML = `<div class="error-message">Error loading projects: ${err.message}</div>`;
    }
  },

  async save(data) {
    const form = document.getElementById(`${this.modalId}-form`);
    const id = form.dataset.editId;
    const method = id ? 'PUT' : 'POST';
    const endpoint = id ? `/api/projects/${id}` : `/api/projects`;

    await adminFetch(endpoint, {
      method,
      body: JSON.stringify(data)
    });
    this.render();
  },

  async delete(id) {
    if (confirm('Are you sure you want to delete this project?')) {
      try {
        await adminFetch(`/api/projects/${id}`, { method: 'DELETE' });
        showToast('Project deleted successfully');
        this.render();
      } catch (err) {
        showToast(`Failed to delete: ${err.message}`, 'error');
      }
    }
  },

  async moveItem(id, direction) {
    try {
      const data = await adminFetch('/api/projects');
      const index = data.findIndex(p => p.id === id);
      if (index === -1) return;

      const newIndex = index + direction;
      if (newIndex < 0 || newIndex >= data.length) return;

      const temp = data[index];
      data[index] = data[newIndex];
      data[newIndex] = temp;

      const itemIds = data.map(p => p.id);

      await adminFetch('/api/projects/reorder', {
        method: 'PUT',
        body: JSON.stringify({ item_ids: itemIds })
      });
      this.render();
    } catch (err) {
      showToast(`Failed to reorder: ${err.message}`, 'error');
    }
  }
};

const AdminAchievements = {
  containerId: 'admin-achievements-container',
  modalId: 'achievementModal',

  async init() {
    const btn = document.getElementById('addAchievementBtn');
    if (!btn || !document.getElementById(this.containerId)) return;

    const fields = `
      <div class="form-group">
        <label class="form-label">Achievement Name *</label>
        <input type="text" name="name" class="form-input" required maxlength="100">
        <div class="char-counter"><span>0</span>/100</div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Start Date *</label>
          <input type="date" name="start_date" class="form-input" required>
        </div>
        <div class="form-group">
          <label class="form-label">End Date</label>
          <input type="date" name="end_date" class="form-input">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Description *</label>
        <textarea name="description" class="form-textarea" required maxlength="1000"></textarea>
        <div class="char-counter"><span>0</span>/1000</div>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Score/Grade</label><input type="text" name="score_or_grade" class="form-input" maxlength="50"><div class="char-counter"><span>0</span>/50</div></div>
        <div class="form-group"><label class="form-label">Picture Link</label><input type="url" name="picture" class="form-input" maxlength="200"><div class="char-counter"><span>0</span>/200</div></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label class="form-label">Certificate Link</label><input type="url" name="view_certificate" class="form-input" maxlength="200"><div class="char-counter"><span>0</span>/200</div></div>
        <div class="form-group"><label class="form-label">LinkedIn Post</label><input type="url" name="linkedin_post" class="form-input" maxlength="200"><div class="char-counter"><span>0</span>/200</div></div>
      </div>
    `;

    ModalManager.createModal(this.modalId, 'Achievement Details', fields, this.save.bind(this));

    btn.addEventListener('click', () => ModalManager.showModal(this.modalId));
    this.render();
  },

  async render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;
    try {
      container.innerHTML = `
        <div class="admin-card"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-text"></div></div>
      `;
      const data = await adminFetch('/api/achievements');
      container.innerHTML = '';

      if (data.length === 0) {
        container.innerHTML = '<p style="color: #94a3b8;">No achievements found.</p>';
        return;
      }

      data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'admin-card';
        card.innerHTML = `
          <div class="card-header">
            <div>
              <h3 class="card-title">${item.name}</h3>
              <p class="card-subtitle">${formatProjectDates(item.start_date, item.end_date)} ${item.score_or_grade ? `| Score: ${item.score_or_grade}` : ''}</p>
            </div>
            <div class="card-actions">
              <button class="btn-action btn-move-up" title="Move Up">↑</button>
              <button class="btn-action btn-move-down" title="Move Down">↓</button>
              <button class="btn-action btn-edit">Edit</button>
              <button class="btn-action btn-delete">Delete</button>
            </div>
          </div>
          <div class="card-body">
            <p>${item.description}</p>
          </div>
        `;

        card.querySelector('.btn-edit').addEventListener('click', () => ModalManager.showModal(this.modalId, item));
        card.querySelector('.btn-delete').addEventListener('click', () => this.delete(item.id));
        card.querySelector('.btn-move-up').addEventListener('click', () => this.moveItem(item.id, -1));
        card.querySelector('.btn-move-down').addEventListener('click', () => this.moveItem(item.id, 1));

        container.appendChild(card);
      });
    } catch (err) {
      container.innerHTML = `<div class="error-message">Error loading achievements: ${err.message}</div>`;
    }
  },

  async save(data) {
    const form = document.getElementById(`${this.modalId}-form`);
    const id = form.dataset.editId;
    const method = id ? 'PUT' : 'POST';
    const endpoint = id ? `/api/achievements/${id}` : `/api/achievements`;

    await adminFetch(endpoint, {
      method,
      body: JSON.stringify(data)
    });
    this.render();
  },

  async delete(id) {
    if (confirm('Are you sure you want to delete this achievement?')) {
      try {
        await adminFetch(`/api/achievements/${id}`, { method: 'DELETE' });
        showToast('Achievement deleted successfully');
        this.render();
      } catch (err) {
        showToast(`Failed to delete: ${err.message}`, 'error');
      }
    }
  },

  async moveItem(id, direction) {
    try {
      const data = await adminFetch('/api/achievements');
      const index = data.findIndex(p => p.id === id);
      if (index === -1) return;

      const newIndex = index + direction;
      if (newIndex < 0 || newIndex >= data.length) return;

      const temp = data[index];
      data[index] = data[newIndex];
      data[newIndex] = temp;

      const itemIds = data.map(p => p.id);

      await adminFetch('/api/achievements/reorder', {
        method: 'PUT',
        body: JSON.stringify({ item_ids: itemIds })
      });
      this.render();
    } catch (err) {
      showToast(`Failed to reorder: ${err.message}`, 'error');
    }
  }
};

const AdminChitChat = {
  containerId: 'admin-chitchatFeed',
  modalId: 'chitchatModal',

  async init() {
    const btn = document.getElementById('addChitchatBtn');
    if (!btn || !document.getElementById(this.containerId)) return;

    const fields = `
      <div class="form-group">
        <label class="form-label">Description (Content) *</label>
        <textarea name="description" class="form-textarea" required maxlength="280"></textarea>
        <div class="char-counter"><span>0</span>/280</div>
      </div>
      <div class="form-group"><label class="form-label">Link</label><input type="url" name="link" class="form-input" maxlength="200"><div class="char-counter"><span>0</span>/200</div></div>
      <div class="form-group">
        <label class="form-label">Vanishing Date (Optional)</label>
        <input type="datetime-local" name="vanishing_date" class="form-input">
      </div>
    `;

    ModalManager.createModal(this.modalId, 'Chit Chat Details', fields, this.save.bind(this));

    btn.addEventListener('click', () => ModalManager.showModal(this.modalId));
    this.render();
  },

  async render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;
    try {
      container.innerHTML = `
        <div class="admin-card"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-text"></div></div>
      `;
      const data = await adminFetch('/api/chitchat');
      container.innerHTML = '';

      if (data.length === 0) {
        container.innerHTML = '<p style="color: #94a3b8;">No updates found.</p>';
        return;
      }

      data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'admin-card';

        let localVanishing = '';
        if (item.vanishing_date) {
          const tempD = new Date(item.vanishing_date);
          localVanishing = new Date(tempD.getTime() - tempD.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        }

        const editItem = { ...item, vanishing_date: localVanishing };

        card.innerHTML = `
          <div class="card-header">
            <div>
              <p class="card-subtitle" style="margin-top:0;">
                ${new Date(item.date_added).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                ${item.vanishing_date ? ` | Vanishes: ${new Date(item.vanishing_date).toLocaleString()}` : ''}
              </p>
            </div>
            <div class="card-actions">
              <button class="btn-action btn-edit">Edit</button>
              <button class="btn-action btn-delete">Delete</button>
            </div>
          </div>
          <div class="card-body">
            <p>${item.description}</p>
            ${item.link ? `<p style="margin-top: 1rem;"><a href="${item.link}" target="_blank" class="btn-link" style="padding: 0.4rem 1rem;">View Link</a></p>` : ''}
          </div>
        `;

        card.querySelector('.btn-edit').addEventListener('click', () => ModalManager.showModal(this.modalId, editItem));
        card.querySelector('.btn-delete').addEventListener('click', () => this.delete(item.id));

        container.appendChild(card);
      });
    } catch (err) {
      container.innerHTML = `<div class="error-message">Error loading updates: ${err.message}</div>`;
    }
  },

  async save(data) {
    const form = document.getElementById(`${this.modalId}-form`);
    const id = form.dataset.editId;
    const method = id ? 'PUT' : 'POST';
    const endpoint = id ? `/api/chitchat/${id}` : `/api/chitchat`;

    if (data.vanishing_date) {
      data.vanishing_date = new Date(data.vanishing_date).toISOString();
    }

    await adminFetch(endpoint, {
      method,
      body: JSON.stringify(data)
    });
    this.render();
  },

  async delete(id) {
    if (confirm('Are you sure you want to delete this post?')) {
      try {
        await adminFetch(`/api/chitchat/${id}`, { method: 'DELETE' });
        showToast('Post deleted successfully');
        this.render();
      } catch (err) {
        showToast(`Failed to delete: ${err.message}`, 'error');
      }
    }
  }
};

// ------------------------------------------------------------------
// 5. Update Password Logic
// ------------------------------------------------------------------
function initUpdatePassword() {
  const btn = document.getElementById('updatePasswordBtn');

  if (!btn) return;

  const fields = `
    <div class="form-group">
      <label class="form-label" for="newPassword">New Password</label>
      <input type="password" name="newPassword" class="form-input" required maxlength="50">
      <div class="char-counter"><span>0</span>/50</div>
    </div>
    <div class="form-group">
      <label class="form-label" for="confirmPassword">Confirm Password</label>
      <input type="password" name="confirmPassword" class="form-input" required maxlength="50">
      <div class="char-counter"><span>0</span>/50</div>
    </div>
  `;

  ModalManager.createModal('passwordModal', 'Update Password', fields, async (data) => {
    if (data.newPassword !== data.confirmPassword) {
      throw new Error("Passwords do not match. Please try again.");
    }

    await adminFetch('/update-password', {
      method: 'PUT',
      body: JSON.stringify({ new_password: data.newPassword })
    });
  });

  btn.addEventListener('click', () => {
    ModalManager.showModal('passwordModal');
  });
}

// ------------------------------------------------------------------
// 6. Smart Mode Toggle Logic
// ------------------------------------------------------------------
async function initSmartModeToggle() {
  const toggles = document.querySelectorAll('#smartModeToggle');
  if (!toggles.length) return;

  try {
    const data = await adminFetch('/api/chatbot/smart-mode');
    toggles.forEach(toggle => {
      toggle.checked = data.smart_mode;

      toggle.addEventListener('change', async (e) => {
        const newState = e.target.checked;
        // Sync all toggles if multiple exist on the page
        toggles.forEach(t => { if (t !== e.target) t.checked = newState; });

        try {
          await adminFetch('/api/chatbot/smart-mode', {
            method: 'POST',
            body: JSON.stringify({ smart_mode: newState })
          });
          showToast(`Smart Mode is now ${newState ? 'ON' : 'OFF'}`, 'success');
        } catch (err) {
          e.target.checked = !newState;
          toggles.forEach(t => { if (t !== e.target) t.checked = !newState; });
          showToast(`Failed to update Smart Mode: ${err.message}`, 'error');
        }
      });
    });
  } catch (err) {
    console.error('Failed to load Smart Mode state:', err);
  }
}

// Initialize on DOM Load
const AdminCGPA = {
  containerId: 'admin-cgpa-container',
  modalId: 'cgpaModal',
  currentData: null,

  async init() {
    const btn = document.getElementById('editCgpaBtn');
    if (!btn || !document.getElementById(this.containerId)) return;

    const fields = `
      <div class="form-group">
        <label class="form-label">CGPA (Out of 10) *</label>
        <input type="number" step="0.01" min="0" max="10" name="grade" class="form-input" required>
      </div>
    `;

    ModalManager.createModal(this.modalId, 'Update CGPA', fields, this.save.bind(this));

    btn.addEventListener('click', () => {
      ModalManager.showModal(this.modalId, this.currentData);
    });

    this.render();
  },

  async render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;
    try {
      const data = await adminFetch('/api/cgpa');
      this.currentData = data;
      container.innerHTML = `
        <div class="admin-card">
          <div class="card-body">
            <h3 style="font-size: 2rem; color: #60a5fa; margin: 0;">${data.grade.toFixed(2)}</h3>
            <p style="color: #94a3b8; margin: 0;">Overall CGPA</p>
          </div>
        </div>
      `;
    } catch (err) {
      container.innerHTML = `<div class="error-message">Error loading CGPA: ${err.message}</div>`;
    }
  },

  async save(data) {
    const method = 'PUT';
    data.grade = parseFloat(data.grade);
    await adminFetch('/api/cgpa', {
      method,
      body: JSON.stringify(data)
    });
    this.render();
  }
};

const AdminSGPA = {
  containerId: 'admin-sgpa-container',
  modalId: 'sgpaModal',

  async init() {
    const btn = document.getElementById('addSgpaBtn');
    if (!btn || !document.getElementById(this.containerId)) return;

    const fields = `
      <div class="form-group">
        <label class="form-label">Semester Name *</label>
        <input type="text" name="semester_name" class="form-input" required>
      </div>
      <div class="form-group">
        <label class="form-label">SGPA (Out of 10) *</label>
        <input type="number" step="0.01" min="0" max="10" name="grade" class="form-input" required>
      </div>
    `;

    ModalManager.createModal(this.modalId, 'SGPA Details', fields, this.save.bind(this));

    btn.addEventListener('click', () => ModalManager.showModal(this.modalId));
    this.render();
  },

  async render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;
    try {
      const data = await adminFetch('/api/sgpa');
      container.innerHTML = '';

      if (data.length === 0) {
        container.innerHTML = '<p style="color: #94a3b8;">No SGPA records found.</p>';
        return;
      }

      const grid = document.createElement('div');
      grid.style.display = 'grid';
      grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(200px, 1fr))';
      grid.style.gap = '1rem';

      data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'admin-card';
        card.innerHTML = `
          <div class="card-header" style="flex-direction: column; align-items: flex-start; gap: 0.5rem; border: none; padding-bottom: 0;">
            <h3 class="card-title">${item.semester_name}</h3>
            <h2 style="font-size: 1.5rem; color: #a855f7; margin: 0;">${item.grade.toFixed(2)}</h2>
          </div>
          <div class="card-actions" style="padding: 1rem; padding-top: 0;">
            <button class="btn-action btn-edit">Edit</button>
            <button class="btn-action btn-delete">Delete</button>
          </div>
        `;

        card.querySelector('.btn-edit').addEventListener('click', () => ModalManager.showModal(this.modalId, item));
        card.querySelector('.btn-delete').addEventListener('click', () => this.delete(item.id));

        grid.appendChild(card);
      });
      container.appendChild(grid);
    } catch (err) {
      container.innerHTML = `<div class="error-message">Error loading SGPA: ${err.message}</div>`;
    }
  },

  async save(data) {
    const form = document.getElementById(`${this.modalId}-form`);
    const id = form.dataset.editId;
    const method = id ? 'PUT' : 'POST';
    const endpoint = id ? `/api/sgpa/${id}` : `/api/sgpa`;

    data.grade = parseFloat(data.grade);

    await adminFetch(endpoint, {
      method,
      body: JSON.stringify(data)
    });
    this.render();
  },

  async delete(id) {
    if (confirm('Are you sure you want to delete this SGPA record?')) {
      await adminFetch(`/api/sgpa/${id}`, { method: 'DELETE' });
      this.render();
    }
  }
};

const AdminProfiles = {
  containerId: 'admin-profiles-container',
  modalId: 'profileModal',

  async init() {
    const btn = document.getElementById('addProfileBtn');
    if (!btn || !document.getElementById(this.containerId)) return;

    const fields = `
      <div class="form-group">
        <label class="form-label">Logo Google Drive Link *</label>
        <input type="text" name="logo" class="form-input" required>
      </div>
      <div class="form-group">
        <label class="form-label">Profile Link *</label>
        <input type="url" name="link" class="form-input" required>
      </div>
    `;

    ModalManager.createModal(this.modalId, 'Profile Details', fields, this.save.bind(this));

    btn.addEventListener('click', () => ModalManager.showModal(this.modalId));
    this.render();
  },

  async render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;
    try {
      const data = await adminFetch('/api/profiles');
      container.innerHTML = '';

      if (data.length === 0) {
        container.innerHTML = '<p style="color: #94a3b8; grid-column: 1 / -1;">No profiles found.</p>';
        return;
      }

      data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'admin-card';
        card.innerHTML = `
          <div class="card-body" style="display: flex; align-items: center; gap: 1rem;">
            <div style="flex-shrink: 0;">
              <img src="${item.logo}" alt="Profile Logo" style="width: 40px; height: 40px; object-fit: contain; border-radius: 4px; background: #fff; padding: 4px;">
            </div>
            <div style="flex-grow: 1; overflow: hidden;">
              <a href="${item.link}" target="_blank" class="btn-link" style="display: block; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${item.link}</a>
            </div>
          </div>
          <div class="card-actions" style="padding: 1rem; border-top: 1px solid #334155;">
            <button class="btn-action btn-edit">Edit</button>
            <button class="btn-action btn-delete">Delete</button>
          </div>
        `;

        card.querySelector('.btn-edit').addEventListener('click', () => ModalManager.showModal(this.modalId, item));
        card.querySelector('.btn-delete').addEventListener('click', () => this.delete(item.id));

        container.appendChild(card);
      });
    } catch (err) {
      container.innerHTML = `<div class="error-message" style="grid-column: 1 / -1;">Error loading profiles: ${err.message}</div>`;
    }
  },

  async save(data) {
    const form = document.getElementById(`${this.modalId}-form`);
    const id = form.dataset.editId;
    const method = id ? 'PUT' : 'POST';
    const endpoint = id ? `/api/profiles/${id}` : `/api/profiles`;

    await adminFetch(endpoint, {
      method,
      body: JSON.stringify(data)
    });
    this.render();
  },

  async delete(id) {
    if (confirm('Are you sure you want to delete this profile?')) {
      await adminFetch(`/api/profiles/${id}`, { method: 'DELETE' });
      this.render();
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  initSidebarToggle();
  initCharacterCounters();
  initUpdatePassword();
  initSmartModeToggle();

  AdminStudentDetails.init();
  AdminCGPA.init();
  AdminSGPA.init();
  AdminProfiles.init();

  AdminProjects.init();
  AdminAchievements.init();
  AdminChitChat.init();
});

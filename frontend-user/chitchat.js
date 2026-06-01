// Global API Base URL
const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// Format date cleanly
function formatTime(isoStr) {
  if (!isoStr) return '';
  // Add 'Z' if naive from DB to treat as UTC
  if (!isoStr.endsWith('Z') && !isoStr.includes('+')) {
    isoStr += 'Z';
  }
  const dateObj = new Date(isoStr);
  return dateObj.toLocaleString('en-US', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
}

// Fetch and render chitchats
async function fetchChitchatFeed() {
  const feedContainer = document.getElementById('chitchatFeed');
  if (!feedContainer) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/chitchat`);
    if (!res.ok) throw new Error('Failed to fetch feed');
    
    const posts = await res.json();
    feedContainer.innerHTML = '';

    if (posts.length === 0) {
      feedContainer.innerHTML = `
        <div style="text-align: center; color: #64748b; padding: 4rem 0;">
          <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">The board is quiet...</p>
          <p style="font-size: 0.95rem;">Be the first to post a thought or update above!</p>
        </div>
      `;
      return;
    }

    posts.forEach(post => {
      const card = document.createElement('div');
      card.className = 'chitchat-card';

      // Meta header (Added date + optional vanishing tag)
      let vanishingHtml = '';
      if (post.vanishing_date) {
        vanishingHtml = `
          <span class="chitchat-vanishing-tag">
            <svg style="width: 14px; height: 14px; fill: currentColor; vertical-align: middle; margin-right: 3px;" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
            </svg>
            Vanishing: ${formatTime(post.vanishing_date)}
          </span>
        `;
      }

      const formattedAdded = formatTime(post.date_added);

      card.innerHTML = `
        <div class="chitchat-meta">
          <div class="chitchat-time">
            <svg style="width: 14px; height: 14px; fill: currentColor;" viewBox="0 0 24 24">
              <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
            </svg>
            <span>${formattedAdded}</span>
          </div>
          ${vanishingHtml}
        </div>
        <div class="chitchat-desc">${post.description}</div>
      `;

      // Optional URL link
      if (post.link) {
        // Safe check for URL protocol
        let href = post.link;
        if (!href.startsWith('http://') && !href.startsWith('https://')) {
          href = 'https://' + href;
        }
        
        const linkBtn = document.createElement('a');
        linkBtn.href = href;
        linkBtn.target = '_blank';
        linkBtn.className = 'chitchat-link-btn';
        linkBtn.innerHTML = `
          <span>Visit attached link</span>
          <svg style="width: 14px; height: 14px; fill: currentColor;" viewBox="0 0 24 24">
            <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
          </svg>
        `;
        card.appendChild(linkBtn);
      }

      feedContainer.appendChild(card);
    });

  } catch (err) {
    console.error('Error loading feed:', err);
    feedContainer.innerHTML = `
      <div style="text-align: center; color: #f87171; padding: 3rem 0;">
        <p>Error loading updates. Make sure backend server is running.</p>
      </div>
    `;
  }
}



// Fetch student updated_at timestamp for footer
async function fetchFooterTimestamp() {
  const updatedAtEl = document.getElementById('updatedAtText');
  if (!updatedAtEl) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/student_details`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    
    if (data.updated_at) {
      let updatedDateStr = data.updated_at;
      if (!updatedDateStr.endsWith('Z') && !updatedDateStr.includes('+')) {
        updatedDateStr += 'Z';
      }
      const dateObj = new Date(updatedDateStr);
      const options = { 
        day: 'numeric', 
        month: 'short', 
        year: 'numeric',
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        hour12: true 
      };
      const formattedDate = dateObj.toLocaleString('en-US', options);
      updatedAtEl.textContent = `Updated at: ${formattedDate}`;
    }
  } catch (e) {
    console.error('Failed to update footer timestamp:', e);
  }
}

// Main Load
document.addEventListener('DOMContentLoaded', () => {
  fetchChitchatFeed();
  fetchFooterTimestamp();
});

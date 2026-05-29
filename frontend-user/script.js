// Global API Base URL
const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// Helper to convert Google Drive file links to thumbnail links using regex
function convertGoogleDriveLink(url) {
  if (!url) return '';
  // Match file share link: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
  const match = url.match(/https?:\/\/(?:drive|docs)\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)/i);
  if (match && match[1]) {
    return `https://drive.google.com/thumbnail?id=${match[1]}&sz=s800`;
  }
  // Match query parameter link: https://drive.google.com/open?id=FILE_ID
  const queryMatch = url.match(/[?&]id=([a-zA-Z0-9_-]+)/i);
  if (queryMatch && queryMatch[1] && url.includes('google.com')) {
    return `https://drive.google.com/thumbnail?id=${queryMatch[1]}&sz=s800`;
  }
  return url;
}

// Draw the semester-wise SGPA histogram with a horizontal CGPA line
function drawSGPAChart(sgpaData, cgpaVal) {
  const svg = document.getElementById('sgpaChart');
  if (!svg) return;

  // Clear existing content
  svg.innerHTML = '';

  // Setup gradient definition
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  defs.innerHTML = `
    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#c084fc" />
      <stop offset="100%" stop-color="#6366f1" />
    </linearGradient>
    <filter id="barShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#a855f7" flood-opacity="0.15"/>
    </filter>
  `;
  svg.appendChild(defs);

  // Fallback for empty data
  if (!sgpaData || sgpaData.length === 0) {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', '400');
    text.setAttribute('y', '175');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('class', 'chart-axis-text');
    text.setAttribute('font-size', '16');
    text.textContent = 'No academic records available. Seed data in the database.';
    svg.appendChild(text);
    return;
  }

  // Lexicographical sort by semester name (e.g. "Semester 1", "Semester 2")
  sgpaData.sort((a, b) => {
    return a.semester_name.localeCompare(b.semester_name);
  });

  const width = 800;
  const height = 350;
  const paddingLeft = 55;
  const paddingRight = 95;
  const paddingTop = 40;
  const paddingBottom = 50;

  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  // Draw Y-axis gridlines & labels (grades 0, 2, 4, 6, 8, 10)
  const gridGrades = [0, 2, 4, 6, 8, 10];
  gridGrades.forEach(g => {
    const yVal = height - paddingBottom - (g / 10) * chartHeight;

    // Gridline
    if (g > 0) {
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', paddingLeft);
      line.setAttribute('y1', yVal);
      line.setAttribute('x2', width - paddingRight);
      line.setAttribute('y2', yVal);
      line.setAttribute('class', 'chart-grid-line');
      svg.appendChild(line);
    }

    // Label
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', paddingLeft - 12);
    text.setAttribute('y', yVal + 4);
    text.setAttribute('text-anchor', 'end');
    text.setAttribute('class', 'chart-axis-text');
    text.textContent = g.toFixed(2);
    svg.appendChild(text);
  });

  // Draw X-axis baseline
  const baseline = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  baseline.setAttribute('x1', paddingLeft);
  baseline.setAttribute('y1', height - paddingBottom);
  baseline.setAttribute('x2', width - paddingRight);
  baseline.setAttribute('y2', height - paddingBottom);
  baseline.setAttribute('class', 'chart-axis-line');
  svg.appendChild(baseline);

  // Setup Tooltip Element
  let tooltip = document.querySelector('.chart-tooltip-el');
  if (!tooltip) {
    tooltip = document.createElement('div');
    tooltip.className = 'chart-tooltip-el';
    document.body.appendChild(tooltip);
  }

  // Draw Bars
  const numBars = sgpaData.length;
  const colWidth = chartWidth / numBars;
  const barWidth = colWidth * 0.55; // 55% of column width for bars

  sgpaData.forEach((item, index) => {
    const colX = paddingLeft + index * colWidth;
    const barX = colX + (colWidth - barWidth) / 2;
    const barHeight = (item.grade / 10) * chartHeight;
    const barY = height - paddingBottom - barHeight;

    // SVG Rect (bar)
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', barX);
    rect.setAttribute('y', barY);
    rect.setAttribute('width', barWidth);
    rect.setAttribute('height', barHeight);
    rect.setAttribute('rx', '6'); // round top corners
    rect.setAttribute('class', 'chart-bar');
    rect.setAttribute('fill', 'url(#barGradient)');
    rect.setAttribute('filter', 'url(#barShadow)');

    // Interactive Tooltip Events
    rect.addEventListener('mouseover', (e) => {
      tooltip.innerHTML = `<strong>${item.semester_name}</strong><br>SGPA: <strong>${item.grade.toFixed(2)}</strong>`;
      tooltip.style.opacity = '1';
    });

    rect.addEventListener('mousemove', (e) => {
      tooltip.style.left = e.pageX + 'px';
      tooltip.style.top = e.pageY + 'px';
    });

    rect.addEventListener('mouseout', () => {
      tooltip.style.opacity = '0';
    });

    svg.appendChild(rect);

    // Exact grade score above bar
    const scoreText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    scoreText.setAttribute('x', barX + barWidth / 2);
    scoreText.setAttribute('y', barY - 8);
    scoreText.setAttribute('text-anchor', 'middle');
    scoreText.setAttribute('class', 'chart-axis-text');
    scoreText.setAttribute('font-weight', '600');
    scoreText.setAttribute('fill', '#e2e8f0');
    scoreText.textContent = item.grade.toFixed(2);
    svg.appendChild(scoreText);

    // Semester Label on X-axis
    const labelText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    labelText.setAttribute('x', barX + barWidth / 2);
    labelText.setAttribute('y', height - paddingBottom + 25);
    labelText.setAttribute('text-anchor', 'middle');
    labelText.setAttribute('class', 'chart-axis-text');
    labelText.textContent = item.semester_name;
    svg.appendChild(labelText);
  });

  // Draw CGPA horizontal parallel line
  if (cgpaVal !== null && cgpaVal > 0) {
    const cgpaY = height - paddingBottom - (cgpaVal / 10) * chartHeight;

    const cgpaLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    cgpaLine.setAttribute('x1', paddingLeft);
    cgpaLine.setAttribute('y1', cgpaY);
    cgpaLine.setAttribute('x2', width - paddingRight);
    cgpaLine.setAttribute('y2', cgpaY);
    cgpaLine.setAttribute('class', 'cgpa-line');
    svg.appendChild(cgpaLine);

    const cgpaLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    cgpaLabel.setAttribute('x', width - paddingRight + 10);
    cgpaLabel.setAttribute('y', cgpaY + 4);
    cgpaLabel.setAttribute('class', 'cgpa-line-label');
    cgpaLabel.textContent = `CGPA Line: ${cgpaVal.toFixed(2)}`;
    svg.appendChild(cgpaLabel);
  }
}

// Fetch Candidate Details (Name, Bio, Profile Pic, Email, Updated_At date)
async function fetchStudentDetails() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/student_details`);
    if (!res.ok) throw new Error('Failed to fetch student details');
    const data = await res.json();

    // Populate name
    const nameEl = document.getElementById('candidateName');
    if (nameEl) nameEl.textContent = data.name;

    // Populate bio / summary
    const bioEl = document.getElementById('candidateBio');
    if (bioEl) {
      bioEl.innerHTML = '';
      const pTag = document.createElement('p');
      pTag.textContent = data.bio.replace(/\\n/g, ' ').replace(/\s+/g, ' ').trim();
      bioEl.appendChild(pTag);
    }

    // Populate email
    const emailLink = document.getElementById('candidateEmail');
    const emailText = document.getElementById('candidateEmailText');
    if (emailLink && emailText) {
      emailLink.href = `mailto:${data.gmail}`;
      emailText.textContent = data.gmail;
    }

    // Populate profile pic with Google Drive link conversion
    const profileImg = document.getElementById('profilePic');
    if (profileImg) {
      profileImg.src = convertGoogleDriveLink(data.profile_pic);
      profileImg.onload = () => {
        profileImg.style.opacity = '1';
      };
    }

    // Populate updated at timestamp
    const updatedAtEl = document.getElementById('updatedAtText');
    if (updatedAtEl && data.updated_at) {
      // Parse ISO string cleanly. Add 'Z' if not present to treat as UTC, since it comes naive from DB
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

  } catch (err) {
    console.error('Error fetching student details:', err);
    const nameEl = document.getElementById('candidateName');
    if (nameEl) nameEl.textContent = 'Error Loading Portfolio';
  }
}

// Fetch CGPA and SGPA academic data
async function fetchAcademicData() {
  try {
    // 1. Fetch CGPA
    let cgpaVal = 0.00;
    try {
      const cgpaRes = await fetch(`${API_BASE_URL}/api/cgpa`);
      if (cgpaRes.ok) {
        const cgpaData = await cgpaRes.json();
        cgpaVal = cgpaData.grade;
        const cgpaValEl = document.getElementById('cgpaVal');
        if (cgpaValEl) cgpaValEl.textContent = cgpaVal.toFixed(2);
      }
    } catch (e) {
      console.error('Failed to load CGPA:', e);
    }

    // 2. Fetch SGPA
    const sgpaRes = await fetch(`${API_BASE_URL}/api/sgpa`);
    if (!sgpaRes.ok) throw new Error('Failed to fetch SGPA scores');
    const sgpaData = await sgpaRes.json();

    // Draw the chart
    drawSGPAChart(sgpaData, cgpaVal);

  } catch (err) {
    console.error('Error fetching academic scores:', err);
    drawSGPAChart([], 0.0);
  }
}

// Core Hamburger Menu Toggle Functionality
function initHamburger() {
  const hamburgerBtn = document.getElementById('hamburgerBtn');
  const navMenu = document.getElementById('navMenu');

  if (hamburgerBtn && navMenu) {
    hamburgerBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isExpanded = hamburgerBtn.getAttribute('aria-expanded') === 'true';
      hamburgerBtn.setAttribute('aria-expanded', !isExpanded);
      navMenu.classList.toggle('open');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (event) => {
      const isClickInsideNav = navMenu.contains(event.target);
      const isClickOnHamburger = hamburgerBtn.contains(event.target);

      if (!isClickInsideNav && !isClickOnHamburger && navMenu.classList.contains('open')) {
        navMenu.classList.remove('open');
        hamburgerBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
}

// Transform YouTube sharing links to embeddable links (with autoplay and mute)
function getYouTubeEmbedUrl(url) {
  if (!url) return '';
  let videoId = '';

  // 1. Match shortened URLs: https://youtu.be/VIDEO_ID
  const youtuBeMatch = url.match(/youtu\.be\/([a-zA-Z0-9_-]+)/i);
  if (youtuBeMatch && youtuBeMatch[1]) {
    videoId = youtuBeMatch[1];
  } else {
    // 2. Match standard watch URLs: v=VIDEO_ID
    const watchMatch = url.match(/[?&]v=([a-zA-Z0-9_-]+)/i);
    if (watchMatch && watchMatch[1]) {
      videoId = watchMatch[1];
    } else {
      // 3. Match shorts URLs: /shorts/VIDEO_ID
      const shortsMatch = url.match(/\/shorts\/([a-zA-Z0-9_-]+)/i);
      if (shortsMatch && shortsMatch[1]) {
        videoId = shortsMatch[1];
      } else {
        // 4. Match embed URLs: /embed/VIDEO_ID
        const embedMatch = url.match(/\/embed\/([a-zA-Z0-9_-]+)/i);
        if (embedMatch && embedMatch[1]) {
          videoId = embedMatch[1];
        }
      }
    }
  }

  if (videoId) {
    return `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`;
  }
  return url;
}

// Format start and end date ranges into Jan 1, 2026 - Present / Feb 1, 2026
function formatProjectDates(startStr, endStr) {
  if (!startStr) return '';
  const options = { day: 'numeric', month: 'short', year: 'numeric' };

  // Parse date strings in a timezone-safe manner (split to avoid local offset shift)
  const parseParts = (dateStr) => {
    const parts = dateStr.split('-');
    return new Date(parts[0], parts[1] - 1, parts[2] || 1);
  };

  const startDate = parseParts(startStr);
  const startFormatted = startDate.toLocaleString('en-US', options);

  if (!endStr) {
    return `${startFormatted} - Present`;
  }
  const endDate = parseParts(endStr);
  const endFormatted = endDate.toLocaleString('en-US', options);
  return `${startFormatted} - ${endFormatted}`;
}

// Fetch and dynamically render portfolio projects
async function fetchProjects() {
  const projectsContainer = document.getElementById('projects-container');
  if (!projectsContainer) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/projects`);
    if (!res.ok) throw new Error('Failed to fetch projects');

    const projects = await res.json();
    projectsContainer.innerHTML = '';

    if (projects.length === 0) {
      projectsContainer.innerHTML = `
        <div style="text-align: center; color: #64748b; padding: 4rem 0;">
          <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">No projects available.</p>
          <p style="font-size: 0.95rem;">Add some projects to the database to get started!</p>
        </div>
      `;
      return;
    }

    projects.forEach(project => {
      const card = document.createElement('div');
      card.className = 'project-card';

      const dateRange = formatProjectDates(project.start_date, project.end_date);

      // Video or Placeholder Card
      let videoHtml = '';
      if (project.video_link) {
        const embedUrl = getYouTubeEmbedUrl(project.video_link);
        videoHtml = `
          <div class="video-wrapper">
            <iframe width="420" height="345" class="project-video" src="${embedUrl}" title="${project.project_name} Video Demo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
          </div>
        `;
      } else {
        videoHtml = `
          <div class="video-wrapper">
            <div class="video-placeholder-card" title="Video walkthrough is pending upload.">
              <div class="placeholder-icon">
                <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
                  <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4zM14 16H5V8h9v8z"/>
                </svg>
              </div>
              <div class="placeholder-title">Demonstration Pending</div>
              <div class="placeholder-text">A video walkthrough is not currently available for this project. The creator may upload it in the future.</div>
            </div>
          </div>
        `;
      }

      // GitHub Repository Link or Placeholder
      let githubHtml = '';
      if (project.github_repo) {
        githubHtml = `<a href="${project.github_repo}" target="_blank" class="btn-link">GitHub</a>`;
      } else {
        githubHtml = `
          <span class="btn-link btn-placeholder" title="Source code is currently private or pending upload.">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="margin-right: 6px; vertical-align: middle;">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
            </svg>
            Code: Pending
          </span>
        `;
      }

      // Deployed Link or Placeholder
      let deployedHtml = '';
      if (project.deployed_link) {
        deployedHtml = `<a href="${project.deployed_link}" target="_blank" class="btn-link">Live Demo</a>`;
      } else {
        deployedHtml = `
          <span class="btn-link btn-placeholder" title="Live demonstration is not yet deployed for public access.">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="margin-right: 6px; vertical-align: middle;">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
            Demo: Pending
          </span>
        `;
      }

      // LinkedIn Post Link or Placeholder
      let linkedinHtml = '';
      if (project.linkedin_post) {
        linkedinHtml = `<a href="${project.linkedin_post}" target="_blank" class="btn-link">LinkedIn</a>`;
      } else {
        linkedinHtml = `
          <span class="btn-link btn-placeholder" title="No LinkedIn feature update has been published yet.">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="margin-right: 6px; vertical-align: middle;">
              <path d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM8 19H5V10h3v9zM6.5 8.7c-.97 0-1.75-.79-1.75-1.75S5.53 5.2 6.5 5.2s1.75.79 1.75 1.75-.78 1.75-1.75 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93-.89 0-1.52.61-1.52 1.93V19h-3V10h3v1.2c.43-.65 1.2-1.35 2.45-1.35 1.96 0 3.45 1.25 3.45 4.05V19z"/>
            </svg>
            LinkedIn: Pending
          </span>
        `;
      }

      card.innerHTML = `
        <div class="project-header">
          <div>
            <h3 class="project-title">${project.project_name}</h3>
            <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.3rem; font-weight: 500;">
              ${dateRange}
            </div>
          </div>
          <span class="project-category">${project.project_category}</span>
        </div>
        
        <div class="project-tech"><strong>Tech Stack:</strong> ${project.tech_stack}</div>
        
        <div class="project-body">
          ${videoHtml}
          <p class="project-desc">${project.project_description}</p>
        </div>
        
        <div class="project-links">
          ${githubHtml}
          ${deployedHtml}
          ${linkedinHtml}
        </div>
      `;

      projectsContainer.appendChild(card);
    });
  } catch (err) {
    console.error('Error loading projects:', err);
    projectsContainer.innerHTML = `
      <div style="text-align: center; color: #f87171; padding: 3rem 0;">
        <p>Error loading projects. Ensure backend server is running.</p>
      </div>
    `;
  }
}

// Fetch and dynamically render portfolio achievements
async function fetchAchievements() {
  const achievementsContainer = document.getElementById('achievements-container');
  if (!achievementsContainer) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/achievements`);
    if (!res.ok) throw new Error('Failed to fetch achievements');

    const achievements = await res.json();
    achievementsContainer.innerHTML = '';

    if (achievements.length === 0) {
      achievementsContainer.innerHTML = `
        <div style="text-align: center; color: #64748b; padding: 4rem 0;">
          <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">No achievements available.</p>
          <p style="font-size: 0.95rem;">Add some achievements to the database to get started!</p>
        </div>
      `;
      return;
    }

    achievements.forEach(ach => {
      const card = document.createElement('div');
      card.className = 'project-card';

      const dateRange = formatProjectDates(ach.start_date, ach.end_date);

      // Image or Placeholder Card
      let imageHtml = '';
      if (ach.picture) {
        const imageUrl = convertGoogleDriveLink(ach.picture);
        imageHtml = `
          <div class="video-wrapper">
            <img src="${imageUrl}" alt="${ach.name}" class="project-video" style="object-fit: cover; aspect-ratio: 16/9; display: block; border: none; width: 100%;">
          </div>
        `;
      } else {
        imageHtml = `
          <div class="video-wrapper">
            <div class="video-placeholder-card" title="Certification image pending upload.">
              <div class="placeholder-icon">
                <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
                  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 15l-4-4 1.41-1.41L10 13.17l5.59-5.59L17 9l-7 7z"/>
                </svg>
              </div>
              <div class="placeholder-title">Image Pending</div>
              <div class="placeholder-text">A certificate snapshot or achievement photo is not currently available.</div>
            </div>
          </div>
        `;
      }

      // View Certificate Button/Link or Placeholder
      let certificateHtml = '';
      if (ach.view_certificate) {
        certificateHtml = `<a href="${ach.view_certificate}" target="_blank" class="btn-link">View Certificate</a>`;
      } else {
        certificateHtml = `
          <span class="btn-link btn-placeholder" title="Certificate link is currently pending.">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="margin-right: 6px; vertical-align: middle;">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
            </svg>
            Certificate: Pending
          </span>
        `;
      }

      // LinkedIn Post Link or Placeholder
      let linkedinHtml = '';
      if (ach.linkedin_post) {
        linkedinHtml = `<a href="${ach.linkedin_post}" target="_blank" class="btn-link">LinkedIn</a>`;
      } else {
        linkedinHtml = `
          <span class="btn-link btn-placeholder" title="No LinkedIn update has been published yet.">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="margin-right: 6px; vertical-align: middle;">
              <path d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM8 19H5V10h3v9zM6.5 8.7c-.97 0-1.75-.79-1.75-1.75S5.53 5.2 6.5 5.2s1.75.79 1.75 1.75-.78 1.75-1.75 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93-.89 0-1.52.61-1.52 1.93V19h-3V10h3v1.2c.43-.65 1.2-1.35 2.45-1.35 1.96 0 3.45 1.25 3.45 4.05V19z"/>
            </svg>
            LinkedIn: Pending
          </span>
        `;
      }

      const categoryText = ach.score_or_grade ? ach.score_or_grade : 'Certificate';

      card.innerHTML = `
        <div class="project-header">
          <div>
            <h3 class="project-title">${ach.name}</h3>
            <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.3rem; font-weight: 500;">
              ${dateRange}
            </div>
          </div>
          <span class="project-category">${categoryText}</span>
        </div>
        
        <div class="project-body">
          ${imageHtml}
          <p class="project-desc">${ach.description}</p>
        </div>
        
        <div class="project-links">
          ${certificateHtml}
          ${linkedinHtml}
        </div>
      `;

      achievementsContainer.appendChild(card);
    });
  } catch (err) {
    console.error('Error loading achievements:', err);
    achievementsContainer.innerHTML = `
      <div style="text-align: center; color: #f87171; padding: 3rem 0;">
        <p>Error loading achievements. Ensure backend server is running.</p>
      </div>
    `;
  }
}

// Fetch and dynamically render profiles
async function fetchProfiles() {
  const profilesContainer = document.getElementById('profilesContainer');
  if (!profilesContainer) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/profiles`);
    if (!res.ok) throw new Error('Failed to fetch profiles');

    const profiles = await res.json();
    profilesContainer.innerHTML = '';

    if (profiles.length === 0) {
      profilesContainer.innerHTML = `
        <div style="text-align: center; color: #64748b; padding: 2rem 0; width: 100%;">
          <p>No profiles available.</p>
        </div>
      `;
      return;
    }

    profiles.forEach(profile => {
      const card = document.createElement('a');
      card.className = 'profile-card';
      card.href = profile.link;
      card.target = '_blank';
      card.rel = 'noopener noreferrer';

      const logoUrl = convertGoogleDriveLink(profile.logo);

      let platformName = 'Profile';
      try {
        const urlObj = new URL(profile.link);
        const hostname = urlObj.hostname.replace('www.', '');
        const parts = hostname.split('.');
        if (parts.length > 1) {
          platformName = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
        }
      } catch (e) { }

      card.innerHTML = `
        <div class="profile-icon">
          <img src="${logoUrl}" alt="Logo" style="width: 100%; height: 100%; object-fit: contain; border-radius: 8px;">
        </div>
        <div class="profile-info">
          <div class="profile-platform">${platformName}</div>
          <div class="profile-username" style="font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 180px;">View Profile</div>
        </div>
        <div class="profile-arrow">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/>
          </svg>
        </div>
      `;

      profilesContainer.appendChild(card);
    });

  } catch (err) {
    console.error('Error loading profiles:', err);
    profilesContainer.innerHTML = `
      <div style="text-align: center; color: #f87171; padding: 2rem 0; width: 100%;">
        <p>Error loading profiles. Ensure backend server is running.</p>
      </div>
    `;
  }
}

// On Page Load
document.addEventListener('DOMContentLoaded', () => {
  initHamburger();

  // Only execute index-specific fetches if on index page
  if (document.getElementById('candidateName')) {
    Promise.allSettled([
      fetchStudentDetails(),
      fetchAcademicData(),
      fetchProfiles()
    ]);
  }
  // Load projects dynamically if on projects page
  else if (document.getElementById('projects-container')) {
    fetchProjects();
  }
  // Load achievements dynamically if on achievements page
  else if (document.getElementById('achievements-container')) {
    fetchAchievements();
  }
});

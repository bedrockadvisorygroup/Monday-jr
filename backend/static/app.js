// app.js - Monday Jr SPA State & Logic V2

// Main Application State
const state = {
  leads: [],
  activeLead: null,
  painPoints: [],
  benchmarks: [],
  latestMagnet: null,
  slides: [],
  activeSlideIndex: 0,
  activeLitTab: 'lit-linkedin',
  activeLibSubTab: 'lib-benchmarks',
  projects: [], // Wednesday/Tuesday Jr converted projects
  activityLogs: [
    { type: 'system', text: 'Monday Jr Pre-Meeting Intelligence OS initialized successfully.' }
  ]
};

// DOM Elements & Hooks
document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

function initApp() {
  setupNavigation();
  setupModal();
  setupClipboard();
  setupSubTabs();
  setupQuickActions();
  
  // Initial API loads
  loadLeads();
  loadPainPoints();
  loadBenchmarks();
  loadKnowledgeItems();
  loadTuesdayProjects();
}

// 1. Sidebar SPA Navigation
function setupNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const panels = document.querySelectorAll('.view-panel');
  const pageTitle = document.getElementById('page-title');
  const pageSubheading = document.getElementById('page-subheading');

  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      
      const targetTab = item.getAttribute('data-tab');
      
      // Update sidebar active classes
      navItems.forEach(nav => nav.classList.remove('active'));
      item.classList.add('active');
      
      // Update viewport active panels
      panels.forEach(panel => panel.classList.remove('active'));
      const activePanel = document.getElementById(`view-${targetTab}`);
      if (activePanel) {
        activePanel.classList.add('active');
      }
      
      // Set Header Title & Subheading workflow tags
      pageTitle.textContent = item.textContent.trim();
      pageSubheading.textContent = `Monday Jr | ${item.textContent.trim()} Scoping Phase`;
      
      // Post-tab specific render updates
      if (targetTab === 'dashboard') {
        renderDashboardStats();
      } else if (targetTab === 'sales-pipeline') {
        renderPipelineBoard();
      } else if (targetTab === 'knowledge-library') {
        renderLibraryTables();
      } else if (targetTab === 'tuesday-handoff') {
        loadTuesdayProjects();
      }
    });
  });
}

// Quick action shortcuts routing inside Dashboard
function setupQuickActions() {
    const actions = {
      'btn-quick-finder': 'lead-finder',
      'btn-quick-profile': 'lead-profile',
      'btn-quick-magnet': 'magnet-studio',
      'btn-quick-ppt': 'ppt-builder',
      'btn-quick-discovery': 'discovery-prep',
      'btn-quick-handoff': 'tuesday-handoff'
    };

  Object.entries(actions).forEach(([btnId, tabId]) => {
    const el = document.getElementById(btnId);
    if (el) {
      el.addEventListener('click', () => {
        const navEl = document.getElementById(`nav-${tabId}`);
        if (navEl) navEl.click();
      });
    }
  });

  // Next action advice button
  const adviceBtn = document.getElementById('dash-btn-next-action');
  if (adviceBtn) {
    adviceBtn.addEventListener('click', () => {
      if (!state.activeLead) {
        document.getElementById('nav-lead-finder').click();
      } else {
        const status = state.activeLead.status;
        if (status === 'draft') {
          document.getElementById('nav-magnet-studio').click();
        } else if (status === 'needs_review') {
          document.getElementById('nav-ppt-builder').click();
        } else if (status === 'approved') {
          document.getElementById('nav-literature-builder').click();
        } else if (status === 'used_in_outreach') {
          document.getElementById('nav-discovery-prep').click();
        } else {
          document.getElementById('nav-tuesday-handoff').click();
        }
      }
    });
  }
}

// 2. Modals (Add Lead)
function setupModal() {
  const modal = document.getElementById('add-lead-modal');
  const btnOpen = document.getElementById('btn-add-lead-modal');
  const btnClose = document.getElementById('btn-close-lead-modal');
  const btnCancel = document.getElementById('btn-cancel-lead-modal');
  const form = document.getElementById('add-lead-form');

  btnOpen.addEventListener('click', () => modal.classList.add('active'));
  
  const closeModal = () => {
    modal.classList.remove('active');
    form.reset();
  };
  
  btnClose.addEventListener('click', closeModal);
  btnCancel.addEventListener('click', closeModal);
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const company = document.getElementById('company-name-input').value;
    const payload = {
      name: document.getElementById('lead-name-input').value,
      company_name: company,
      industry: document.getElementById('industry-select').value,
      stage: document.getElementById('stage-select').value,
      geography: document.getElementById('geography-input').value,
      website_url: document.getElementById('website-input').value || null
    };

    try {
      const response = await fetch('/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (response.ok) {
        const newLead = await response.json();
        logActivity('lead', `Added qualified startup target lead profile for ${company}.`);
        closeModal();
        loadLeads(() => {
          selectLead(newLead.id);
        });
      } else {
        alert('Error creating lead');
      }
    } catch (err) {
      console.error(err);
    }
  });
}

// 3. Sub-tabs Logic (Magnet Studio, Library, Literature)
function setupSubTabs() {
  // Studio Lead Magnet Subtabs
  const subTabs = document.querySelectorAll('.sub-tab[data-subtab]');
  subTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      subTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      const subPanelId = `subpanel-${tab.getAttribute('data-subtab')}`;
      document.querySelectorAll('.subtab-panel').forEach(p => p.classList.remove('active'));
      document.getElementById(subPanelId).classList.add('active');
    });
  });

  // Library Subtabs
  const libTabs = document.querySelectorAll('.sub-tab[data-libtab]');
  libTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      libTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      state.activeLibSubTab = tab.getAttribute('data-libtab');
      document.querySelectorAll('.lib-subpanel').forEach(p => p.classList.remove('active'));
      document.getElementById(`libpanel-${state.activeLibSubTab.replace('lib-', '')}`).classList.add('active');
    });
  });

  // Literature tabs
  const litTabs = document.querySelectorAll('.v-tab[data-lit]');
  litTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      litTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      state.activeLitTab = tab.getAttribute('data-lit');
      renderActiveLiteratureDraft();
    });
  });
}

// 4. Clipboard helper
function setupClipboard() {
  document.querySelectorAll('.btn-copy').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const element = document.getElementById(targetId);
      if (!element) return;
      
      let text = '';
      if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
        text = element.value;
      } else {
        text = element.textContent;
      }
      
      navigator.clipboard.writeText(text).then(() => {
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        btn.style.backgroundColor = 'var(--success)';
        setTimeout(() => {
          btn.textContent = originalText;
          btn.style.backgroundColor = '';
        }, 1500);
      });
    });
  });
}

// Helper: Logging activity in the UI
function logActivity(type, text) {
  state.activityLogs.unshift({
    type: type,
    text: text,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  });
  renderActivityLogs();
}

function renderActivityLogs() {
  const container = document.getElementById('dash-activity-logs');
  if (!container) return;
  
  container.innerHTML = '';
  state.activityLogs.slice(0, 5).forEach(log => {
    const item = document.createElement('div');
    item.className = 'timeline-item';
    item.innerHTML = `
      <span class="timeline-time">${log.time || 'NOW'} - ${log.type.toUpperCase()}</span>
      <p>${log.text}</p>
    `;
    container.appendChild(item);
  });
}

// 5. API Fetchers
async function loadLeads(callback) {
  try {
    const res = await fetch('/leads');
    if (res.ok) {
      state.leads = await res.json();
      renderLeadsTable();
      renderPipelineBoard();
      renderDashboardStats();
      if (callback) callback();
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadPainPoints() {
  try {
    const res = await fetch('/knowledge/pain-points');
    if (res.ok) {
      state.painPoints = await res.json();
      renderPainPointsCheckboxes();
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadBenchmarks() {
  try {
    const res = await fetch('/knowledge/benchmarks');
    if (res.ok) {
      state.benchmarks = await res.json();
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadKnowledgeItems() {
  try {
    const res = await fetch('/knowledge');
    if (res.ok) {
      renderKnowledgeItems(await res.json());
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadTuesdayProjects() {
  try {
    const res = await fetch('/projects');
    if (res.ok) {
      state.projects = await res.json();
      renderTuesdayHandoffs();
      renderDashboardStats();
    }
  } catch (err) {
    console.error(err);
  }
}

// 6. Renders & DOM Updates

// 6.1. Dashboard Statistics
function renderDashboardStats() {
  const total = state.leads.length;
  const qualified = state.leads.filter(l => l.status !== 'archived').length;
  const magnets = state.leads.filter(l => ['needs_review', 'approved', 'used_in_outreach', 'converted'].includes(l.status)).length;
  
  // Approximate based on items saved to knowledge repo
  const decks = state.leads.filter(l => ['approved', 'used_in_outreach', 'converted'].includes(l.status)).length;
  const handoffs = state.leads.filter(l => l.status === 'converted').length;
  
  // Set elements
  const elTotal = document.getElementById('stat-total-leads');
  const elQual = document.getElementById('stat-qualified-leads');
  const elMag = document.getElementById('stat-magnets-created');
  const elDeck = document.getElementById('stat-decks-created');
  const elHandoff = document.getElementById('stat-handoffs-created');
  
  if (elTotal) elTotal.textContent = total;
  if (elQual) elQual.textContent = qualified;
  if (elMag) elMag.textContent = magnets;
  if (elDeck) elDeck.textContent = decks;
  if (elHandoff) elHandoff.textContent = handoffs;

  // Render Dashboard active spotlight card
  renderDashboardSpotlight();
}

function renderDashboardSpotlight() {
  const companyEl = document.getElementById('dash-lead-company');
  const founderEl = document.getElementById('dash-lead-founder');
  const detailsRow = document.getElementById('dash-lead-details-row');
  const statusEl = document.getElementById('dash-lead-status');
  
  const recText = document.getElementById('dash-recommendation-text');
  const adviceBtn = document.getElementById('dash-btn-next-action');

  if (!state.activeLead) {
    companyEl.textContent = 'No Active Lead Selected';
    founderEl.textContent = 'Please choose a startup profile from the Lead Finder menu.';
    detailsRow.style.display = 'none';
    statusEl.style.display = 'none';
    
    recText.textContent = 'Select or create a target startup profile to activate pre-meeting qualification diagnostic workflows.';
    adviceBtn.textContent = 'Go to Lead Finder';
    return;
  }
  
  const lead = state.activeLead;
  companyEl.textContent = lead.company_name;
  founderEl.textContent = `Founder: ${lead.founder_name || 'N/A'} — ${lead.geography}`;
  statusEl.style.display = 'inline-block';
  statusEl.className = `badge ${lead.status}`;
  statusEl.textContent = lead.status.replace('_', ' ');
  updateReadinessMeter();

  // Calculate Opportunity Fit Score
  const score = calculateOpportunityScore(lead.stage);
  
  detailsRow.style.display = 'flex';
  document.getElementById('dash-lead-industry').textContent = lead.industry;
  document.getElementById('dash-lead-stage').textContent = lead.stage;
  document.getElementById('dash-lead-score').textContent = `${score}%`;

  // Update Recommended Action guidance dynamically
  if (lead.status === 'draft') {
    recText.textContent = `Opportunity identified for ${lead.company_name} in ${lead.industry}. Recommended Action: Launch Lead Magnet Studio to formulate diagnostic hypotheses and opening hooks.`;
    adviceBtn.textContent = 'Formulate Hypotheses';
  } else if (lead.status === 'needs_review') {
    recText.textContent = `Hypothesis generated for ${lead.company_name} (${score}% match). Recommended Action: Edit the 11-slide pre-meeting PPT outline and customize literature templates.`;
    adviceBtn.textContent = 'Edit Slide Deck';
  } else if (lead.status === 'approved') {
    recText.textContent = `Outreach collateral approved for ${lead.company_name}. Recommended Action: Copy connection drafts from the Literature Builder and send pitches to the founder.`;
    adviceBtn.textContent = 'Open Literature';
  } else if (lead.status === 'used_in_outreach') {
    recText.textContent = `Outreach sent. Discovery call scheduled? Recommended Action: Review custom agendas, load prep diagnostic questions, and execute Wednesday/Tuesday Jr handoff.`;
    adviceBtn.textContent = 'Discovery Call Prep';
  } else {
    recText.textContent = `Handoff complete. ${lead.company_name} is promoted to Wednesday/Tuesday active operational scoping project. Recommended Action: Browse handoff files in Tuesday cockpit.`;
    adviceBtn.textContent = 'Open Tuesday Jr Log';
  }
}

function calculateOpportunityScore(stage) {
  const scores = { 'Seed': 70, 'Series A': 85, 'Series B': 90, 'Bootstrapped': 75 };
  return scores[stage] || 80;
}

// 6.2. Lead Finder Table

// Update readiness meter based on current state
function updateReadinessMeter() {
  const steps = document.querySelectorAll('.readiness-steps .step');
  let completed = 0;
  steps.forEach(step => {
    const num = parseInt(step.dataset.step);
    let done = false;
    switch (num) {
      case 1:
        done = !!state.activeLead;
        break;
      case 2:
        // Assume public signal review when lead is selected
        done = !!state.activeLead;
        break;
      case 3:
        done = !!state.latestMagnet;
        break;
      case 4:
        done = !!state.latestMagnet && !!state.latestMagnet.ppt_outline;
        break;
      case 5:
        done = state.slides && state.slides.length > 0;
        break;
      case 6:
        done = state.activeLead && state.activeLead.status === 'converted';
        break;
    }
    if (done) {
      step.classList.add('completed');
      completed++;
    } else {
      step.classList.remove('completed');
    }
  });
  const fill = document.querySelector('.progress-fill');
  if (fill) {
    fill.style.width = `${(completed / 6) * 100}%`;
  }
}

function renderLeadsTable() {
  const tbody = document.getElementById('leads-table-body');
  tbody.innerHTML = '';
  
  if (state.leads.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 40px; color: var(--text-muted);">No qualified leads found. Click "+ New Lead" above to initialize a target profile!</td></tr>`;
    return;
  }
  
  state.leads.forEach(lead => {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    
    if (state.activeLead && state.activeLead.id === lead.id) {
      tr.style.backgroundColor = 'hsla(22, 90%, 52%, 0.08)';
    }

    tr.innerHTML = `
      <td><strong>${lead.name}</strong></td>
      <td>${lead.company_name}</td>
      <td>${lead.industry}</td>
      <td><span class="badge draft">${lead.stage}</span></td>
      <td>${lead.geography}</td>
      <td><span class="badge ${lead.status}">${lead.status.replace('_', ' ')}</span></td>
      <td>
        <button class="btn btn-secondary btn-sm btn-glow" onclick="event.stopPropagation(); selectLead(${lead.id})">Analyze Profile</button>
      </td>
    `;
    
    tr.addEventListener('click', () => {
      selectLead(lead.id);
      document.getElementById('nav-lead-profile').click();
    });
    tbody.appendChild(tr);
  });
}

// 6.3. Select and Load Lead Profile context
async function selectLead(leadId) {
  const lead = state.leads.find(l => l.id === leadId);
  if (!lead) return;
  
  state.activeLead = lead;
  
  // Update header badge status
  const badge = document.getElementById('active-lead-badge');
  badge.textContent = `Active Lead: ${lead.company_name}`;
  badge.classList.add('selected');
  
  // Update Dashboard spot
  renderDashboardSpotlight();

  // Populate Lead Profile View
  document.getElementById('profile-avatar').textContent = lead.company_name.substring(0, 1).toUpperCase();
  document.getElementById('profile-lead-name').textContent = lead.name;
  document.getElementById('profile-company-info').textContent = `${lead.company_name} — Qualified Pre-Meeting Corporate Profile`;
  
  const statusBadge = document.getElementById('profile-status-badge');
  statusBadge.className = `badge ${lead.status}`;
  statusBadge.textContent = lead.status.replace('_', ' ');

  document.getElementById('profile-industry').textContent = lead.industry;
  document.getElementById('profile-stage').textContent = lead.stage;
  document.getElementById('profile-geography').textContent = lead.geography;
  
  const websiteLink = document.getElementById('profile-website');
  if (lead.website_url) {
    websiteLink.textContent = lead.website_url;
    websiteLink.href = lead.website_url;
    websiteLink.style.display = 'inline-block';
  } else {
    websiteLink.textContent = 'N/A';
    websiteLink.removeAttribute('href');
  }

  // Radial score render
  const score = calculateOpportunityScore(lead.stage);
  const radialBar = document.querySelector('.gauge-radial-bar');
  const radialText = document.getElementById('gauge-score-value');
  const radialVerdict = document.getElementById('gauge-score-verdict');
  
  if (radialBar) {
    radialBar.style.setProperty('--gauge-percent', `${score}%`);
    radialText.textContent = `${score}%`;
    
    if (score >= 85) {
      radialVerdict.textContent = 'Premium Segment Target';
      radialVerdict.style.color = 'var(--primary)';
    } else {
      radialVerdict.textContent = 'Strong Expansion Upside';
      radialVerdict.style.color = 'var(--secondary)';
    }
  }

  // Pre-check checkboxes in Studio based on lead industry
  renderPainPointsCheckboxes(lead.industry);

  // Load latest magnet package if it exists
  await loadLeadMagnet(lead.id);
  
  // Refresh leads table to update highlight
  renderLeadsTable();
}

// 6.4. Fetch and Render Lead Magnet Package
async function loadLeadMagnet(leadId) {
  resetMagnetWorkspace();

  try {
    const res = await fetch(`/magnet/${leadId}`);
    if (res.ok) {
      const magnet = await res.json();
      state.latestMagnet = magnet;
      
      state.slides = JSON.parse(magnet.ppt_outline);
      state.activeSlideIndex = 0;
      
      renderMagnetOutputs();
      renderSlideDeckList();
      renderSlideCanvas();
      renderActiveLiteratureDraft();
      renderDiscoveryAgenda();
      // Update readiness meter after magnet generation
      updateReadinessMeter();
    }
  } catch (err) {
    state.latestMagnet = null;
    state.slides = [];
  }
}

function resetMagnetWorkspace() {
  document.getElementById('magnet-onepager-content').innerHTML = `<p class="placeholder-text">Click "Run Lead Magnet Engine" on the left to synthesize personalized marketing collateral.</p>`;
  document.getElementById('magnet-hook-content').textContent = 'Hook draft will generate here...';
  document.getElementById('magnet-offer-content').textContent = 'Suggested roadmap invitation will generate here...';
  
  document.getElementById('ppt-slides-list').innerHTML = '<p class="placeholder-text" style="padding:10px;">Select a qualified lead and generate a magnet outline.</p>';
  document.getElementById('slide-viewer-bullets').innerHTML = '';
  document.getElementById('active-lit-textarea').value = 'Draft will generate when a lead magnet is created.';
  document.getElementById('discovery-agenda-content').innerHTML = `<p class="placeholder-text">Please generate a lead magnet to configure the custom agenda brief.</p>`;
}

// Bind Generate Magnet engine trigger
const generateBtn = document.getElementById('btn-generate-magnet');
if (generateBtn) {
  generateBtn.addEventListener('click', async () => {
    if (!state.activeLead) {
      alert('Please select a lead first from the Lead Finder!');
      return;
    }
    
    const checkedPains = Array.from(document.querySelectorAll('input[name="pain_points"]:checked')).map(el => el.value);
    if (checkedPains.length === 0) {
      alert('Please select at least one problem hypothesis!');
      return;
    }
    
    generateBtn.textContent = 'Generating Collateral...';
    generateBtn.disabled = true;

    const payload = {
      lead_id: state.activeLead.id,
      selected_pain_points: checkedPains,
      custom_signals: document.getElementById('custom-signals-input').value
    };

    try {
      const res = await fetch('/magnet/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        logActivity('magnet', `Generated pre-meeting lead magnet overview deck for ${state.activeLead.company_name}.`);
        await selectLead(state.activeLead.id);
        await loadLeads();
        alert('Success! Lead magnet generated. templates and outlines updated.');
      } else {
        alert('Error generating lead magnet');
      }
    } catch (err) {
      console.error(err);
    } finally {
      generateBtn.textContent = 'Run Lead Magnet Engine';
      generateBtn.disabled = false;
    }
  });
}

// Render outputs
function renderMagnetOutputs() {
  if (!state.latestMagnet) return;
  
  const markdownText = parseSimpleMarkdown(state.latestMagnet.pre_meeting_one_pager);
  document.getElementById('magnet-onepager-content').innerHTML = markdownText;
  
  document.getElementById('magnet-hook-content').textContent = state.latestMagnet.opening_hook;
  document.getElementById('magnet-offer-content').textContent = state.latestMagnet.suggested_offer;
}

// Simple Custom Markdown Parser to keep SPA zero-dependency
function parseSimpleMarkdown(md) {
  let html = md;
  // Alerts blockquote formatting
  html = html.replace(/> \[\!NOTE\]\n(> .*\n?)*/g, (match) => {
    const cleanContent = match.replace(/> \[\!NOTE\]\n/, '').replace(/> /g, '');
    return `<div class="quote-text" style="background-color: hsla(199, 100%, 50%, 0.05); border-left: 4px solid var(--primary); padding: 12px; margin: 12px 0;"><strong>Hypothesis:</strong><br>${cleanContent}</div>`;
  });
  
  // Tables formatting
  html = html.replace(/\|(.+)\|/g, (match) => {
    if (match.includes('---')) return ''; // ignore dividers
    const cols = match.split('|').map(s => s.trim()).filter(s => s !== '');
    const isHeader = match.includes('Dimension') && match.includes('Industry Standard');
    const tag = isHeader ? 'th' : 'td';
    const row = cols.map(c => `<${tag}>${c}</${tag}>`).join('');
    return `<tr>${row}</tr>`;
  });
  
  // Wrap table rows inside real table tags
  html = html.replace(/(<tr>.*<\/tr>\s*)+/g, (match) => {
    return `<div class="table-responsive"><table class="table" style="margin: 16px 0;">${match}</table></div>`;
  });

  // H1, H2, H3
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  
  // Bold
  html = html.replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>');
  
  // List items
  html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\s*)+/g, '<ul>$&</ul>');

  return html;
}

// 6.5. Pre-Meeting PPT Outline Editor
function renderSlideDeckList() {
  const container = document.getElementById('ppt-slides-list');
  container.innerHTML = '';
  
  if (state.slides.length === 0) return;
  
  state.slides.forEach((slide, idx) => {
    const div = document.createElement('div');
    div.className = `slide-thumb ${idx === state.activeSlideIndex ? 'active' : ''}`;
    div.innerHTML = `
      <div class="slide-thumb-num">Slide ${slide.slide_number}</div>
      <div class="slide-thumb-title">${slide.title}</div>
    `;
    div.addEventListener('click', () => {
      saveCurrentSlideInMemory();
      
      state.activeSlideIndex = idx;
      renderSlideDeckList();
      renderSlideCanvas();
    });
    container.appendChild(div);
  });
}

function renderSlideCanvas() {
  const numLabel = document.getElementById('slide-viewer-number');
  const titleInput = document.getElementById('slide-viewer-title');
  const bulletsArea = document.getElementById('slide-viewer-bullets');
  
  bulletsArea.innerHTML = '';
  
  if (state.slides.length === 0) {
    numLabel.textContent = 'Slide -';
    titleInput.value = 'No slide outline selected';
    return;
  }
  
  const slide = state.slides[state.activeSlideIndex];
  numLabel.textContent = `Slide ${slide.slide_number} of ${state.slides.length}`;
  titleInput.value = slide.title;
  
  slide.content.forEach((bullet, idx) => {
    const div = document.createElement('div');
    div.className = 'slide-bullet-item';
    div.innerHTML = `
      <span class="bullet-dot">&bull;</span>
      <input type="text" class="form-control slide-bullet-input" value="${bullet}" data-idx="${idx}">
    `;
    bulletsArea.appendChild(div);
  });
}

function saveCurrentSlideInMemory() {
  if (state.slides.length === 0) return;
  
  const activeSlide = state.slides[state.activeSlideIndex];
  activeSlide.title = document.getElementById('slide-viewer-title').value;
  
  const bulletInputs = document.querySelectorAll('.slide-bullet-input');
  const bullets = [];
  bulletInputs.forEach(input => {
    bullets.push(input.value);
  });
  activeSlide.content = bullets;
}

// Bind Save changes locally
const savePptBtn = document.getElementById('btn-save-ppt-changes');
if (savePptBtn) {
  savePptBtn.addEventListener('click', () => {
    saveCurrentSlideInMemory();
    alert('Slide outline changes saved to local memory.');
    renderSlideDeckList();
  });
}

// Bind Save Deck to Knowledge Library
const saveLibPptBtn = document.getElementById('btn-save-ppt-knowledge');
if (saveLibPptBtn) {
  saveLibPptBtn.addEventListener('click', async () => {
    if (!state.activeLead || state.slides.length === 0) {
      alert('No active slide deck found to save!');
      return;
    }
    
    saveCurrentSlideInMemory();
    
    const payload = {
      title: `Pre-Meeting Deck: ${state.activeLead.company_name}`,
      source_agent: "monday_jr",
      category: "case_example",
      content: JSON.stringify(state.slides),
      reuse_permission: "reusable"
    };

    try {
      const res = await fetch('/knowledge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        logActivity('knowledge', `Saved pre-meeting presentation outline for ${state.activeLead.company_name} to knowledge repo.`);
        alert('Deck outline successfully added to Shared Knowledge Library!');
        loadKnowledgeItems();
      } else {
        alert('Error saving slide deck');
      }
    } catch (err) {
      console.error(err);
    }
  });
}

// 6.6. Literature tabs drafts
function renderActiveLiteratureDraft() {
  const textarea = document.getElementById('active-lit-textarea');
  const title = document.getElementById('active-lit-title');
  
  if (!state.latestMagnet) {
    textarea.value = 'Draft will generate when a lead magnet is created.';
    return;
  }
  
  const outreach = JSON.parse(state.latestMagnet.outreach_message);
  
  if (state.activeLitTab === 'lit-linkedin') {
    title.textContent = 'LinkedIn Connection Hook';
    textarea.value = outreach.linkedin;
  } else if (state.activeLitTab === 'lit-email') {
    title.textContent = 'Founder Cold Email';
    textarea.value = outreach.email;
  } else if (state.activeLitTab === 'lit-whatsapp') {
    title.textContent = 'WhatsApp Quick Pitch';
    textarea.value = outreach.whatsapp;
  }
}

// 6.7. Discovery Prep & Handoff
function renderDiscoveryAgenda() {
  if (!state.latestMagnet) return;
  const content = parseSimpleMarkdown(state.latestMagnet.discovery_agenda);
  document.getElementById('discovery-agenda-content').innerHTML = content;
}

// Handoff Trigger logic
const handoffBtn = document.getElementById('btn-trigger-handoff');
if (handoffBtn) {
  handoffBtn.addEventListener('click', async () => {
    if (!state.activeLead) {
      alert('Please select a lead first!');
      return;
    }
    
    if (state.activeLead.status === 'converted') {
      alert('This lead has already been handed off to Tuesday Jr!');
      return;
    }

    handoffBtn.textContent = 'Converting Lead...';
    handoffBtn.disabled = true;

    try {
      const res = await fetch(`/leads/${state.activeLead.id}/convert`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        logActivity('handoff', `Promoted ${state.activeLead.company_name} to active Client Project scoping.`);
        alert(`Success! Lead converted to project.\n- Folder path: ${data.project_folder_path}\n- Diagnostic brief created in client folder.\nTuesday Jr pipeline is now initialized as discovery_pending.`);
        // Update Tuesday Jr Handoff Status widget
        const handoffWidget = document.getElementById('widget-tuesday-handoff-status');
        if (handoffWidget) {
          handoffWidget.innerHTML = `<h3>Tuesday Jr Handoff Status</h3><p>Lead successfully handed off. Check Tuesday Jr Handoff list for details.</p>`;
        }
        await loadLeads();
        await loadTuesdayProjects();
        await selectLead(state.activeLead.id);
      } else {
        alert('Error triggering handoff');
      }
    } catch (err) {
      console.error(err);
    } finally {
      handoffBtn.textContent = 'Confirm Handoff to Tuesday Jr';
      handoffBtn.disabled = false;
    }
  });
}

// 6.8. Pipeline Kanban Board
function renderPipelineBoard() {
  const columns = ["draft", "needs_review", "approved", "used_in_outreach", "converted"];
  
  columns.forEach(col => {
    const container = document.getElementById(`cards-${col}`);
    const countBadge = document.getElementById(`count-${col}`);
    if (!container) return;
    
    container.innerHTML = '';
    const filteredLeads = state.leads.filter(l => l.status === col);
    countBadge.textContent = filteredLeads.length;
    
    if (filteredLeads.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--text-muted); font-size:11px; border: 1px dashed var(--border-glass); border-radius:8px">Column Empty</div>`;
      return;
    }
    
    filteredLeads.forEach(lead => {
      const card = document.createElement('div');
      card.className = 'pipeline-card';
      card.innerHTML = `
        <h4>${lead.company_name}</h4>
        <p>${lead.name} — ${lead.stage}</p>
        <div class="pipeline-card-footer">
          <span class="pipeline-card-stage">${lead.industry}</span>
          <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); changeCardStatus(${lead.id}, '${col}')">&rarr;</button>
        </div>
      `;
      card.addEventListener('click', () => {
        selectLead(lead.id);
        document.getElementById('nav-lead-profile').click();
      });
      container.appendChild(card);
    });
  });
}

// Status progress helper within pipeline board
async function changeCardStatus(leadId, currentStatus) {
  const pipelineFlow = ["draft", "needs_review", "approved", "used_in_outreach", "converted"];
  const curIdx = pipelineFlow.indexOf(currentStatus);
  if (curIdx === -1 || curIdx === pipelineFlow.length - 1) return;
  
  const nextStatus = pipelineFlow[curIdx + 1];
  
  if (nextStatus === 'converted') {
    selectLead(leadId);
    document.getElementById('nav-discovery-prep').click();
    setTimeout(() => {
      alert('Handoff requires discovery meeting details validation. Please review the Discovery Prep brief and click "Confirm Handoff" to finish!');
    }, 300);
    return;
  }

  try {
    const res = await fetch(`/leads/${leadId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: nextStatus })
    });
    if (res.ok) {
      const lead = state.leads.find(l => l.id === leadId);
      logActivity('pipeline', `Moved ${lead.company_name} pipeline status to ${nextStatus.replace('_', ' ')}.`);
      await loadLeads();
      if (state.activeLead && state.activeLead.id === leadId) {
        await selectLead(leadId);
      }
    }
  } catch (err) {
    console.error(err);
  }
}

// 6.9. Knowledge Library View Renders
function renderLibraryTables() {
  // 1. Render Benchmarks
  const benchmarksTbody = document.getElementById('lib-benchmarks-table-body');
  if (benchmarksTbody) {
    benchmarksTbody.innerHTML = '';
    if (state.benchmarks.length === 0) {
      benchmarksTbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">Loading benchmarks...</td></tr>`;
    } else {
      state.benchmarks.forEach(b => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${b.industry}</strong></td>
          <td>${b.dimension}</td>
          <td>${b.industry_standard}</td>
          <td><span class="text-link">${b.market_leader}</span></td>
          <td><small style="color:var(--text-muted)">${b.recommendation_playbook || 'N/A'}</small></td>
        `;
        benchmarksTbody.appendChild(tr);
      });
    }
  }

  // 2. Render Seeded Pain Categories
  const painsTbody = document.getElementById('lib-pains-table-body');
  if (painsTbody) {
    painsTbody.innerHTML = '';
    if (state.painPoints.length === 0) {
      painsTbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">Loading pain point presets...</td></tr>`;
    } else {
      state.painPoints.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${p.category}</strong></td>
          <td>${p.typical_signals || 'N/A'}</td>
          <td><small>${p.diagnostic_questions || 'N/A'}</small></td>
          <td><span class="badge approved">${p.bedrock_service_fit}</span></td>
        `;
        painsTbody.appendChild(tr);
      });
    }
  }
}

function renderKnowledgeItems(items) {
  const container = document.getElementById('lib-items-list-container');
  if (!container) return;
  
  container.innerHTML = '';
  const reusableDecks = items.filter(it => it.category === 'case_example');
  
  if (reusableDecks.length === 0) {
    container.innerHTML = `<p class="placeholder-text" style="grid-column: span 3; text-align:center; padding:40px;">No customized decks or plays saved to the library yet. Build a pre-meeting PPT outline and click "Save Slide Deck to Library" to create reusable templates!</p>`;
    return;
  }
  
  reusableDecks.forEach(item => {
    const card = document.createElement('div');
    card.className = 'lib-item-card';
    
    let slidesCount = 0;
    try {
      slidesCount = JSON.parse(item.content).length;
    } catch(e) {}

    card.innerHTML = `
      <div class="lib-item-header">
        <h4>${item.title}</h4>
        <span class="badge approved">reusable</span>
      </div>
      <div class="lib-item-body">
Category: Pre-Meeting Slide Deck Outline
Agent Source: ${item.source_agent}
Saved At: ${new Date(item.created_at).toLocaleDateString()}
Total slides: ${slidesCount} slides

Click to load slides to current PPT builder context.
      </div>
    `;
    card.style.cursor = 'pointer';
    card.addEventListener('click', () => {
      if (confirm(`Would you like to import this reusable deck outline (${item.title}) into the active PPT builder session?`)) {
        state.slides = JSON.parse(item.content);
        state.activeSlideIndex = 0;
        document.getElementById('nav-ppt-builder').click();
        renderSlideDeckList();
        renderSlideCanvas();
        alert('Deck outline imported to active workspace!');
      }
    });
    container.appendChild(card);
  });
}

// 6.10. Render Converted Tuesday Jr Handoff projects
function renderTuesdayHandoffs() {
  const tbody = document.getElementById('handoffs-list-tbody');
  if (!tbody) return;
  
  tbody.innerHTML = '';
  const handoffs = state.projects.filter(p => p.name.startsWith('Monday Jr Handoff:'));
  
  if (handoffs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--text-muted);">No projects promoted to Tuesday Jr yet. Qualify a lead and complete the Handoff to activate scoping logs!</td></tr>`;
    return;
  }
  
  handoffs.forEach(project => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${project.name.replace('Monday Jr Handoff: ', '')}</strong></td>
      <td>${project.client_name}</td>
      <td>${project.industry}</td>
      <td>${project.location}</td>
      <td><span class="badge converted">${project.status.replace('_', ' ')}</span></td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="alert('Scoping logs are active under Wednesday/Tuesday directories: clients/${safeProjectFolderName(project.name.replace('Monday Jr Handoff: ', \'\'))}/')">View Scoping logs</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function safeProjectFolderName(name) {
  return name.trim().toLowerCase().replace(/[\s\-]+/g, '_').replace(/[^a-z0-9_]+/g, '').replace(/_+/g, '_').trim('_');
}

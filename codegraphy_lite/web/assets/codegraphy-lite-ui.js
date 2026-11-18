/**
 * CodeGraphy Lite - Pro Features Enhancement & Upgrade Modal
 *
 * Surfaces PRO badges and an upgrade modal for proprietary features.
 * Design: Linear/Raycast developer-tool aesthetic -- no emojis, no gradients.
 */

(function () {
  'use strict';

  /* -- Lucide-style 16x16 inline SVG icons -- */
  const ICONS = {
    ast: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    blast: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/><line x1="4.93" y1="4.93" x2="7.05" y2="7.05"/><line x1="16.95" y1="16.95" x2="19.07" y2="19.07"/><line x1="4.93" y1="19.07" x2="7.05" y2="16.95"/><line x1="16.95" y1="7.05" x2="19.07" y2="4.93"/></svg>',
    inspector: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    mcp: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    pro: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    close: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    check: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    dash: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    arrow: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
  };

  const PRO_URL = 'https://github.com/Vindettobkb/Codegraphy-releases/releases/tag/v2.2.0';

  const PRO_FEATURES = {
    smart_context: {
      id: 'smart_context',
      title: 'AST Context Compression',
      icon: ICONS.ast,
      desc: 'Strip function bodies while keeping types, imports, and signatures (~85% fewer tokens).',
    },
    blast_radius: {
      id: 'blast_radius',
      title: 'Blast Radius & Git Diff',
      icon: ICONS.blast,
      desc: 'Trace downstream callers before refactoring and spot layer drift across commits.',
    },
    context_inspector: {
      id: 'context_inspector',
      title: 'Hybrid Context Inspector',
      icon: ICONS.inspector,
      desc: 'Switch files between Full, AST, and Excluded with exact token counts.',
    },
    mcp_tools: {
      id: 'mcp_tools',
      title: 'Unlimited Files & 11 MCP Tools',
      icon: ICONS.mcp,
      desc: 'Scan full repositories and expose impact, diff, and test tools over STDIO.',
    },
  };

  function closeProModal(e) {
    if (e && e.preventDefault) {
      e.preventDefault();
      e.stopPropagation();
    }
    const modals = document.querySelectorAll('.cg-modal-backdrop, .cg-modal-overlay, #cg-pro-modal-backdrop');
    modals.forEach(m => {
      m.style.display = 'none';
      m.remove();
    });
  }

  window.closeCodeGraphyProModal = closeProModal;

  function createBadge(featureId) {
    const badge = document.createElement('span');
    badge.className = 'cg-pro-badge';
    badge.textContent = 'PRO';
    badge.title = 'CodeGraphy Pro feature -- click to learn more';
    badge.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      openProModal(featureId);
    });
    return badge;
  }

  function openProModal(featureKeyOrTitle) {
    closeProModal(); // remove any existing modal first

    let feat = null;
    if (featureKeyOrTitle && PRO_FEATURES[featureKeyOrTitle]) {
      feat = PRO_FEATURES[featureKeyOrTitle];
    } else if (typeof featureKeyOrTitle === 'string') {
      const lower = featureKeyOrTitle.toLowerCase();
      for (const k of Object.keys(PRO_FEATURES)) {
        if (lower.includes(k) || PRO_FEATURES[k].title.toLowerCase().includes(lower)) {
          feat = PRO_FEATURES[k];
          break;
        }
      }
    }
    if (!feat) feat = PRO_FEATURES.smart_context;

    const featureCards = Object.values(PRO_FEATURES).map(f => `
      <div class="cg-feature-card ${f.id === feat.id ? 'highlight' : ''}">
        <div class="cg-feature-card-header">
          ${f.icon}
          <span>${f.title}</span>
        </div>
        <p class="cg-feature-card-desc">${f.desc}</p>
      </div>
    `).join('');

    const tableRows = [
      { label: 'Project size',            lite: '150 files',  pro: 'Unlimited' },
      { label: 'MCP tools',               lite: '3',          pro: '11' },
      { label: 'AST Compression',         lite: null,         pro: 'Included' },
      { label: 'Blast Radius & Git Diff', lite: null,         pro: 'Included' },
    ].map(r => `
      <div class="cg-comparison-row">
        <span style="color:#94A3B8;">${r.label}</span>
        <span style="color:${r.lite ? '#CBD5E1' : '#475569'}; display:inline-flex; align-items:center; gap:4px;">
          ${r.lite ? r.lite : ICONS.dash}
        </span>
        <span style="color:#38BDF8; display:inline-flex; align-items:center; gap:4px;">
          ${ICONS.check}&nbsp;${r.pro}
        </span>
      </div>
    `).join('');

    const backdrop = document.createElement('div');
    backdrop.id = 'cg-pro-modal-backdrop';
    backdrop.className = 'cg-modal-backdrop cg-modal-overlay';
    backdrop.style.display = 'flex';

    backdrop.innerHTML = `
      <div class="cg-modal-card" role="dialog" aria-modal="true" aria-label="CodeGraphy Pro">
        <div class="cg-modal-header">
          <div class="cg-modal-title-wrap">
            <div class="cg-modal-title-row">
              <h2 class="cg-modal-title">CodeGraphy Pro</h2>
            </div>
            <p class="cg-modal-subtitle">Full AST compression, impact analysis, and unlimited project scanning.</p>
          </div>
          <button type="button" class="cg-modal-close-btn" id="cg-modal-close-btn" aria-label="Close dialog">
            ${ICONS.close}
          </button>
        </div>

        <div class="cg-modal-body">
          <div class="cg-feature-grid">
            ${featureCards}
          </div>

          <div class="cg-comparison-box">
            <div class="cg-comparison-header">
              <span>Capability</span>
              <span>Lite</span>
              <span>Pro</span>
            </div>
            ${tableRows}
          </div>
        </div>

        <div class="cg-modal-footer">
          <button type="button" class="cg-btn-secondary" id="cg-modal-dismiss-btn">Continue with Lite</button>
          <a class="cg-btn-primary" href="${PRO_URL}" target="_blank" rel="noopener noreferrer">
            Get CodeGraphy Pro
            ${ICONS.arrow}
          </a>
        </div>
      </div>
    `;

    // Click handler with bubbling and capture
    function handleDismiss(e) {
      e.preventDefault();
      e.stopPropagation();
      closeProModal(e);
    }

    // 1. Outside click
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        handleDismiss(e);
      }
    });

    document.body.appendChild(backdrop);

    // 2. Direct event listeners on buttons
    const closeBtn = backdrop.querySelector('#cg-modal-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', handleDismiss, true);
      closeBtn.onclick = handleDismiss;
    }

    const dismissBtn = backdrop.querySelector('#cg-modal-dismiss-btn');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', handleDismiss, true);
      dismissBtn.onclick = handleDismiss;
    }
  }

  window.openCodeGraphyProModal = openProModal;

  // Global keydown for Escape
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' || e.keyCode === 27) {
      closeProModal(e);
    }
  }, true);

  function attachBadges() {
    // Git Diff buttons
    document.querySelectorAll('button[title*="Git Architecture Diff"], button[aria-label*="Git Architecture Diff"]').forEach(btn => {
      if (btn.closest('.cg-modal-card') || btn.closest('.cg-modal-overlay') || btn.closest('#cg-pro-modal-backdrop')) return;
      if (!btn.dataset.cgProHandled) {
        btn.dataset.cgProHandled = 'true';
        btn.appendChild(createBadge('blast_radius'));
        btn.addEventListener('click', (e) => {
          if (e.target.closest('.cg-modal-overlay') || e.target.closest('.cg-modal-card')) return;
          e.preventDefault();
          e.stopPropagation();
          openProModal('blast_radius');
        }, true);
      }
    });

    // Blast Radius text buttons
    document.querySelectorAll('button, [role="button"]').forEach(el => {
      if (el.closest('.cg-modal-card') || el.closest('.cg-modal-overlay') || el.closest('#cg-pro-modal-backdrop')) return;
      const text = el.textContent || '';
      if (text.includes('Blast Radius') && !el.dataset.cgProHandled) {
        el.dataset.cgProHandled = 'true';
        el.appendChild(createBadge('blast_radius'));
        el.addEventListener('click', (e) => {
          if (e.target.closest('.cg-modal-overlay') || e.target.closest('.cg-modal-card')) return;
          e.preventDefault();
          e.stopPropagation();
          openProModal('blast_radius');
        }, true);
      }
    });

    // Context Inspector buttons
    document.querySelectorAll('button[title*="Inspector"], button[aria-label*="Inspector"]').forEach(btn => {
      if (btn.closest('.cg-modal-card') || btn.closest('.cg-modal-overlay') || btn.closest('#cg-pro-modal-backdrop')) return;
      if (!btn.dataset.cgProHandled) {
        btn.dataset.cgProHandled = 'true';
        btn.appendChild(createBadge('context_inspector'));
        btn.addEventListener('click', (e) => {
          if (e.target.closest('.cg-modal-overlay') || e.target.closest('.cg-modal-card')) return;
          e.preventDefault();
          e.stopPropagation();
          openProModal('context_inspector');
        }, true);
      }
    });

    // MCP Config headings only
    document.querySelectorAll('h3, h4').forEach(el => {
      if (el.closest('.cg-modal-card') || el.closest('.cg-modal-overlay') || el.closest('#cg-pro-modal-backdrop')) return;
      if ((el.textContent || '').includes('MCP Config') && !el.dataset.cgProHandled) {
        el.dataset.cgProHandled = 'true';
        el.appendChild(createBadge('mcp_tools'));
      }
    });

    // Top-bar PRO button
    const topBarLeft = document.querySelector('.top-bar-left');
    if (topBarLeft && !document.getElementById('cg-topbar-pro-btn')) {
      const proBtn = document.createElement('button');
      proBtn.id = 'cg-topbar-pro-btn';
      proBtn.className = 'cg-topbar-pro-btn';
      proBtn.type = 'button';
      proBtn.innerHTML = ICONS.pro + '<span>PRO Features</span>';
      proBtn.title = 'View CodeGraphy Pro features';
      proBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        openProModal('smart_context');
      });
      topBarLeft.appendChild(proBtn);
    }
  }

  // Intercept 402/403 pro-feature responses
  const originalFetch = window.fetch;
  window.fetch = async function (...args) {
    const res = await originalFetch.apply(this, args);
    const clone = res.clone();
    try {
      if (res.status === 402 || res.status === 403) {
        const body = await clone.json();
        if (body && (body.pro_feature || body.feature)) {
          openProModal(body.feature || 'smart_context');
        }
      }
    } catch { /* ignore non-JSON bodies */ }
    return res;
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { attachBadges(); setInterval(attachBadges, 800); });
  } else {
    attachBadges();
    setInterval(attachBadges, 800);
  }

  new MutationObserver(attachBadges).observe(document.documentElement, { childList: true, subtree: true });
})();

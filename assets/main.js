(() => {
  const root = document.documentElement;
  root.dataset.theme = 'dark';
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  if (themeMeta) themeMeta.setAttribute('content', '#050b12');

  const projectsGrid = document.querySelector('#projects .projects-grid');
  if (projectsGrid && !projectsGrid.querySelector('[data-project="shareholder-cms"]')) {
    const isEnglish = root.lang.startsWith('en');
    const article = document.createElement('article');
    article.className = 'project-card';
    article.dataset.project = 'shareholder-cms';
    article.innerHTML = isEnglish
      ? `<div class="project-media"><img src="../assets/projects/shareholder-cms.svg" alt="Shareholder Gift Service and CMS architecture preview" loading="lazy"></div><div class="project-topline"><span class="project-number">04</span><span class="project-badge">BUSINESS CMS</span></div><h3>Shareholder Gift Service & CMS Platform</h3><p>A maintainable service website with product and announcement CMS, Supabase authentication, PostgreSQL and cloud image storage.</p><ul class="tags"><li>Vue 3 / TypeScript</li><li>Supabase Auth + RLS</li><li>CMS + Storage</li></ul><div class="project-links"><a class="project-primary" href="projects/shareholder-cms/">Case Study</a><a href="https://github.com/yoya9933/-------_202601221138_XY_Propose_Minutes" target="_blank">GitHub ↗</a></div>`
      : `<div class="project-media"><img src="assets/projects/shareholder-cms.svg" alt="股東紀念品服務與 CMS 平台架構預覽" loading="lazy"></div><div class="project-topline"><span class="project-number">04</span><span class="project-badge">BUSINESS CMS</span></div><h3>股東紀念品服務與 CMS 平台</h3><p>整合公開服務網站、商品與公告後台、Supabase 認證、PostgreSQL 與雲端圖片儲存的商業網站。</p><ul class="tags"><li>Vue 3 / TypeScript</li><li>Supabase Auth + RLS</li><li>CMS + Storage</li></ul><div class="project-links"><a class="project-primary" href="projects/shareholder-cms/">看 Case Study</a><a href="https://github.com/yoya9933/-------_202601221138_XY_Propose_Minutes" target="_blank">GitHub ↗</a></div>`;
    projectsGrid.appendChild(article);
    projectsGrid.classList.add('has-four-selected');

    const headingCopy = document.querySelector('#projects .section-heading p:not(.section-index)');
    if (headingCopy) headingCopy.textContent = isEnglish
      ? 'Four selected projects spanning engineering data and AI, multiplayer web, field operations, and a maintainable business CMS.'
      : '四個代表專案涵蓋工程資料與 AI、多人 Web、活動現場營運，以及可持續維護的商業 CMS。';

    const structuredData = document.createElement('script');
    structuredData.type = 'application/ld+json';
    structuredData.textContent = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'SoftwareApplication',
      name: isEnglish ? 'Shareholder Gift Service & CMS Platform' : '股東紀念品服務與 CMS 平台',
      url: isEnglish ? 'https://yoya9933.page/en/projects/shareholder-cms/' : 'https://yoya9933.page/projects/shareholder-cms/',
      applicationCategory: 'BusinessApplication',
      operatingSystem: 'Web',
      codeRepository: 'https://github.com/yoya9933/-------_202601221138_XY_Propose_Minutes'
    });
    document.head.appendChild(structuredData);
  }

  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');
  if (toggle && nav) {
    const closeMenu = () => {
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', root.lang.startsWith('en') ? 'Open navigation' : '開啟導覽');
      toggle.textContent = '☰';
      nav.classList.remove('is-open');
    };
    closeMenu();
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') === 'true';
      if (open) closeMenu();
      else {
        toggle.setAttribute('aria-expanded', 'true');
        toggle.setAttribute('aria-label', root.lang.startsWith('en') ? 'Close navigation' : '關閉導覽');
        toggle.textContent = '×';
        nav.classList.add('is-open');
      }
    });
    nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeMenu(); });
    window.addEventListener('resize', () => { if (window.innerWidth > 900) closeMenu(); });
  }

  document.querySelectorAll('img[data-avatar-fallback]').forEach((img) => {
    img.addEventListener('error', () => {
      if (img.dataset.fallbackApplied === 'true') return;
      img.dataset.fallbackApplied = 'true';
      img.src = img.dataset.avatarFallback || '/assets/avatar-fallback.svg';
    }, { once: true });
  });

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealTargets = document.querySelectorAll('.section-heading, .project-card, .focus-card, .skill-groups article, .timeline-item, .contact, .case-section, .metric, .architecture, .v4-reveal');
  if (!reduceMotion && 'IntersectionObserver' in window && revealTargets.length) {
    document.body.classList.add('reveal-ready');
    revealTargets.forEach((element, index) => {
      element.classList.add('reveal', 'v4-reveal');
      element.style.setProperty('--reveal-delay', `${Math.min(index % 4, 3) * 55}ms`);
    });
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -36px' });
    revealTargets.forEach((element) => observer.observe(element));
  }
})();

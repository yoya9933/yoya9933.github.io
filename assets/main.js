(() => {
  const root = document.documentElement;
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  const themeColors = { dark: '#07111f', light: '#f5f8fc' };

  const setTheme = (theme, persist = false) => {
    root.dataset.theme = theme;
    if (themeMeta) themeMeta.setAttribute('content', themeColors[theme] || themeColors.dark);
    if (persist) localStorage.setItem('portfolioTheme', theme);
  };

  const savedTheme = localStorage.getItem('portfolioTheme');
  const systemLight = window.matchMedia('(prefers-color-scheme: light)').matches;
  setTheme(root.dataset.theme || savedTheme || (systemLight ? 'light' : 'dark'));

  const themeButtons = document.querySelectorAll('[data-theme-toggle]');
  const updateThemeButtons = () => {
    const light = root.dataset.theme === 'light';
    themeButtons.forEach((button) => {
      button.textContent = light ? 'Dark' : 'Light';
      button.setAttribute('aria-label', light ? 'Switch to dark mode' : 'Switch to light mode');
      button.setAttribute('aria-pressed', String(light));
    });
  };
  updateThemeButtons();
  themeButtons.forEach((button) => button.addEventListener('click', () => {
    setTheme(root.dataset.theme === 'light' ? 'dark' : 'light', true);
    updateThemeButtons();
  }));

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
  const revealTargets = document.querySelectorAll('.section-heading, .project-card, .focus-card, .skill-groups article, .timeline-item, .contact, .case-section, .metric, .architecture');
  if (!reduceMotion && 'IntersectionObserver' in window && revealTargets.length) {
    document.body.classList.add('reveal-ready');
    revealTargets.forEach((element, index) => {
      element.classList.add('reveal');
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

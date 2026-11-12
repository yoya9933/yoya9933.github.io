(() => {
  const root = document.documentElement;
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

  // Update the active navigation link, scroll progress and back-to-top control.
  const mobileSectionLabel = document.querySelector('.mobile-section-label');
  const progressFill = document.querySelector('.scroll-progress-fill');
  const backToTop = document.querySelector('.back-to-top');
  if (nav && progressFill && backToTop) {
    const sections = [...nav.querySelectorAll('a[href^="#"]')]
      .map((link) => ({ link, section: document.getElementById(link.hash.slice(1)) }))
      .filter(({ section }) => section);
    let scheduled = false;
    const updateReadingPosition = () => {
      const headerBottom = document.querySelector('.site-header').getBoundingClientRect().bottom + 20;
      const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
      const scrolled = Math.max(0, Math.min(window.scrollY, maxScroll));
      let current = null;
      for (const { link, section } of sections) {
        if (section.getBoundingClientRect().top <= headerBottom) current = link;
      }
      if (maxScroll > 0 && scrolled >= maxScroll - 4) current = sections[sections.length - 1]?.link || null;
      sections.forEach(({ link }) => {
        if (link === current) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
      if (mobileSectionLabel) {
        const heading = current ? current.textContent.trim() : (root.lang.startsWith('en') ? 'Home' : '首頁');
        const label = (root.lang.startsWith('en') ? 'Now: ' : '目前：') + heading;
        if (mobileSectionLabel.textContent !== label) mobileSectionLabel.textContent = label;
      }
      progressFill.style.transform = `scaleX(${maxScroll ? scrolled / maxScroll : 0})`;
      backToTop.classList.toggle('is-visible', scrolled > 500);
      scheduled = false;
    };
    const scheduleReadingPosition = () => {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(updateReadingPosition);
    };
    window.addEventListener('scroll', scheduleReadingPosition, { passive: true });
    window.addEventListener('resize', scheduleReadingPosition);
    window.addEventListener('hashchange', scheduleReadingPosition);
    scheduleReadingPosition();
  }

  // Copy the same canonical project URLs used for the Case Study links.
  document.querySelectorAll('.copy-project-link').forEach((button) => {
    const originalText = button.textContent;
    const originalLabel = button.getAttribute('aria-label');
    let restoreTimer;
    button.addEventListener('click', async () => {
      const url = button.dataset.copyUrl;
      if (!url) return;
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(url);
        const message = root.lang.startsWith('en') ? 'Link copied' : '已複製連結';
        button.textContent = message;
        button.setAttribute('aria-label', message);
        clearTimeout(restoreTimer);
        restoreTimer = setTimeout(() => {
          button.textContent = originalText;
          if (originalLabel) button.setAttribute('aria-label', originalLabel);
          else button.removeAttribute('aria-label');
        }, 2200);
      } catch {
        window.prompt(root.lang.startsWith('en') ? 'Copy this project link:' : '請手動複製作品連結：', url);
      }
    });
  });

  // A subtle glow follows the mouse within project cards, never on touch or reduced motion.
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)');
  if (finePointer.matches) {
    document.querySelectorAll('.project-card').forEach((card) => {
      card.classList.add('pointer-glow');
      card.addEventListener('pointermove', (event) => {
        if (!finePointer.matches) return;
        const rect = card.getBoundingClientRect();
        card.style.setProperty('--pointer-x', (event.clientX - rect.left) + 'px');
        card.style.setProperty('--pointer-y', (event.clientY - rect.top) + 'px');
      }, { passive: true });
    });
  }

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealTargets = document.querySelectorAll('.section-heading, .project-card, .skill-groups article, .timeline-item, .contact, .case-section, .metric, .architecture, .v4-reveal');
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

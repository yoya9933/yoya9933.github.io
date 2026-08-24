(() => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');

  if (toggle && nav) {
    const closeMenu = () => {
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', '開啟導覽');
      toggle.textContent = '☰';
      nav.classList.remove('is-open');
    };

    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') === 'true';
      if (open) {
        closeMenu();
      } else {
        toggle.setAttribute('aria-expanded', 'true');
        toggle.setAttribute('aria-label', '關閉導覽');
        toggle.textContent = '×';
        nav.classList.add('is-open');
      }
    });

    nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 900) closeMenu();
    });
  }

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealTargets = document.querySelectorAll(
    '.section-heading, .project-card, .focus-card, .skill-groups article, .timeline-item, .contact, .case-section'
  );

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

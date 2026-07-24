(function () {
  const views = Array.from(document.querySelectorAll('[data-view]'));
  const viewLinks = Array.from(document.querySelectorAll('[data-view-link]'));
  const validViews = new Set(views.map((view) => view.dataset.view));

  function showView(name, updateHash) {
    const target = validViews.has(name) ? name : 'home';
    views.forEach((view) => { view.hidden = view.dataset.view !== target; });
    viewLinks.forEach((link) => link.classList.toggle('active', link.dataset.viewLink === target));
    document.title = `${target === 'home' ? 'Home' : target.replace('-', ' ')} - AI Job Risk preview`;
    if (updateHash && location.hash !== `#${target}`) history.pushState(null, '', `#${target}`);
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  viewLinks.forEach((link) => link.addEventListener('click', (event) => {
    event.preventDefault();
    showView(link.dataset.viewLink, true);
  }));
  window.addEventListener('hashchange', () => showView(location.hash.slice(1), false));
  showView(location.hash.slice(1), false);

  const paletteSelect = document.getElementById('palette-select');
  paletteSelect.value = document.documentElement.dataset.palette || 'current';
  paletteSelect.addEventListener('change', () => {
    document.documentElement.dataset.palette = paletteSelect.value;
    try { localStorage.setItem('preview-palette', paletteSelect.value); } catch (_) {}
  });

  const themeToggle = document.getElementById('theme-toggle');
  themeToggle.addEventListener('click', () => {
    document.documentElement.dataset.theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('preview-mode', document.documentElement.dataset.theme); } catch (_) {}
  });

  const occupations = [
    ['Accountant', '68 risk · Canada'],
    ['Graphic Designer', '58 risk · Canada'],
    ['Software Engineer', '47 risk · Canada'],
    ['Registered Nurse', '24 risk · Canada'],
    ['Electrician', '18 risk · Canada']
  ];
  const query = document.getElementById('job-query');
  const suggestions = document.getElementById('search-suggestions');
  function renderSuggestions() {
    const value = query.value.trim().toLowerCase();
    if (!value) { suggestions.hidden = true; return; }
    const matches = occupations.filter(([name]) => name.toLowerCase().includes(value)).slice(0, 4);
    suggestions.innerHTML = matches.length
      ? matches.map(([name, meta]) => `<button type="button"><strong>${name}</strong><span>${meta}</span></button>`).join('')
      : '<button type="button"><strong>No exact sample match</strong><span>View Accountant demo</span></button>';
    suggestions.hidden = false;
    suggestions.querySelectorAll('button').forEach((button) => button.addEventListener('click', () => showView('job', true)));
  }
  query.addEventListener('input', renderSuggestions);
  document.getElementById('job-search').addEventListener('submit', (event) => { event.preventDefault(); showView('job', true); });

  const stageContent = {
    risk: ['Workforce exposure', 'Where AI pressure is concentrated'],
    safe: ['Human resilience', 'Careers with the strongest human moat'],
    matrix: ['Career economics', 'Where salary and AI resilience meet']
  };
  document.querySelectorAll('[data-home-tab]').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('[data-home-tab]').forEach((tab) => tab.classList.remove('active'));
    button.classList.add('active');
    const [kicker, title] = stageContent[button.dataset.homeTab];
    document.getElementById('stage-kicker').textContent = kicker;
    document.getElementById('stage-title').textContent = title;
  }));

  document.querySelectorAll('[data-job-tab]').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('[data-job-tab]').forEach((tab) => tab.classList.remove('active'));
    document.querySelectorAll('[data-job-panel]').forEach((panel) => { panel.hidden = panel.dataset.jobPanel !== button.dataset.jobTab; });
    button.classList.add('active');
  }));

  document.querySelectorAll('[data-salary-view]').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('[data-salary-view]').forEach((tab) => tab.classList.remove('active'));
    document.querySelectorAll('[data-salary-panel]').forEach((panel) => { panel.hidden = panel.dataset.salaryPanel !== button.dataset.salaryView; });
    button.classList.add('active');
  }));

  const countryFilter = document.getElementById('country-filter');
  countryFilter.addEventListener('input', () => {
    const value = countryFilter.value.trim().toLowerCase();
    document.querySelectorAll('#country-table tbody tr').forEach((row) => {
      row.hidden = !row.cells[1].textContent.toLowerCase().includes(value);
    });
  });

  document.querySelectorAll('.chip').forEach((chip) => chip.addEventListener('click', () => {
    chip.closest('.chip-row').querySelectorAll('.chip').forEach((item) => item.classList.remove('active'));
    chip.classList.add('active');
  }));

  document.getElementById('find-jobs').addEventListener('click', () => {
    document.querySelector('[data-salary-panel="scatter"]').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();

const CONFIG = {
  careerGraph: 'https://aicareergraph.com',
  riskMap: 'https://aijobriskmap.com',
  research: 'https://aijobrisk.com'
};

const MODEL_VERSION = '1.0';

const COUNTRIES = {
  US: { name: 'United States', path: 'united-states' },
  AU: { name: 'Australia', path: 'australia' },
  UK: { name: 'United Kingdom', path: 'united-kingdom' },
  CA: { name: 'Canada', path: 'canada' },
  NZ: { name: 'New Zealand', path: 'new-zealand' },
  DE: { name: 'Germany', path: 'germany' },
  FR: { name: 'France', path: 'france' },
  ES: { name: 'Spain', path: 'spain' },
  IT: { name: 'Italy', path: 'italy' },
  NL: { name: 'Netherlands', path: 'netherlands' },
  IE: { name: 'Ireland', path: 'ireland' },
  JP: { name: 'Japan', path: 'japan' },
  KR: { name: 'South Korea', path: 'south-korea' }
};

const TASKS = [
  { id: 'routine', name: 'Routine information work', note: 'Forms, records, scheduling, standard reports', automation: .92, human: .12, augment: .65 },
  { id: 'analysis', name: 'Analysis and problem-solving', note: 'Research, models, diagnosis, technical decisions', automation: .58, human: .48, augment: .92 },
  { id: 'content', name: 'Writing and content creation', note: 'Drafts, presentations, code, visual concepts', automation: .76, human: .35, augment: .9 },
  { id: 'people', name: 'Communication and care', note: 'Clients, patients, students, colleagues', automation: .25, human: .88, augment: .55 },
  { id: 'decisions', name: 'Judgment and accountability', note: 'Trade-offs, approvals, negotiation, leadership', automation: .18, human: .96, augment: .58 },
  { id: 'physical', name: 'Physical or on-site work', note: 'Equipment, environments, dexterity, field work', automation: .1, human: .91, augment: .34 }
];

const CONTEXTS = [
  { id: 'digital', question: 'Are your inputs and outputs mostly digital?', answers: [['No', 0], ['Mixed', .5], ['Yes', 1]], risk: 1 },
  { id: 'repeatable', question: 'Does the work follow repeatable rules?', answers: [['Rarely', 0], ['Sometimes', .5], ['Often', 1]], risk: 1 },
  { id: 'accountability', question: 'Must a person formally own the outcome?', answers: [['No', 0], ['Shared', .5], ['Yes', 1]], risk: -1 },
  { id: 'relationships', question: 'Do trust and long-term relationships affect success?', answers: [['Little', 0], ['Somewhat', .5], ['A lot', 1]], risk: -1 },
  { id: 'uncertainty', question: 'Do you handle unusual or ambiguous situations?', answers: [['Rarely', 0], ['Sometimes', .5], ['Often', 1]], risk: -1 },
  { id: 'adoption', question: 'Is your workplace already using AI in this role?', answers: [['No', 0], ['Piloting', .5], ['Widely', 1]], risk: 1 }
];

const STEP_TITLES = ['Your role', 'Your task mix', 'Work context', 'Your goal'];
const RANGE_LABELS = ['None', 'A little', 'Some', 'A lot', 'Core work'];
const state = {
  step: 1,
  occupations: [],
  selectedJob: null,
  tasks: Object.fromEntries(TASKS.map((task) => [task.id, 2])),
  context: Object.fromEntries(CONTEXTS.map((item) => [item.id, .5]))
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const clamp = (value, min = 0, max = 100) => Math.round(Math.min(max, Math.max(min, value)));
const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));

function track(event, details = {}) {
  const payload = { event: `ijap_${event}`, ...details };
  window.dataLayer?.push(payload);
  window.dispatchEvent(new CustomEvent('ijap:event', { detail: payload }));
}

function renderTasks() {
  $('#task-list').innerHTML = TASKS.map((task) => `
    <label class="task-row" for="task-${task.id}">
      <span class="task-copy"><strong>${task.name}</strong><small>${task.note}</small></span>
      <span class="range-wrap">
        <input type="range" id="task-${task.id}" min="0" max="4" step="1" value="2" data-task="${task.id}">
        <span class="range-value" id="task-${task.id}-value">Some</span>
      </span>
    </label>
  `).join('');

  $$('[data-task]').forEach((input) => input.addEventListener('input', () => {
    state.tasks[input.dataset.task] = Number(input.value);
    $(`#${input.id}-value`).textContent = RANGE_LABELS[Number(input.value)];
  }));
}

function renderContexts() {
  $('#context-list').innerHTML = CONTEXTS.map((item) => `
    <div class="context-row">
      <p id="context-${item.id}-label">${item.question}</p>
      <div class="segmented" role="radiogroup" aria-labelledby="context-${item.id}-label">
        ${item.answers.map(([label, value], index) => `
          <label><input type="radio" name="context-${item.id}" value="${value}" ${index === 1 ? 'checked' : ''}><span>${label}</span></label>
        `).join('')}
      </div>
    </div>
  `).join('');

  CONTEXTS.forEach((item) => {
    $$(`input[name="context-${item.id}"]`).forEach((input) => input.addEventListener('change', () => {
      state.context[item.id] = Number(input.value);
    }));
  });
}

async function loadOccupations() {
  try {
    const response = await fetch('/data/occupations.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    state.occupations = payload.occupations;
    $('#search-status').textContent = `${payload.occupations.length.toLocaleString()} roles`;
  } catch (error) {
    $('#search-status').textContent = 'Search unavailable';
    console.error('Could not load occupation index:', error);
  }
}

function searchJobs(query) {
  const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return [];
  return state.occupations
    .map((job) => {
      const name = job.name.toLowerCase();
      const aliases = (job.aliases || []).join(' ').toLowerCase();
      const allMatch = terms.every((term) => name.includes(term) || aliases.includes(term));
      if (!allMatch) return null;
      let score = name === query.toLowerCase() ? 0 : name.startsWith(query.toLowerCase()) ? 1 : 2;
      score += name.length / 1000;
      return { job, score };
    })
    .filter(Boolean)
    .sort((a, b) => a.score - b.score)
    .slice(0, 8)
    .map(({ job }) => job);
}

function renderJobOptions(matches) {
  const options = $('#job-options');
  if (!matches.length) {
    options.innerHTML = '<div class="job-option"><strong>No close match</strong><span>Try a shorter or more common title</span></div>';
  } else {
    options.innerHTML = matches.map((job, index) => `
      <button class="job-option" type="button" role="option" data-index="${index}">
        <strong>${escapeHtml(job.name)}</strong>
        <span>${escapeHtml(job.category)} · ${job.countries.length} ${job.countries.length === 1 ? 'country' : 'countries'}</span>
      </button>
    `).join('');
    $$('.job-option[data-index]', options).forEach((button) => button.addEventListener('click', () => selectJob(matches[Number(button.dataset.index)])));
  }
  options.hidden = false;
  $('#job-search').setAttribute('aria-expanded', 'true');
}

function selectJob(job) {
  state.selectedJob = job;
  $('#job-search').value = job.name;
  $('#job-options').hidden = true;
  $('#job-search').setAttribute('aria-expanded', 'false');
  $('#job-error').hidden = true;
  track('occupation_selected', { occupation: job.slug });
}

function updateStep() {
  $$('.step-panel').forEach((panel) => {
    const active = Number(panel.dataset.step) === state.step;
    panel.hidden = !active;
    panel.classList.toggle('is-active', active);
  });
  $('#step-label').textContent = `Step ${state.step} of 4`;
  $('#step-title').textContent = STEP_TITLES[state.step - 1];
  $('#progress-bar').style.width = `${state.step * 25}%`;
  $('#back-button').hidden = state.step === 1;
  $('#next-button').innerHTML = state.step === 4 ? 'See my result <span aria-hidden="true">→</span>' : 'Continue <span aria-hidden="true">→</span>';
  $('#assessment-tool').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function validateStep() {
  if (state.step !== 1) return true;
  const typed = $('#job-search').value.trim();
  if (state.selectedJob && typed === state.selectedJob.name) return true;
  const exact = state.occupations.find((job) => job.name.toLowerCase() === typed.toLowerCase());
  if (exact) {
    selectJob(exact);
    return true;
  }
  $('#job-error').hidden = false;
  $('#job-search').focus();
  return false;
}

function weightedTaskScore(key) {
  let total = 0;
  let weight = 0;
  TASKS.forEach((task) => {
    const amount = state.tasks[task.id];
    total += task[key] * amount;
    weight += amount;
  });
  return weight ? (total / weight) * 100 : 50;
}

function calculateResult() {
  const job = state.selectedJob;
  const level = $('input[name="level"]:checked').value;
  const levelRisk = { junior: 8, mid: 0, senior: -5, manager: -8 }[level];
  const levelMoat = { junior: -6, mid: 0, senior: 6, manager: 9 }[level];
  const taskAutomation = weightedTaskScore('automation');
  const taskHuman = weightedTaskScore('human');
  const taskAugment = weightedTaskScore('augment');
  const contextRisk = (
    state.context.digital + state.context.repeatable + state.context.adoption +
    (1 - state.context.accountability) + (1 - state.context.relationships) + (1 - state.context.uncertainty)
  ) / 6 * 100;
  const contextProtection = 100 - contextRisk;
  const baselineExposure = Number(job.exposure || 5) * 10;
  const baselineMoat = Number(job.moat || 5) * 10;
  const baselineUpside = Number(job.upside || 6) * 10;

  const exposure = clamp(baselineExposure * .58 + taskAutomation * .28 + contextRisk * .14 + levelRisk);
  const automation = clamp(exposure * .57 + taskAutomation * .2 + contextRisk * .23 + levelRisk);
  const human = clamp(baselineMoat * .43 + taskHuman * .34 + contextProtection * .23 + levelMoat);
  const augmentation = clamp(baselineUpside * .54 + taskAugment * .32 + (state.context.adoption * 100) * .14);
  const resilience = clamp((100 - automation) * .45 + human * .35 + augmentation * .2);

  return { exposure, automation, human, augmentation, resilience, level, taskAutomation, taskHuman };
}

function band(score, inverse = false) {
  const value = inverse ? 100 - score : score;
  if (value >= 75) return 'High';
  if (value >= 50) return 'Moderate';
  if (value >= 30) return 'Limited';
  return 'Low';
}

function verdictFor(result) {
  if (result.resilience >= 76) return 'Your role has strong human defenses.';
  if (result.resilience >= 61) return 'Your job is likely to change more than disappear.';
  if (result.resilience >= 46) return 'A meaningful part of your role is exposed.';
  return 'Your current task mix faces substantial automation pressure.';
}

function renderMetrics(result) {
  const metrics = [
    ['AI exposure', result.exposure, 'How much work AI can reach', 'var(--red)'],
    ['Automation pressure', result.automation, 'Pressure to reduce human effort', 'var(--yellow)'],
    ['Augmentation upside', result.augmentation, 'Potential to do more with AI', 'var(--blue)'],
    ['Human advantage', result.human, 'Trust, judgment and physical context', 'var(--teal)']
  ];
  $('#metric-grid').innerHTML = metrics.map(([name, score, note, color]) => `
    <div class="metric" style="--metric-color:${color}">
      <div class="metric-head"><span>${name}</span><strong>${score}/100</strong></div>
      <div class="metric-track"><span style="width:${score}%"></span></div>
      <small>${band(score)} · ${note}</small>
    </div>
  `).join('');
}

function rankedTasks(key) {
  return TASKS
    .map((task) => ({ ...task, score: state.tasks[task.id] * task[key] }))
    .filter((task) => state.tasks[task.id] > 0)
    .sort((a, b) => b.score - a.score);
}

function renderOutcomes() {
  const automate = rankedTasks('automation')[0] || TASKS[0];
  const augment = rankedTasks('augment').find((task) => task.id !== automate.id) || rankedTasks('augment')[0] || TASKS[1];
  const human = rankedTasks('human').find((task) => task.id !== automate.id && task.id !== augment.id) || rankedTasks('human')[0] || TASKS[4];
  $('#task-outcomes').innerHTML = `
    <div class="outcome automate"><span>Watch closely</span><strong>${automate.name}</strong></div>
    <div class="outcome augment"><span>Use AI to accelerate</span><strong>${augment.name}</strong></div>
    <div class="outcome human"><span>Build your moat</span><strong>${human.name}</strong></div>
  `;
  return { automate, augment, human };
}

function actionsFor(result, outcomes) {
  const goal = $('input[name="goal"]:checked').value;
  const goalActions = {
    protect: `Document where your judgment changes the outcome in ${outcomes.human.name.toLowerCase()}; make that value visible to your manager or clients.`,
    earn: `Package an AI-assisted workflow that improves speed or quality in ${outcomes.augment.name.toLowerCase()}, then measure the gain.`,
    switch: 'Compare adjacent roles that use your current domain knowledge but rely more on accountability, relationships or physical context.',
    learn: `Choose one approved AI tool and practice it on ${outcomes.augment.name.toLowerCase()} with a repeatable review checklist.`
  };
  const first = result.automation >= 60
    ? `Audit the time spent on ${outcomes.automate.name.toLowerCase()}. Separate repeatable steps from exceptions that still need you.`
    : `Identify one low-risk experiment in ${outcomes.augment.name.toLowerCase()} and establish a human review step.`;
  return [
    first,
    goalActions[goal],
    'Reassess in 90 days after your tools, responsibilities or workplace adoption change.'
  ];
}

function renderExternalLinks() {
  const job = state.selectedJob;
  const country = $('#country').value;
  const countryData = COUNTRIES[country];
  const mapHref = countryData ? `${CONFIG.riskMap}/${countryData.path}/` : `${CONFIG.riskMap}/`;
  const mapLabel = countryData ? `Compare roles across ${countryData.name}` : 'Explore the global AI job risk map';
  $('#external-links').innerHTML = `
    <a class="external-card" href="${CONFIG.careerGraph}/${job.categorySlug}/${job.slug}" target="_blank" rel="noopener">
      <span>AI Career Graph</span><strong>Full ${escapeHtml(job.name)} career profile →</strong>
    </a>
    <a class="external-card" href="${mapHref}" target="_blank" rel="noopener">
      <span>AI Job Risk Map</span><strong>${mapLabel} →</strong>
    </a>
    <a class="external-card" href="${CONFIG.research}/" target="_blank" rel="noopener">
      <span>AI Job Risk</span><strong>Read the latest evidence and analysis →</strong>
    </a>
  `;
}

function showResult() {
  const result = calculateResult();
  const job = state.selectedJob;
  const countryCode = $('#country').value;
  const country = COUNTRIES[countryCode]?.name;
  const exposedPhrase = result.exposure >= 65 ? 'a large share' : result.exposure >= 45 ? 'a meaningful share' : 'a limited share';

  $('#assessment-form').hidden = true;
  $('.progress-header').hidden = true;
  $('#results').hidden = false;
  $('#result-role').textContent = [job.name, country, result.level.replace('mid', 'mid-level')].filter(Boolean).join(' · ');
  $('#result-verdict').textContent = verdictFor(result);
  $('#result-summary').textContent = `${exposedPhrase[0].toUpperCase()}${exposedPhrase.slice(1)} of your task mix can be reached by current AI, but exposure is not the same as replacement. Your result reflects how repeatable the work is and how much it depends on human judgment, trust or physical context.`;
  $('#resilience-score').textContent = result.resilience;
  $('#score-ring').style.setProperty('--score', `${result.resilience}%`);
  renderMetrics(result);
  const outcomes = renderOutcomes();
  $('#action-plan').innerHTML = actionsFor(result, outcomes).map((action) => `<li>${escapeHtml(action)}</li>`).join('');
  renderExternalLinks();
  state.lastResult = result;
  $('#result-task-section').hidden = false;
  $('#result-plan-section').hidden = false;
  $('#shared-result-note').hidden = true;
  track('result_viewed', { occupation: job.slug, resilience_band: band(result.resilience) });
  $('#assessment-tool').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function restart() {
  state.step = 1;
  state.selectedJob = null;
  state.tasks = Object.fromEntries(TASKS.map((task) => [task.id, 2]));
  state.context = Object.fromEntries(CONTEXTS.map((item) => [item.id, .5]));
  $('#assessment-form').reset();
  $('#job-search').value = '';
  $$('[data-task]').forEach((input) => {
    input.value = 2;
    $(`#${input.id}-value`).textContent = 'Some';
  });
  $('#results').hidden = true;
  $('#assessment-form').hidden = false;
  $('.progress-header').hidden = false;
  $('#result-task-section').hidden = false;
  $('#result-plan-section').hidden = false;
  $('#shared-result-note').hidden = true;
  if (new URL(location.href).searchParams.has('r')) history.replaceState(null, '', '/#assessment-tool');
  updateStep();
}

async function copySummary() {
  const text = resultSummary(sharedResultUrl());
  try {
    await navigator.clipboard.writeText(text);
    $('#copy-button').textContent = 'Copied';
    setTimeout(() => { $('#copy-button').textContent = 'Copy summary'; }, 1600);
  } catch {
    window.prompt('Copy your result:', text);
  }
}

function encodeSharedResult() {
  const result = state.lastResult;
  const payload = {
    v: MODEL_VERSION,
    j: state.selectedJob.slug,
    r: result.resilience,
    e: result.exposure,
    a: result.automation,
    u: result.augmentation,
    h: result.human
  };
  return btoa(JSON.stringify(payload)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function decodeSharedResult(value) {
  try {
    const normalised = value.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(normalised.padEnd(Math.ceil(normalised.length / 4) * 4, '=')));
    const scores = ['r', 'e', 'a', 'u', 'h'];
    if (payload.v !== MODEL_VERSION || typeof payload.j !== 'string') return null;
    if (!scores.every((key) => Number.isInteger(payload[key]) && payload[key] >= 0 && payload[key] <= 100)) return null;
    return payload;
  } catch {
    return null;
  }
}

function sharedResultUrl() {
  return `${location.origin}/?r=${encodeSharedResult()}#assessment-tool`;
}

function resultSummary(url = 'https://ismyjobaiproof.com/') {
  return `My Job Resilience Score as a ${state.selectedJob.name}: ${state.lastResult.resilience}/100. This is a planning indicator, not a job-loss probability. ${url}`;
}

function roundedRect(context, x, y, width, height, radius) {
  context.beginPath();
  context.roundRect(x, y, width, height, radius);
  context.fill();
}

function wrapCanvasText(context, text, x, y, maxWidth, lineHeight, maxLines = 3) {
  const words = text.split(' ');
  let line = '';
  let lines = 0;
  for (const word of words) {
    const test = line ? `${line} ${word}` : word;
    if (context.measureText(test).width > maxWidth && line) {
      context.fillText(line, x, y + lines * lineHeight);
      line = word;
      lines += 1;
      if (lines === maxLines - 1) break;
    } else {
      line = test;
    }
  }
  context.fillText(line, x, y + lines * lineHeight);
}

async function createResultCard() {
  const canvas = document.createElement('canvas');
  canvas.width = 1200;
  canvas.height = 630;
  const context = canvas.getContext('2d');
  context.fillStyle = '#f4f6f2';
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = '#17211f';
  context.fillRect(0, 0, 18, canvas.height);
  context.font = '700 28px system-ui, sans-serif';
  context.fillText('IS MY JOB AI-PROOF?', 72, 82);
  context.fillStyle = '#5f6c68';
  context.font = '500 20px system-ui, sans-serif';
  context.fillText(`Personal result · Model ${MODEL_VERSION}`, 72, 118);
  context.fillStyle = '#17211f';
  context.font = '700 52px system-ui, sans-serif';
  wrapCanvasText(context, state.selectedJob.name, 72, 205, 700, 62, 2);
  context.fillStyle = '#087f73';
  context.beginPath();
  context.arc(1000, 218, 112, 0, Math.PI * 2);
  context.fill();
  context.fillStyle = '#ffffff';
  context.textAlign = 'center';
  context.font = '800 70px system-ui, sans-serif';
  context.fillText(String(state.lastResult.resilience), 1000, 230);
  context.font = '700 17px system-ui, sans-serif';
  context.fillText('JOB RESILIENCE', 1000, 270);
  context.textAlign = 'left';
  const metrics = [
    ['AI exposure', state.lastResult.exposure, '#bf4a3f'],
    ['Automation pressure', state.lastResult.automation, '#d8a522'],
    ['Augmentation upside', state.lastResult.augmentation, '#3474a5'],
    ['Human advantage', state.lastResult.human, '#087f73']
  ];
  metrics.forEach(([label, score, color], index) => {
    const x = 72 + (index % 2) * 410;
    const y = 382 + Math.floor(index / 2) * 92;
    context.fillStyle = '#ffffff';
    roundedRect(context, x, y, 370, 68, 6);
    context.fillStyle = color;
    context.fillRect(x, y, 7, 68);
    context.fillStyle = '#17211f';
    context.font = '650 20px system-ui, sans-serif';
    context.fillText(label, x + 24, y + 30);
    context.font = '800 25px system-ui, sans-serif';
    context.fillText(`${score}/100`, x + 258, y + 32);
  });
  context.fillStyle = '#5f6c68';
  context.font = '500 18px system-ui, sans-serif';
  context.fillText('Planning indicator, not a job-loss probability', 72, 594);
  context.fillStyle = '#17211f';
  context.font = '700 20px system-ui, sans-serif';
  context.fillText('ismyjobaiproof.com', 930, 594);
  return new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
}

async function shareResult() {
  const url = sharedResultUrl();
  const text = resultSummary(url);
  try {
    const blob = await createResultCard();
    const file = new File([blob], `job-resilience-${state.selectedJob.slug}.png`, { type: 'image/png' });
    if (navigator.share && navigator.canShare?.({ files: [file] })) {
      await navigator.share({ title: `${state.selectedJob.name}: Job Resilience ${state.lastResult.resilience}/100`, text, url, files: [file] });
    } else if (navigator.share) {
      await navigator.share({ title: 'My Job Resilience Score', text, url });
    } else {
      await navigator.clipboard.writeText(text);
      $('#share-button').textContent = 'Share link copied';
      setTimeout(() => { $('#share-button').textContent = 'Share result'; }, 1600);
    }
    track('result_shared', { occupation: state.selectedJob.slug, method: navigator.share ? 'native' : 'clipboard' });
  } catch (error) {
    if (error.name !== 'AbortError') window.prompt('Copy your result:', text);
  }
}

async function saveResultCard() {
  const blob = await createResultCard();
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `job-resilience-${state.selectedJob.slug}.png`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  track('result_card_saved', { occupation: state.selectedJob.slug });
}

function renderSharedResult(payload) {
  const job = state.occupations.find((item) => item.slug === payload.j);
  if (!job) return false;
  state.selectedJob = job;
  const result = { resilience: payload.r, exposure: payload.e, automation: payload.a, augmentation: payload.u, human: payload.h };
  state.lastResult = result;
  $('#assessment-form').hidden = true;
  $('.progress-header').hidden = true;
  $('#results').hidden = false;
  $('#result-role').textContent = `${job.name} · Shared score summary`;
  $('#result-verdict').textContent = verdictFor(result);
  $('#result-summary').textContent = 'This link contains summary scores only. Exposure is not the same as replacement, and another person with the same title may receive a different result.';
  $('#resilience-score').textContent = result.resilience;
  $('#score-ring').style.setProperty('--score', `${result.resilience}%`);
  renderMetrics(result);
  renderExternalLinks();
  $('#result-task-section').hidden = true;
  $('#result-plan-section').hidden = true;
  $('#shared-result-note').hidden = false;
  track('shared_result_viewed', { occupation: job.slug });
  return true;
}

async function applyUrlState() {
  await state.occupationsReady;
  const params = new URL(location.href).searchParams;
  const shared = params.get('r');
  if (shared && renderSharedResult(decodeSharedResult(shared) || {})) return;
  const jobSlug = params.get('job');
  if (jobSlug) await startPopularAssessment(jobSlug);
}

function focusAssessment() {
  if (!$('#results').hidden || state.step !== 1) restart();
  $('#assessment-tool').scrollIntoView({ behavior: 'smooth', block: 'start' });
  $('#job-search').focus({ preventScroll: true });
}

async function startPopularAssessment(slug) {
  await state.occupationsReady;
  const job = state.occupations.find((occupation) => occupation.slug === slug);
  if (!job) return;
  restart();
  selectJob(job);
  $('#country').value = '';
  $('#assessment-tool').scrollIntoView({ behavior: 'smooth', block: 'start' });
  $('#job-search').focus({ preventScroll: true });
}

function bindEvents() {
  const search = $('#job-search');
  search.addEventListener('input', () => {
    state.selectedJob = null;
    $('#job-error').hidden = true;
    if (search.value.trim().length < 2) {
      $('#job-options').hidden = true;
      search.setAttribute('aria-expanded', 'false');
      return;
    }
    renderJobOptions(searchJobs(search.value));
  });
  search.addEventListener('focus', () => {
    if (search.value.trim().length >= 2 && !state.selectedJob) renderJobOptions(searchJobs(search.value));
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.search-field')) {
      $('#job-options').hidden = true;
      search.setAttribute('aria-expanded', 'false');
    }
  });
  $('#next-button').addEventListener('click', () => {
    if (!validateStep()) return;
    if (state.step < 4) {
      if (state.step === 1) track('assessment_started', { occupation: state.selectedJob.slug });
      state.step += 1;
      updateStep();
    } else {
      showResult();
    }
  });
  $('#back-button').addEventListener('click', () => {
    if (state.step > 1) {
      state.step -= 1;
      updateStep();
    }
  });
  $('#restart-button').addEventListener('click', restart);
  $('#share-button').addEventListener('click', shareResult);
  $('#save-card-button').addEventListener('click', saveResultCard);
  $('#copy-button').addEventListener('click', copySummary);
  $('#print-button').addEventListener('click', () => window.print());
  $('#start-assessment-button').addEventListener('click', focusAssessment);
  $$('[data-popular-job]').forEach((button) => button.addEventListener('click', () => {
    startPopularAssessment(button.dataset.popularJob);
  }));
}

renderTasks();
renderContexts();
bindEvents();
state.occupationsReady = loadOccupations();
applyUrlState();
$('#year').textContent = new Date().getFullYear();

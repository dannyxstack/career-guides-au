export const SITE_URL = 'https://ismyjobaiproof.com';
export const MODEL_VERSION = '1.0';
export const DATA_SNAPSHOT = '2026-07-16';

export const featuredSlugs = [
  'customer-service-representative', 'graphic-designer', 'accountant', 'data-analyst',
  'marketing-manager', 'software-engineer', 'lawyer', 'electrician',
  'secondary-school-teacher', 'registered-nurse', 'administrative-assistant', 'writer',
  'translator', 'journalist', 'web-developer', 'cyber-security-professionals',
  'project-manager', 'human-resources-manager', 'financial-analyst', 'bookkeeper',
  'auditor', 'legal-secretary-paralegal', 'architect', 'civil-engineer',
  'mechanical-engineer', 'general-practitioner', 'pharmacist', 'dentist',
  'psychologist', 'social-worker', 'primary-school-teacher', 'university-lecturer',
  'chef', 'retail-manager-general', 'sales-manager', 'real-estate-agent',
  'truck-driver', 'delivery-driver', 'warehouse-worker', 'plumber', 'carpenter',
  'welder', 'automotive-mechanic', 'police-officer', 'firefighter', 'photographer',
  'film-and-video-editors', 'executive-assistant', 'occupational-therapist', 'data-scientist'
];

export const jobOverrides = {
  'customer-service-representative': {
    automate: ['Classifying routine enquiries', 'Drafting standard replies', 'Summarising customer histories'],
    human: ['De-escalating emotional cases', 'Owning unusual resolutions', 'Building customer trust'],
    augment: ['Real-time answer retrieval', 'Call and chat summaries', 'Quality-review assistance']
  },
  'graphic-designer': {
    automate: ['Producing first-pass variants', 'Resizing and adapting assets', 'Removing backgrounds and retouching'],
    human: ['Interpreting an ambiguous brief', 'Defending creative direction', 'Understanding brand and audience context'],
    augment: ['Rapid concept exploration', 'Reference and mood-board generation', 'Production workflow acceleration']
  },
  accountant: {
    automate: ['Transaction coding and reconciliation', 'Routine report preparation', 'First-pass variance detection'],
    human: ['Signing off accountable decisions', 'Interpreting unusual transactions', 'Advising stakeholders under uncertainty'],
    augment: ['Continuous anomaly review', 'Scenario modelling', 'Faster management reporting']
  },
  'data-analyst': {
    automate: ['Generating routine queries', 'Drafting recurring reports', 'Explaining standard chart patterns'],
    human: ['Defining the right business question', 'Validating messy source data', 'Influencing decisions with context'],
    augment: ['Exploratory analysis', 'SQL and code assistance', 'Narrative and visual iteration']
  },
  'software-engineer': {
    automate: ['Boilerplate implementation', 'Routine test generation', 'Code explanation and migration drafts'],
    human: ['Architecture trade-offs', 'Production accountability', 'Understanding unstated product constraints'],
    augment: ['Faster prototyping', 'Debugging assistance', 'Broader codebase navigation']
  },
  lawyer: {
    automate: ['Document review and classification', 'First-pass research', 'Template drafting'],
    human: ['Professional accountability', 'Negotiation and advocacy', 'Judgment in novel fact patterns'],
    augment: ['Faster matter preparation', 'Issue spotting', 'Draft comparison and summarisation']
  },
  electrician: {
    automate: ['Estimating and paperwork drafts', 'Standards lookup', 'Basic fault-diagnosis support'],
    human: ['Safe physical installation', 'On-site diagnosis', 'Licensed accountability'],
    augment: ['Mobile troubleshooting guidance', 'Documentation assistance', 'Predictive maintenance insights']
  },
  'secondary-school-teacher': {
    automate: ['Worksheet and quiz drafts', 'Routine feedback suggestions', 'Administrative summaries'],
    human: ['Motivating individual students', 'Managing a live classroom', 'Safeguarding and pastoral judgment'],
    augment: ['Lesson differentiation', 'Resource generation', 'Learning-gap identification']
  },
  'registered-nurse': {
    automate: ['Documentation assistance', 'Routine monitoring summaries', 'Administrative coordination'],
    human: ['Hands-on patient care', 'Clinical escalation judgment', 'Trust during vulnerable moments'],
    augment: ['Decision-support prompts', 'Handover summaries', 'Patient education drafts']
  }
};

export const categoryTasks = {
  'Business, Finance & Legal': {
    automate: ['Routine document processing', 'Standard reporting and reconciliation', 'First-pass research and drafting'],
    human: ['Accountable professional judgment', 'Negotiation and stakeholder trust', 'Handling exceptions and regulation'],
    augment: ['Faster analysis and drafting', 'Anomaly and pattern detection', 'Scenario preparation']
  },
  'Creative, Media & Personal Services': {
    automate: ['First-pass content variants', 'Routine production edits', 'Asset classification and adaptation'],
    human: ['Original direction and taste', 'Client and audience understanding', 'Reputation and creative accountability'],
    augment: ['Rapid ideation', 'Production acceleration', 'Personalised content exploration']
  },
  'Education & Community': {
    automate: ['Routine resource preparation', 'Administrative summaries', 'Standard information responses'],
    human: ['Trust and behaviour support', 'Live facilitation and care', 'Judgment around individual needs'],
    augment: ['Personalised materials', 'Planning assistance', 'Early identification of support needs']
  },
  'Engineering & Infrastructure': {
    automate: ['Routine calculations and documentation', 'Standard design iterations', 'Monitoring-data summaries'],
    human: ['Safety and design accountability', 'On-site constraints and trade-offs', 'Novel failure diagnosis'],
    augment: ['Simulation and option generation', 'Technical-document search', 'Predictive maintenance support']
  },
  'Healthcare & Care': {
    automate: ['Administrative documentation', 'Routine triage support', 'Standard patient information'],
    human: ['Hands-on care and trust', 'Clinical accountability', 'Judgment in complex cases'],
    augment: ['Decision support', 'Handover and record summaries', 'Personalised education']
  },
  'Hospitality, Retail & Tourism': {
    automate: ['Bookings and routine enquiries', 'Inventory and schedule optimisation', 'Standard promotions'],
    human: ['In-person service recovery', 'Live operational judgment', 'Relationship-led experiences'],
    augment: ['Demand forecasting', 'Personalised recommendations', 'Faster operational planning']
  },
  'IT & Digital': {
    automate: ['Boilerplate implementation', 'Routine testing and documentation', 'First-pass troubleshooting'],
    human: ['Architecture and security trade-offs', 'Production accountability', 'Translating ambiguous needs'],
    augment: ['Code and query assistance', 'Faster investigation', 'Prototype generation']
  },
  'Trades & Construction': {
    automate: ['Quoting and paperwork drafts', 'Standards and parts lookup', 'Routine planning'],
    human: ['Physical installation and repair', 'Site-specific diagnosis', 'Safety accountability'],
    augment: ['Mobile diagnostic support', 'Documentation assistance', 'Scheduling optimisation']
  },
  'Transport, Logistics & Mining': {
    automate: ['Route and load optimisation', 'Routine tracking updates', 'Administrative dispatch work'],
    human: ['Handling real-world exceptions', 'Safety-critical intervention', 'Physical inspection and coordination'],
    augment: ['Predictive maintenance', 'Live decision support', 'Network planning']
  },
  default: {
    automate: ['Routine digital administration', 'Standard information processing', 'First-pass drafting'],
    human: ['Contextual judgment', 'Trust and accountability', 'Physical or unusual situations'],
    augment: ['Faster research', 'Decision preparation', 'Workflow assistance']
  }
};

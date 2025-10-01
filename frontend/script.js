// Application state (in-memory variables held by the browser while the page is open)
// - currentTab: which tab is visible (upload/config/results)
// - sourceCode: the contents of the uploaded .py file
// - fileName: the uploaded file's name
// - isAnalyzing: whether a request is in progress (disables the button + shows loading)
// - report: the latest report returned from the backend (normalized for the UI)
// - config: which detectors are enabled and their thresholds as chosen in the UI
let currentTab = "upload"
let sourceCode = ""
let fileName = ""
let isAnalyzing = false
let report = null
let config = {
  smells: {
    LongMethod: true,
    GodClass: true,
    DuplicatedCode: true,
    LargeParameterList: true,
    MagicNumbers: true,
    FeatureEnvy: true,
  },
  thresholds: {
    longMethodSloc: 30,
    longMethodCyclomatic: 12,
    godClassMethods: 20,
    godClassFields: 15,
    largeParameterList: 6,
    magicNumberOccurrences: 3,
  },
}

// Helper to format threshold keys for display
const formatThresholdKey = (key) => {
  let formatted = key.replace(/_/g, ' ');
  formatted = formatted.replace(/\b(\w)/g, (char) => char.toUpperCase()); // Capitalize first letter of each word

  // Expand common abbreviations
  formatted = formatted.replace('Sloc', 'Source Lines Of Code');
  formatted = formatted.replace('Atfd', 'Access To Foreign Data');
  formatted = formatted.replace('Fdp', 'Foreign Data Providers');
  formatted = formatted.replace('Laa', 'Locality Of Attribute Accesses');

  // Specific replacement for the requested change
  if (key === 'min_sloc') { // Assuming 'min_sloc' is the raw key for "Min Source Lines Of Code"
    return 'Source Lines Of Code Threshold';
  }

  return formatted;
};

// Initialize the application after the HTML is ready
// - Sets up icons
// - Wires up all event listeners for tabs, file upload, analyze button, and config inputs
// - Ensures the Analyze button starts disabled (until a file is loaded)
// - Loads default configuration from backend
document.addEventListener("DOMContentLoaded", () => {
  initializeLucideIcons()
  setupEventListeners()
  updateAnalyzeButton()
  loadDefaultConfig()
})

// Load default configuration from backend
// This ensures the frontend uses the same defaults as the backend
async function loadDefaultConfig() {
  try {
    const response = await fetch("http://localhost:5000/api/config/default")
    if (response.ok) {
      const backendConfig = await response.json()
      
      // Update config with backend defaults
      config.smells = backendConfig.smells || config.smells
      config.thresholds = {
        longMethodSloc: backendConfig.long_method?.sloc || 30,
        longMethodCyclomatic: backendConfig.long_method?.cyclomatic || 12,
        godClassMethods: backendConfig.god_class?.max_methods || 20,
        godClassFields: backendConfig.god_class?.max_fields || 15,
        largeParameterList: backendConfig.large_parameter_list?.params || 6,
        magicNumberOccurrences: backendConfig.magic_numbers?.min_occurrences || 3,
      }
      
      // Update UI with new defaults
      updateConfigUI()
    }
  } catch (error) {
    console.warn("Could not load default config from backend, using fallback defaults:", error)
  }
}

// Update UI elements with current config values
function updateConfigUI() {
  // Update smell switches
  Object.keys(config.smells).forEach(smellType => {
    const switchEl = document.getElementById(smellType)
    if (switchEl) {
      switchEl.checked = config.smells[smellType]
    }
  })
  
  // Update threshold inputs
  Object.keys(config.thresholds).forEach(thresholdKey => {
    const inputEl = document.getElementById(thresholdKey.replace(/([A-Z])/g, '-$1').toLowerCase())
    if (inputEl) {
      inputEl.value = config.thresholds[thresholdKey]
    }
  })
}

// Initialize Lucide icons (SVG icons library)
// If the library is available on the window, render icons for any elements with data-lucide
function initializeLucideIcons() {
  const lucide = window.lucide // Declare the lucide variable
  if (typeof lucide !== "undefined") {
    lucide.createIcons()
  }
}

// Setup event listeners for UI interactions
// - Tab navigation buttons switch the visible content
// - File input reads the selected Python file into memory
// - Analyze button triggers the backend request
// - Switches and number inputs update the in-memory config
function setupEventListeners() {
  // Tab navigation
  const tabTriggers = document.querySelectorAll(".tab-trigger")
  tabTriggers.forEach((trigger) => {
    trigger.addEventListener("click", () => {
      const tabName = trigger.getAttribute("data-tab")
      switchTab(tabName)
    })
  })

  // File upload
  const fileInput = document.getElementById("file-upload")
  fileInput.addEventListener("change", handleFileUpload)

  // Analyze button
  const analyzeBtn = document.getElementById("analyze-btn")
  analyzeBtn.addEventListener("click", analyzeCode)

  // Configuration switches
  const switches = document.querySelectorAll('.switch input[type="checkbox"]')
  switches.forEach((switchEl) => {
    switchEl.addEventListener("change", (e) => {
      const smellType = e.target.id
      config.smells[smellType] = e.target.checked
    })
  })

  // Threshold inputs
  const thresholdInputs = document.querySelectorAll(".number-input")
  thresholdInputs.forEach((input) => {
    input.addEventListener("change", (e) => {
      const thresholdKey = getThresholdKey(e.target.id)
      if (thresholdKey) {
        config.thresholds[thresholdKey] = Number.parseInt(e.target.value)
      }
    })
  })
}

// Switch between tabs (upload/config/results)
// - Updates the selected tab button styling
// - Shows the corresponding tab content and hides the others
function switchTab(tabName) {
  // Update tab triggers
  const tabTriggers = document.querySelectorAll(".tab-trigger")
  tabTriggers.forEach((trigger) => {
    trigger.classList.remove("active")
    if (trigger.getAttribute("data-tab") === tabName) {
      trigger.classList.add("active")
    }
  })

  // Update tab content
  const tabContents = document.querySelectorAll(".tab-content")
  tabContents.forEach((content) => {
    content.classList.remove("active")
  })

  const activeTab = document.getElementById(`${tabName}-tab`)
  if (activeTab) {
    activeTab.classList.add("active")
  }

  currentTab = tabName
}

// Handle file upload
// - Only accepts .py files
// - Reads the file into memory using FileReader and stores its text in sourceCode
// - Updates the filename display and enables the Analyze button
function handleFileUpload(event) {
  const file = event.target.files[0]
  if (file && file.name.endsWith(".py")) {
    fileName = file.name
    const reader = new FileReader()
    reader.onload = (e) => {
      sourceCode = e.target.result
      updateFileInfo()
      updateAnalyzeButton()
    }
    reader.readAsText(file)
  }
}

// Update file info display (shows or hides the uploaded filename in the UI)
function updateFileInfo() {
  const fileNameEl = document.getElementById("file-name")
  const fileNameText = document.querySelector(".filename-text")

  if (fileName) {
    fileNameText.textContent = fileName
    fileNameEl.classList.remove("hidden")
  } else {
    fileNameEl.classList.add("hidden")
  }
}

// Update analyze button state
// - Disabled when there is no code or while a request is in-flight
// - Shows "Analyzing..." text while waiting for the backend
function updateAnalyzeButton() {
  const analyzeBtn = document.getElementById("analyze-btn")
  const hasCode = sourceCode.trim().length > 0

  analyzeBtn.disabled = !hasCode || isAnalyzing
  analyzeBtn.textContent = isAnalyzing ? "Analyzing..." : "Analyze Code"
}

// Get threshold key from an input element id
// - Maps DOM ids to the corresponding keys in config.thresholds
function getThresholdKey(inputId) {
  const mapping = {
    "long-method-sloc": "longMethodSloc",
    "god-class-methods": "godClassMethods",
    "large-param-list": "largeParameterList",
    "magic-numbers": "magicNumberOccurrences"
  }
  return mapping[inputId]
}

// Analyze code
// 1) Validate that we have code
// 2) Show the Results tab and a loading state
// 3) POST the code and current config to the backend API
// 4) On success, normalize and render the report
// 5) On failure, show a friendly error in the Results tab
async function analyzeCode() {
  if (!sourceCode.trim()) return

  isAnalyzing = true
  updateAnalyzeButton()
  switchTab("results")
  showLoadingState()

  try {
    const apiUrl = "http://localhost:5000/api/analyze" // Flask backend endpoint
    const payload = {
      // Python file contents and a filename for the report
      source_code: sourceCode,
      file_name: fileName || "uploaded_file.py",
      config: {
        // Enabled/disabled detectors (from the UI switches)
        smells: { ...config.smells },
        // Thresholds for detectors (from the UI number inputs)
        thresholds: { ...config.thresholds },
      },
    }

    // Send the request to the backend
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })

    let backendReport = null
    try {
      backendReport = await response.json()
    } catch (_) {
      backendReport = null
    }

    if (!response.ok) {
      const msg = backendReport?.error ? `API error ${response.status}: ${backendReport.error}` : `API error ${response.status}`
      throw new Error(msg)
    }

    report = normalizeBackendReport(backendReport) // adapt to UI shape
    displayResults()
  } catch (err) {
    console.error("Analysis failed:", err)
    isAnalyzing = false
    updateAnalyzeButton()
    showAnalysisError(err?.message || "Analysis failed")
    return
  }

  isAnalyzing = false
  updateAnalyzeButton()
}

// Normalize backend report to the shape expected by the UI
// - The backend nests line numbers under a `location` object; the UI expects flat fields
// - This function converts and fills sensible defaults to avoid render errors
function normalizeBackendReport(backendReport) {
  if (!backendReport || typeof backendReport !== "object") return null

  const normalized = {
    metadata: backendReport.metadata || {},
    summary: backendReport.summary || {
      total_smells_detected: 0,
      severity_breakdown: { high: 0, medium: 0, low: 0 },
      smells_by_type: {},
    },
    details: [],
  }

  const details = Array.isArray(backendReport.details) ? backendReport.details : []
  normalized.details = details.map((d) => ({
    smell_type: d.smell_type,
    severity: d.severity,
    message: d.message,
    line_start: d.location?.line_start ?? d.line_start ?? 0,
    line_end: d.location?.line_end ?? d.line_end ?? 0,
    details: d.details || {},
  }))

  return normalized
}

// Show a friendly error message in the Results tab
// - Hides the loading and results sections
// - Shows the "no results" card with the error text
function showAnalysisError(message) {
  const loading = document.getElementById("loading-state")
  const resultsContent = document.getElementById("results-content")
  const noResults = document.getElementById("no-results")

  loading.classList.add("hidden")
  resultsContent.classList.add("hidden")
  noResults.classList.remove("hidden")

  const text = noResults.querySelector(".no-results-text p")
  if (text) {
    text.textContent = `Error: ${message}. Ensure backend is running at http://localhost:5000 and try again.`
  }
}

// Show loading state in the Results tab while waiting for the backend
function showLoadingState() {
  document.getElementById("loading-state").classList.remove("hidden")
  document.getElementById("results-content").classList.add("hidden")
  document.getElementById("no-results").classList.add("hidden")
}


// Display results
function displayResults() {
  document.getElementById("loading-state").classList.add("hidden")
  document.getElementById("no-results").classList.add("hidden")
  document.getElementById("results-content").classList.remove("hidden")

  // Update summary cards
  document.getElementById("total-smells").textContent = report.summary.total_smells_detected
  document.getElementById("high-severity").textContent = report.summary.severity_breakdown.high
  document.getElementById("medium-severity").textContent = report.summary.severity_breakdown.medium
  document.getElementById("low-severity").textContent = report.summary.severity_breakdown.low

  // Update results description
  document.getElementById("results-description").textContent =
    `Detailed analysis results for ${report.metadata.file_path}`

  // Display smell details
  displaySmellDetails()

  // Reinitialize icons
  initializeLucideIcons()
}

// Display smell details
function displaySmellDetails() {
  const smellDetailsContainer = document.getElementById("smell-details")
  smellDetailsContainer.innerHTML = ""

  report.details.forEach((smell, index) => {
    const smellItem = createSmellItem(smell, index)
    smellDetailsContainer.appendChild(smellItem)
  })
}

// Create smell item element
function createSmellItem(smell, index) {
  const smellItem = document.createElement("div")
  smellItem.className = "smell-item"

  const severityIcon = getSeverityIcon(smell.severity)
  const severityBadgeClass = getSeverityBadgeClass(smell.severity)
  const severityClass = getSeverityClass(smell.severity)

  smellItem.innerHTML = `
        <div class="smell-header">
            <div class="smell-info">
                <i data-lucide="${severityIcon}" class="${severityClass}"></i>
                <div>
                    <div class="smell-badges">
                        <span class="badge ${severityBadgeClass}">${smell.smell_type}</span>
                        <span class="badge badge-outline">Lines ${smell.line_start}-${smell.line_end}</span>
                    </div>
                    <p class="smell-message">${smell.message}</p>
                </div>
            </div>
            <span class="badge smell-severity ${severityBadgeClass}">
                ${smell.severity.toUpperCase()}
            </span>
        </div>
        ${smell.details && Object.keys(smell.details).length > 0 ? createSmellDetails(smell.details, 0, smell.smell_type) : ""}
    `

  return smellItem
}

// Create smell details section
function createSmellDetails(details, indent = 0, currentSmellType = null) {
  const indentStyle = `padding-left: ${indent * 1.5}rem;`;

  // Special formatting for DuplicatedCode: show Name, Start Line, End Line, Type first for each block
  if (
    currentSmellType === "DuplicatedCode" &&
    details &&
    (details.block1_name || details.block2_name)
  ) {
    const blockSection = (label, name, start, end, type) => `
      <div class="smell-detail-item" style="${indentStyle}">
        <span class="smell-detail-key">${label}:</span>
        <div class="smell-detail-nested-content">
          <div class="smell-detail-item" style="${indentStyle}">
            <span class="smell-detail-key">Name:</span>
            <span class="smell-detail-value">${String(name ?? "-")}</span>
          </div>
          <div class="smell-detail-item" style="${indentStyle}">
            <span class="smell-detail-key">Start Line:</span>
            <span class="smell-detail-value">${String(start ?? "-")}</span>
          </div>
          <div class="smell-detail-item" style="${indentStyle}">
            <span class="smell-detail-key">End Line:</span>
            <span class="smell-detail-value">${String(end ?? "-")}</span>
          </div>
          <div class="smell-detail-item" style="${indentStyle}">
            <span class="smell-detail-key">Type:</span>
            <span class="smell-detail-value">${String(type ?? "-")}</span>
          </div>
        </div>
      </div>`;

    const blocksHtml = [
      blockSection(
        "Block 1",
        details.block1_name,
        details.block1_start_line,
        details.block1_end_line,
        details.block1_type
      ),
      blockSection(
        "Block 2",
        details.block2_name,
        details.block2_start_line,
        details.block2_end_line,
        details.block2_type
      ),
    ].join("");

    // Remove the fields we've already shown, then render any remaining metrics below
    const remaining = { ...details };
    [
      "block1_name",
      "block1_start_line",
      "block1_end_line",
      "block1_type",
      "block2_name",
      "block2_start_line",
      "block2_end_line",
      "block2_type",
    ].forEach((k) => delete remaining[k]);

    const restHtml = Object.keys(remaining).length
      ? createSmellDetails(remaining, indent + 1)
      : "";

    if (indent === 0) {
      return `
        <div class="smell-details">
          <p class="smell-details-title">Details:</p>
          <div class="smell-details-grid">
            ${blocksHtml}
            ${restHtml}
          </div>
        </div>`;
    } else {
      return `
        <div class="smell-details-nested">
          ${blocksHtml}
          ${restHtml}
        </div>`;
    }
  }

  let orderedDetailsHtml = [];
  let thresholdsHtml = '';
  const otherDetails = { ...details };

  // Prioritize class_name
  if (otherDetails.class_name) {
    orderedDetailsHtml.push(`
      <div class="smell-detail-item" style="${indentStyle}">
          <span class="smell-detail-key">${formatThresholdKey('class_name')}:</span>
          <span class="smell-detail-value">${String(otherDetails.class_name)}</span>
      </div>
    `);
    delete otherDetails.class_name;
  }

  // Then method_name
  if (otherDetails.method_name) {
    orderedDetailsHtml.push(`
      <div class="smell-detail-item" style="${indentStyle}">
          <span class="smell-detail-key">${formatThresholdKey('method_name')}:</span>
          <span class="smell-detail-value">${String(otherDetails.method_name)}</span>
      </div>
    `);
    delete otherDetails.method_name;
  }

  // Consolidate specific thresholds into the 'thresholds' object if they exist at the top level
  if (otherDetails.complexity_threshold !== undefined) {
    if (!otherDetails.thresholds) otherDetails.thresholds = {};
    otherDetails.thresholds.complexity_threshold = otherDetails.complexity_threshold;
    delete otherDetails.complexity_threshold;
  }
  if (otherDetails.sloc_threshold !== undefined) {
    if (!otherDetails.thresholds) otherDetails.thresholds = {};
    otherDetails.thresholds.sloc_threshold = otherDetails.sloc_threshold;
    delete otherDetails.sloc_threshold;
  }
  if (otherDetails.parameter_count !== undefined && otherDetails.threshold !== undefined) {
    if (!otherDetails.thresholds) otherDetails.thresholds = {};
    otherDetails.thresholds.large_parameter_list_threshold = otherDetails.threshold;
    delete otherDetails.threshold;
  }
  // Consolidate magic number threshold
  if (otherDetails.number !== undefined && otherDetails.threshold !== undefined && currentSmellType === "MagicNumbers") {
    if (!otherDetails.thresholds) otherDetails.thresholds = {};
    otherDetails.thresholds.magic_number_threshold = otherDetails.threshold;
    delete otherDetails.threshold;
  }

  // Handle thresholds separately in a collapsible section
  if (otherDetails.thresholds && typeof otherDetails.thresholds === 'object' && Object.keys(otherDetails.thresholds).length > 0 && !Array.isArray(otherDetails.thresholds)) {
    const innerThresholdDetailsHtml = Object.entries(otherDetails.thresholds)
      .map(([key, value]) => `
        <div class="smell-detail-item" style="padding-left: ${indent + 1 * 1.5}rem;">
            <span class="smell-detail-key">${formatThresholdKey(key)}:</span>
            <span class="smell-detail-value">${String(value)}</span>
        </div>
      `)
      .join('');

    thresholdsHtml = `
      <details class="smell-thresholds-details" style="${indentStyle}">
          <summary class="smell-thresholds-summary">Thresholds</summary>
          <div class="smell-thresholds-content">
              ${innerThresholdDetailsHtml}
          </div>
      </details>
    `;
    delete otherDetails.thresholds;
  }

  // Remaining metrics
  const otherMetricsHtml = Object.entries(otherDetails)
    .map(([key, value]) => {
      let formattedValue = '';
      let isNested = false;
      let formattedKey = '';

      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        formattedValue = createSmellDetails(value, indent + 1);
        isNested = true;
      } else if (Array.isArray(value)) {
        if (value.length > 0 && typeof value[0] === 'object' && value[0] !== null && key === 'locations') {
          formattedValue = value.map(item => {
            const line = item.line ? `${item.line}` : '';
            if (line) return line;
            return '[Unknown Line]';
          }).join(', ');
          formattedKey = formatThresholdKey(key) + ' (Line Number)'; // Modify key for display
        } else {
          formattedValue = value.map(item => String(item)).join(', ');
          formattedKey = formatThresholdKey(key);
        }
      } else {
        if (key === 'locality_of_attribute_accesses' && typeof value === 'number') {
          formattedValue = value.toFixed(3);
        } else {
          formattedValue = String(value);
        }
        formattedKey = formatThresholdKey(key);
      }

      return `
        <div class="smell-detail-item" style="${indentStyle}">
            <span class="smell-detail-key">${formattedKey}:</span>
            ${isNested ? `<div class="smell-detail-nested-content">${formattedValue}</div>` : `<span class="smell-detail-value">${formattedValue}</span>`}
        </div>
      `;
    })
    .join('');

  // Combine all parts
  const allDetailsHtml = orderedDetailsHtml.join('') + otherMetricsHtml + thresholdsHtml;

  if (indent === 0) {
    return `
        <div class="smell-details">
            <p class="smell-details-title">Details:</p>
            <div class="smell-details-grid">
                ${allDetailsHtml}
            </div>
        </div>
    `;
  } else {
    return `
        <div class="smell-details-nested">
            ${allDetailsHtml}
        </div>
    `;
  }
}

// Get severity icon
function getSeverityIcon(severity) {
  switch (severity) {
    case "high":
      return "x-circle"
    case "medium":
      return "alert-triangle"
    case "low":
      return "check-circle"
    default:
      return "check-circle"
  }
}

// Get severity badge class
function getSeverityBadgeClass(severity) {
  switch (severity) {
    case "high":
      return "badge-destructive"
    case "medium":
      return "badge-warning"
    case "low":
      return "badge-success"
    default:
      return "badge-secondary"
  }
}

// Get severity class
function getSeverityClass(severity) {
  switch (severity) {
    case "high":
      return "high-severity"
    case "medium":
      return "medium-severity"
    case "low":
      return "low-severity"
    default:
      return ""
  }
}


// Application state
let currentTab = "upload"
let sourceCode = ""
let fileName = ""
let isAnalyzing = false
let report = null
const config = {
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

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  initializeLucideIcons()
  setupEventListeners()
  updateAnalyzeButton()
})

// Initialize Lucide icons
function initializeLucideIcons() {
  const lucide = window.lucide // Declare the lucide variable
  if (typeof lucide !== "undefined") {
    lucide.createIcons()
  }
}

// Setup event listeners
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

// Switch between tabs
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

// Update file info display
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
function updateAnalyzeButton() {
  const analyzeBtn = document.getElementById("analyze-btn")
  const hasCode = sourceCode.trim().length > 0

  analyzeBtn.disabled = !hasCode || isAnalyzing
  analyzeBtn.textContent = isAnalyzing ? "Analyzing..." : "Analyze Code"
}

// Get threshold key from input id
function getThresholdKey(inputId) {
  const mapping = {
    "long-method-sloc": "longMethodSloc",
    "god-class-methods": "godClassMethods",
    "large-param-list": "largeParameterList",
    "magic-numbers": "magicNumberOccurrences",
  }
  return mapping[inputId]
}

// Analyze code
async function analyzeCode() {
  if (!sourceCode.trim()) return

  isAnalyzing = true
  updateAnalyzeButton()
  switchTab("results")
  showLoadingState()

  // Simulate API call delay
  setTimeout(() => {
    // Generate mock report for demo
    report = generateMockReport()
    displayResults()
    isAnalyzing = false
    updateAnalyzeButton()
  }, 2000)
}

// Show loading state
function showLoadingState() {
  document.getElementById("loading-state").classList.remove("hidden")
  document.getElementById("results-content").classList.add("hidden")
  document.getElementById("no-results").classList.add("hidden")
}

// Generate mock report
function generateMockReport() {
  return {
    metadata: {
      file_path: fileName || "uploaded_file.py",
      scan_timestamp: new Date().toISOString(),
      active_smells: Object.keys(config.smells).filter((smell) => config.smells[smell]),
    },
    summary: {
      total_smells_detected: 8,
      severity_breakdown: {
        high: 2,
        medium: 5,
        low: 1,
      },
      smells_by_type: {
        LongMethod: 2,
        GodClass: 1,
        DuplicatedCode: 2,
        LargeParameterList: 1,
        MagicNumbers: 1,
        FeatureEnvy: 1,
      },
    },
    details: [
      {
        smell_type: "LongMethod",
        severity: "high",
        message: "Method 'process_customer_order_with_complex_calculations' is too long (SLOC: 135, Complexity: 18)",
        line_start: 45,
        line_end: 180,
        details: {
          method_name: "process_customer_order_with_complex_calculations",
          sloc: 135,
          cyclomatic_complexity: 18,
        },
      },
      {
        smell_type: "GodClass",
        severity: "high",
        message: "Class 'BookstoreManager' has too many responsibilities (Methods: 25, Fields: 18, Coupling: 12)",
        line_start: 10,
        line_end: 280,
        details: {
          class_name: "BookstoreManager",
          method_count: 25,
          field_count: 18,
          coupling: 12,
        },
      },
      {
        smell_type: "DuplicatedCode",
        severity: "medium",
        message:
          "Duplicated code detected between 'validate_book_availability' and 'process_customer_order' (similarity: 85%)",
        line_start: 60,
        line_end: 194,
        details: { similarity: 0.85 },
      },
      {
        smell_type: "LargeParameterList",
        severity: "medium",
        message: "Method 'add_book_to_inventory' has too many parameters (8)",
        line_start: 25,
        line_end: 25,
        details: {
          method_name: "add_book_to_inventory",
          parameter_count: 8,
        },
      },
      {
        smell_type: "MagicNumbers",
        severity: "medium",
        message: "Magic number 0.9 appears 5 times",
        line_start: 85,
        line_end: 240,
        details: { number: 0.9, occurrences: 5 },
      },
      {
        smell_type: "FeatureEnvy",
        severity: "medium",
        message: "Method 'verify_large_transaction' shows feature envy (foreign: 12, self: 3)",
        line_start: 212,
        line_end: 250,
        details: {
          method_name: "verify_large_transaction",
          foreign_accesses: 12,
          self_accesses: 3,
        },
      },
    ],
  }
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
        ${smell.details && Object.keys(smell.details).length > 0 ? createSmellDetails(smell.details) : ""}
    `

  return smellItem
}

// Create smell details section
function createSmellDetails(details) {
  const detailItems = Object.entries(details)
    .map(
      ([key, value]) => `
        <div class="smell-detail-item">
            <span class="smell-detail-key">${key}:</span>
            <span class="smell-detail-value">${String(value)}</span>
        </div>
    `,
    )
    .join("")

  return `
        <div class="smell-details">
            <p class="smell-details-title">Details:</p>
            <div class="smell-details-grid">
                ${detailItems}
            </div>
        </div>
    `
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

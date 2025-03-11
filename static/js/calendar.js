document.addEventListener("DOMContentLoaded", () => {
  // Canvas elements
  const calendarCanvas = document.getElementById("calendar-canvas")
  const timeSlotsCanvas = document.getElementById("time-slots-canvas")

  // Get canvas contexts
  const calendarCtx = calendarCanvas.getContext("2d")
  const timeSlotsCtx = timeSlotsCanvas.getContext("2d")

  // Other elements
  const currentMonthYearEl = document.getElementById("current-month-year")
  const prevMonthBtn = document.getElementById("prev-month")
  const nextMonthBtn = document.getElementById("next-month")
  const timeSlotsContainer = document.getElementById("time-slots-container")
  const selectedDateDisplay = document.getElementById("selected-date-display")
  const appointmentFormContainer = document.getElementById("appointment-form-container")
  const appointmentForm = document.getElementById("appointment-form")
  const backToCalendarBtn = document.getElementById("back-to-calendar")
  const confirmationContainer = document.getElementById("confirmation-container")
  const newAppointmentBtn = document.getElementById("new-appointment")

  // Summary elements
  const summaryDate = document.getElementById("summary-date")
  const summaryTime = document.getElementById("summary-time")

  // Confirmation elements
  const confDate = document.getElementById("conf-date")
  const confTime = document.getElementById("conf-time")
  const confSubject = document.getElementById("conf-subject")
  const confEmail = document.getElementById("conf-email")

  // State
  const currentDate = new Date()
  let selectedDate = null
  let selectedTimeSlot = null
  let calendarDays = []
  let timeSlots = []
  let hoveredDayIndex = -1
  let hoveredTimeSlotIndex = -1

  // Colors (matching the CSS variables)
  const colors = {
    background: "#1a0533",
    foreground: "#ffeb5b",
    secondary: "#f9a8c9",
    mauve: "#c4b5fd",
    cardBg: "rgba(61, 18, 103, 0.7)",
    border: "rgba(249, 168, 201, 0.1)",
    borderHover: "rgba(249, 168, 201, 0.3)",
    textColor: "#ffffff",
    textLight: "#c4b5fd",
    success: "#10b981",
    error: "#ef4444",
  }

  // Month names
  const monthNames = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
  ]

  // Day names
  const dayNames = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

  // Initialize
  initCanvases()
  renderCalendar()

  // Event listeners
  prevMonthBtn.addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() - 1)
    renderCalendar()
  })

  nextMonthBtn.addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() + 1)
    renderCalendar()
  })

  calendarCanvas.addEventListener("mousemove", handleCalendarMouseMove)
  calendarCanvas.addEventListener("click", handleCalendarClick)
  calendarCanvas.addEventListener("mouseout", () => {
    hoveredDayIndex = -1
    renderCalendarDays()
  })

  timeSlotsCanvas.addEventListener("mousemove", handleTimeSlotsMouseMove)
  timeSlotsCanvas.addEventListener("mouseout", () => {
    hoveredTimeSlotIndex = -1
    renderTimeSlots()
  })

  backToCalendarBtn.addEventListener("click", () => {
    appointmentFormContainer.style.display = "none"
    timeSlotsContainer.style.display = "block"
    selectedTimeSlot = null
  })

  newAppointmentBtn.addEventListener("click", () => {
    resetForm()
    confirmationContainer.style.display = "none"
    renderCalendar()
  })

  appointmentForm.addEventListener("submit", (e) => {
    e.preventDefault()

    // Get form data
    const formData = new FormData(appointmentForm)
    const name = formData.get("name")
    const email = formData.get("email")
    const phone = formData.get("phone")
    const subject = formData.get("subject")
    const message = formData.get("message")

    // Update confirmation details
    confDate.textContent = formatDate(selectedDate)
    confTime.textContent = selectedTimeSlot
    confEmail.textContent = email

    // Get subject text
    const subjectEl = document.getElementById("subject")
    const subjectText = subjectEl.options[subjectEl.selectedIndex].text
    confSubject.textContent = subjectText

    // Show confirmation
    appointmentFormContainer.style.display = "none"
    confirmationContainer.style.display = "block"
  })

  timeSlotsCanvas.addEventListener("click", handleTimeSlotsClick)

  // Functions
  function initCanvases() {
    // Set canvas dimensions based on their container size
    resizeCanvas(calendarCanvas)
    resizeCanvas(timeSlotsCanvas)

    // Handle window resize
    window.addEventListener("resize", () => {
      resizeCanvas(calendarCanvas)
      resizeCanvas(timeSlotsCanvas)
      renderCalendarDays()
      if (timeSlotsContainer.style.display === "block") {
        renderTimeSlots()
      }
    })
  }

  function resizeCanvas(canvas) {
    // Get the display size of the canvas
    const rect = canvas.parentNode.getBoundingClientRect()

    // Set the canvas size to match its container
    canvas.width = rect.width
    canvas.height = rect.height

    // Set the device pixel ratio for sharper rendering
    const dpr = window.devicePixelRatio || 1
    const rect2 = canvas.getBoundingClientRect()
    canvas.width = rect2.width * dpr
    canvas.height = rect2.height * dpr

    const ctx = canvas.getContext("2d")
    ctx.scale(dpr, dpr)

    // Set the CSS size
    canvas.style.width = `${rect2.width}px`
    canvas.style.height = `${rect2.height}px`
  }

  function renderCalendar() {
    // Update current month and year display
    currentMonthYearEl.textContent = `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`

    // Calculate calendar days
    calculateCalendarDays()

    // Render the calendar
    renderCalendarDays()

    // Hide time slots and form
    timeSlotsContainer.style.display = "none"
    appointmentFormContainer.style.display = "none"
    confirmationContainer.style.display = "none"
  }

  function calculateCalendarDays() {
    calendarDays = []

    // Get first day of month
    const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)

    // Get last day of month
    const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0)

    // Get day of week of first day (0 = Sunday, 1 = Monday, etc.)
    let firstDayOfWeek = firstDayOfMonth.getDay()
    // Adjust for Monday as first day of week
    firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1

    // Get number of days in month
    const daysInMonth = lastDayOfMonth.getDate()

    // Get number of days from previous month to display
    const daysFromPrevMonth = firstDayOfWeek

    // Get last day of previous month
    const lastDayOfPrevMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 0).getDate()

    // Get today's date
    const today = new Date()

    // Add days from previous month
    for (let i = daysFromPrevMonth - 1; i >= 0; i--) {
      calendarDays.push({
        day: lastDayOfPrevMonth - i,
        month: "prev",
        date: new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, lastDayOfPrevMonth - i),
        disabled: true,
      })
    }

    // Add days of current month
    for (let i = 1; i <= daysInMonth; i++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), i)
      const isPast = date < new Date(today.getFullYear(), today.getMonth(), today.getDate())

      calendarDays.push({
        day: i,
        month: "current",
        date: date,
        isToday:
          currentDate.getFullYear() === today.getFullYear() &&
          currentDate.getMonth() === today.getMonth() &&
          i === today.getDate(),
        disabled: isPast,
      })
    }

    // Calculate days needed from next month
    const totalDaysDisplayed = daysFromPrevMonth + daysInMonth
    const daysFromNextMonth = 42 - totalDaysDisplayed // 6 rows of 7 days

    // Add days from next month
    for (let i = 1; i <= daysFromNextMonth; i++) {
      calendarDays.push({
        day: i,
        month: "next",
        date: new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, i),
        disabled: true,
      })
    }
  }

  function renderCalendarDays() {
    const ctx = calendarCtx
    const width = calendarCanvas.width / window.devicePixelRatio
    const height = calendarCanvas.height / window.devicePixelRatio

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    // Calculate grid dimensions
    const rows = 7 // 1 row for day names + 6 rows for days
    const cols = 7
    const cellWidth = width / cols
    const cellHeight = height / rows

    // Draw day names
    ctx.fillStyle = colors.mauve
    ctx.font = "14px Arial, sans-serif"
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"

    for (let i = 0; i < dayNames.length; i++) {
      ctx.fillText(dayNames[i], (i + 0.5) * cellWidth, cellHeight / 2)
    }

    // Draw days
    for (let i = 0; i < calendarDays.length; i++) {
      const day = calendarDays[i]
      const row = Math.floor(i / 7) + 1 // +1 because first row is day names
      const col = i % 7
      const x = col * cellWidth
      const y = row * cellHeight

      // Calculate cell center
      const centerX = x + cellWidth / 2
      const centerY = y + cellHeight / 2

      // Draw cell background
      ctx.beginPath()
      ctx.roundRect(x + 4, y + 4, cellWidth - 8, cellHeight - 8, 8)

      if (i === hoveredDayIndex && !day.disabled) {
        // Hovered state
        ctx.fillStyle = "rgba(249, 168, 201, 0.25)"
      } else if (day.month !== "current") {
        // Previous or next month
        ctx.fillStyle = "rgba(61, 18, 103, 0.3)"
      } else if (day.disabled) {
        // Disabled day
        ctx.fillStyle = "rgba(61, 18, 103, 0.5)"
      } else if (selectedDate && day.date.toDateString() === selectedDate.toDateString()) {
        // Selected day
        ctx.fillStyle = "rgba(249, 168, 201, 0.5)"
      } else {
        // Normal day
        ctx.fillStyle = "rgba(61, 18, 103, 0.7)"
      }

      ctx.fill()

      // Draw day number
      if (day.month !== "current") {
        ctx.fillStyle = "rgba(196, 181, 253, 0.5)"
      } else if (day.disabled) {
        ctx.fillStyle = "rgba(196, 181, 253, 0.5)"
      } else if (day.isToday) {
        ctx.fillStyle = colors.foreground
      } else {
        ctx.fillStyle = colors.textColor
      }

      ctx.font = day.isToday ? "bold 16px Arial, sans-serif" : "16px Arial, sans-serif"
      ctx.fillText(day.day.toString(), centerX, centerY)

      // Draw today indicator
      if (day.isToday) {
        ctx.beginPath()
        ctx.arc(centerX, centerY + 15, 3, 0, Math.PI * 2)
        ctx.fillStyle = colors.foreground
        ctx.fill()
      }

      // Draw border for selected date
      if (selectedDate && day.date.toDateString() === selectedDate.toDateString()) {
        ctx.beginPath()
        ctx.roundRect(x + 4, y + 4, cellWidth - 8, cellHeight - 8, 8)
        ctx.strokeStyle = colors.secondary
        ctx.lineWidth = 2
        ctx.stroke()
      }
    }
  }

  function handleCalendarMouseMove(e) {
    const rect = calendarCanvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const width = calendarCanvas.width / window.devicePixelRatio
    const height = calendarCanvas.height / window.devicePixelRatio

    const cols = 7
    const rows = 7
    const cellWidth = width / cols
    const cellHeight = height / rows

    // Skip the first row (day names)
    if (y < cellHeight) {
      hoveredDayIndex = -1
      renderCalendarDays()
      return
    }

    const col = Math.floor(x / cellWidth)
    const row = Math.floor(y / cellHeight)

    // Calculate the index in the calendarDays array
    const index = (row - 1) * 7 + col

    if (index >= 0 && index < calendarDays.length && !calendarDays[index].disabled) {
      if (hoveredDayIndex !== index) {
        hoveredDayIndex = index
        renderCalendarDays()
        calendarCanvas.style.cursor = "pointer"
      }
    } else {
      if (hoveredDayIndex !== -1) {
        hoveredDayIndex = -1
        renderCalendarDays()
        calendarCanvas.style.cursor = "default"
      }
    }
  }

  function handleCalendarClick(e) {
    if (hoveredDayIndex >= 0 && hoveredDayIndex < calendarDays.length) {
      const day = calendarDays[hoveredDayIndex]
      if (!day.disabled) {
        selectedDate = day.date
        renderCalendarDays()
        showTimeSlots(selectedDate)
      }
    }
  }

  function showTimeSlots(date) {
    // Update selected date display
    selectedDateDisplay.textContent = formatDate(date)

    // Generate time slots (9:00 AM to 5:00 PM)
    timeSlots = [
      { time: "09:00", disabled: false },
      { time: "10:00", disabled: false },
      { time: "11:00", disabled: false },
      { time: "12:00", disabled: false },
      { time: "14:00", disabled: false },
      { time: "15:00", disabled: false },
      { time: "16:00", disabled: false },
      { time: "17:00", disabled: false },
    ]

    // Render time slots
    renderTimeSlots()

    // Show time slots container and hide others
    timeSlotsContainer.style.display = "block"
    appointmentFormContainer.style.display = "none"
    confirmationContainer.style.display = "none"
  }

  function renderTimeSlots() {
    const ctx = timeSlotsCtx
    const width = timeSlotsCanvas.width / window.devicePixelRatio
    const height = timeSlotsCanvas.height / window.devicePixelRatio

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    // Calculate grid dimensions
    const cols = 4 // 4 time slots per row
    const rows = Math.ceil(timeSlots.length / cols)
    const cellWidth = width / cols
    const cellHeight = height / rows

    // Draw time slots
    for (let i = 0; i < timeSlots.length; i++) {
      const timeSlot = timeSlots[i]
      const row = Math.floor(i / cols)
      const col = i % cols
      const x = col * cellWidth
      const y = row * cellHeight

      // Calculate cell center
      const centerX = x + cellWidth / 2
      const centerY = y + cellHeight / 2

      // Draw cell background
      ctx.beginPath()
      ctx.roundRect(x + 8, y + 8, cellWidth - 16, cellHeight - 16, 8)

      if (i === hoveredTimeSlotIndex && !timeSlot.disabled) {
        // Hovered state
        ctx.fillStyle = "rgba(249, 168, 201, 0.25)"
      } else if (timeSlot.disabled) {
        // Disabled time slot
        ctx.fillStyle = "rgba(61, 18, 103, 0.5)"
      } else if (selectedTimeSlot === timeSlot.time) {
        // Selected time slot
        ctx.fillStyle = "rgba(249, 168, 201, 0.5)"
      } else {
        // Normal time slot
        ctx.fillStyle = "rgba(61, 18, 103, 0.7)"
      }

      ctx.fill()

      // Draw time text
      if (timeSlot.disabled) {
        ctx.fillStyle = "rgba(196, 181, 253, 0.5)"
      } else {
        ctx.fillStyle = colors.textColor
      }

      ctx.font = "16px Arial, sans-serif"
      ctx.textAlign = "center"
      ctx.textBaseline = "middle"
      ctx.fillText(timeSlot.time, centerX, centerY)

      // Draw border for selected time slot
      if (selectedTimeSlot === timeSlot.time) {
        ctx.beginPath()
        ctx.roundRect(x + 8, y + 8, cellWidth - 16, cellHeight - 16, 8)
        ctx.strokeStyle = colors.secondary
        ctx.lineWidth = 2
        ctx.stroke()
      }
    }
  }

  function handleTimeSlotsMouseMove(e) {
    const rect = timeSlotsCanvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const width = timeSlotsCanvas.width / window.devicePixelRatio
    const height = timeSlotsCanvas.height / window.devicePixelRatio

    const cols = 4
    const rows = Math.ceil(timeSlots.length / cols)
    const cellWidth = width / cols
    const cellHeight = height / rows

    const col = Math.floor(x / cellWidth)
    const row = Math.floor(y / cellHeight)

    // Calculate the index in the timeSlots array
    const index = row * cols + col

    if (index >= 0 && index < timeSlots.length && !timeSlots[index].disabled) {
      if (hoveredTimeSlotIndex !== index) {
        hoveredTimeSlotIndex = index
        renderTimeSlots()
        timeSlotsCanvas.style.cursor = "pointer"
      }
    } else {
      if (hoveredTimeSlotIndex !== -1) {
        hoveredTimeSlotIndex = -1
        renderTimeSlots()
        timeSlotsCanvas.style.cursor = "default"
      }
    }
  }

  function handleTimeSlotsClick(e) {
    const rect = timeSlotsCanvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const width = timeSlotsCanvas.width / window.devicePixelRatio
    const height = timeSlotsCanvas.height / window.devicePixelRatio

    const cols = 4
    const rows = Math.ceil(timeSlots.length / cols)
    const cellWidth = width / cols
    const cellHeight = height / rows

    const col = Math.floor(x / cellWidth)
    const row = Math.floor(y / cellHeight)

    // Calculate the index in the timeSlots array
    const index = row * cols + col

    if (index >= 0 && index < timeSlots.length && !timeSlots[index].disabled) {
      const timeSlot = timeSlots[index]
      selectedTimeSlot = timeSlot.time
      renderTimeSlots()

      // Update summary
      summaryDate.textContent = formatDate(selectedDate)
      summaryTime.textContent = timeSlot.time

      // Show appointment form
      timeSlotsContainer.style.display = "none"
      appointmentFormContainer.style.display = "block"
    }
  }

  function formatDate(date) {
    if (!date) return ""

    const day = date.getDate()
    const month = monthNames[date.getMonth()]
    const year = date.getFullYear()

    return `${day} ${month} ${year}`
  }

  function resetForm() {
    // Reset form fields
    appointmentForm.reset()

    // Reset selected date and time
    selectedDate = null
    selectedTimeSlot = null

    // Reset summary
    summaryDate.textContent = "--"
    summaryTime.textContent = "--"
  }
})


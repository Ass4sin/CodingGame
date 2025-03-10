document.addEventListener("DOMContentLoaded", () => {
  // Mobile menu toggle
  const mobileMenuBtn = document.querySelector(".mobile-menu-btn")
  const mainNav = document.querySelector(".main-nav")

  if (mobileMenuBtn && mainNav) {
    mobileMenuBtn.addEventListener("click", () => {
      mainNav.style.display = mainNav.style.display === "flex" ? "none" : "flex"
    })
  }

  // Add current year to footer copyright
  const copyrightYear = document.querySelector(".copyright p")
  if (copyrightYear) {
    const year = new Date().getFullYear()
    copyrightYear.textContent = copyrightYear.textContent.replace("{{ now.year }}", year)
  }

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const targetId = this.getAttribute("href")
      if (targetId === "#") return

      const targetElement = document.querySelector(targetId)
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: "smooth",
        })
      }
    })
  })
})


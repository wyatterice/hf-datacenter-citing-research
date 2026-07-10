// Bottom-right hamburger nav with scroll-spy and a scroll-progress bar.
// Reuses the CIR floating-nav.css; trimmed to this tool's sections (no search,
// account, or assistant).

import { useEffect, useRef, useState, type MouseEvent as ReactMouseEvent } from 'react'

interface NavItem {
  id: string
  label: string
}

const NAV_ITEMS: NavItem[] = [
  { id: 'scores', label: 'Scores' },
  { id: 'demand', label: 'Demand' },
  { id: 'economics', label: 'Economics' },
  { id: 'tax', label: 'Tax' },
]

export function FloatingNav() {
  const [isOpen, setIsOpen] = useState(false)
  const [activeSection, setActiveSection] = useState(NAV_ITEMS[0].id)
  const navRef = useRef<HTMLDivElement>(null)
  const progressBarRef = useRef<HTMLDivElement>(null)

  // Scroll-progress bar; write height via ref to avoid a re-render per frame.
  useEffect(() => {
    let frame: number | null = null
    const write = () => {
      frame = null
      const max = document.documentElement.scrollHeight - window.innerHeight
      const pct = max > 0 ? Math.min((window.scrollY / max) * 100, 100) : 0
      if (progressBarRef.current) progressBarRef.current.style.height = `${pct}%`
    }
    const onScroll = () => {
      if (frame === null) frame = requestAnimationFrame(write)
    }
    write()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      if (frame !== null) cancelAnimationFrame(frame)
    }
  }, [])

  // Scroll-spy: mark the first in-view section active.
  useEffect(() => {
    const ids = NAV_ITEMS.map((i) => i.id)
    const inView = new Set<string>()
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) inView.add(entry.target.id)
          else inView.delete(entry.target.id)
        }
        const first = ids.find((id) => inView.has(id))
        if (first) setActiveSection((prev) => (prev === first ? prev : first))
      },
      { rootMargin: '-200px 0px -60% 0px', threshold: 0 },
    )
    ids.forEach((id) => {
      const el = document.getElementById(id)
      if (el) io.observe(el)
    })
    return () => io.disconnect()
  }, [])

  // Click outside to close.
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (isOpen && navRef.current && !navRef.current.contains(e.target as Node)) setIsOpen(false)
    }
    document.addEventListener('click', handler)
    return () => document.removeEventListener('click', handler)
  }, [isOpen])

  const handleNavClick = (e: ReactMouseEvent, id: string) => {
    e.preventDefault()
    const el = document.getElementById(id)
    if (el) {
      const header = el.querySelector('.metrics-section-header') ?? el
      header.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setTimeout(() => setIsOpen(false), 300)
    }
  }

  return (
    <nav ref={navRef} className={`floating-nav ${isOpen ? 'active' : ''}`}>
      <div className="nav-progress">
        <div ref={progressBarRef} className="nav-progress-bar" style={{ height: '0%' }} />
      </div>

      <div className="nav-items">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
            onClick={(e) => handleNavClick(e, item.id)}
            data-section={item.id}
          >
            {item.label}
          </button>
        ))}
      </div>

      <button
        type="button"
        className="nav-toggle"
        onClick={() => setIsOpen((o) => !o)}
        aria-label={isOpen ? 'Close navigation menu' : 'Open navigation menu'}
        aria-expanded={isOpen}
      >
        <span className="nav-icon">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>
    </nav>
  )
}

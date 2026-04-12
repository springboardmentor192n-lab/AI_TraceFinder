import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { Sun, Moon, Scan, History, BarChart2, Home } from 'lucide-react'

const navLinks = [
  { href: '/',          label: 'Home',      icon: Home      },
  { href: '/scan',      label: 'Scan',      icon: Scan      },
  { href: '/dashboard', label: 'Dashboard', icon: BarChart2 },
  { href: '/history',   label: 'History',   icon: History   },
]

export default function Navbar() {
  const [dark, setDark] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const saved = localStorage.getItem('theme')
    const isDark = saved !== 'light'
    setDark(isDark)
    document.documentElement.classList.toggle('light', !isDark)
  }, [])

  const toggleTheme = () => {
    const next = !dark
    setDark(next)
    document.documentElement.classList.toggle('light', !next)
    localStorage.setItem('theme', next ? 'dark' : 'light')
  }

  return (
    <>
      <nav className="nb">
        {/* Logo */}
        <Link href="/" className="nb-logo">
          <div className="nb-icon">
            <Scan size={15} color="white" strokeWidth={2.5} />
          </div>
          <span className="nb-wordmark">
            Trace<span className="nb-accent">Finder</span>
          </span>
        </Link>

        {/* Centre links */}
        <div className="nb-links">
          {navLinks.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={`nb-link${router.pathname === href ? ' active' : ''}`}
            >
              <Icon size={14} />
              <span>{label}</span>
            </Link>
          ))}
        </div>

        {/* Theme toggle */}
        <button className="nb-toggle" onClick={toggleTheme} aria-label="Toggle theme">
          {dark ? <Sun size={15} /> : <Moon size={15} />}
        </button>
      </nav>

      <style jsx>{`
        .nb {
          position: sticky;
          top: 0;
          z-index: 100;
          height: 56px;
          display: flex;
          align-items: center;
          padding: 0 28px;
          border-bottom: 1px solid var(--border);
          background: rgba(10, 10, 15, 0.92);
          backdrop-filter: blur(14px);
          -webkit-backdrop-filter: blur(14px);
          gap: 0;
        }

        /* ── Logo ── fixed width, never wraps */
        .nb-logo {
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: 8px;
          text-decoration: none;
          flex-shrink: 0;
          width: 160px;
        }
        .nb-icon {
          width: 28px;
          height: 28px;
          min-width: 28px;
          border-radius: 7px;
          background: var(--accent);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .nb-wordmark {
          font-family: var(--font-display);
          font-size: 16px;
          font-weight: 700;
          color: var(--text-primary);
          letter-spacing: -0.3px;
          white-space: nowrap;
        }
        .nb-accent { color: var(--accent-light); }

        /* ── Centre nav ── takes remaining space, centres itself */
        .nb-links {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 2px;
        }
        .nb-link {
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: 5px;
          padding: 5px 12px;
          border-radius: 7px;
          font-size: 13px;
          font-weight: 500;
          color: var(--text-secondary);
          text-decoration: none;
          white-space: nowrap;
          transition: color 0.15s, background 0.15s;
        }
        .nb-link:hover {
          color: var(--text-primary);
          background: rgba(255, 255, 255, 0.06);
        }
        .nb-link.active {
          color: var(--accent-light);
          background: rgba(99, 102, 241, 0.14);
        }

        /* ── Theme button ── fixed width */
        .nb-toggle {
          flex-shrink: 0;
          width: 36px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: transparent;
          border: 1px solid var(--border);
          border-radius: 7px;
          cursor: pointer;
          color: var(--text-secondary);
          transition: border-color 0.15s, color 0.15s;
        }
        .nb-toggle:hover {
          border-color: var(--border-hover);
          color: var(--text-primary);
        }

        :global(.light) .nb {
          background: rgba(248, 248, 252, 0.94);
        }
      `}</style>
    </>
  )
}
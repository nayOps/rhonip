import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'

type Props = {
  children: React.ReactNode
  userName?: string
  onLogout?: () => void
}

const NavLink: React.FC<{ href: string; label: string; icon?: React.ReactNode }> = ({ href, label, icon }) => {
  const router = useRouter()
  const active = router.pathname.startsWith(href)
  return (
    <Link href={href} className={`group ${active ? 'active' : ''}`}>
      <span className="flex items-center gap-3">
        <span className="text-gray-400 group-hover:text-gray-600">{icon}</span>
        <span>{label}</span>
      </span>
    </Link>
  )
}

const DashboardLayout: React.FC<Props> = ({ children, userName, onLogout }) => {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="h-9 w-9 rounded bg-secondary-500/10 flex items-center justify-center text-secondary-700 font-bold">ON</div>
          <div>
            <div className="text-sm font-semibold">Guichet agents ONIP</div>
            <div className="text-xs text-gray-500">République Démocratique du Congo</div>
          </div>
        </div>
        <nav className="p-3 space-y-1">
          <NavLink href="/dashboard" label="Tableau de bord" />
          <NavLink href="/dashboard/enrollments" label="Identification" />
        </nav>
        <div className="mt-auto p-4 text-xs text-gray-500 hidden md:block">
          © {new Date().getFullYear()} ONIP — Tous droits réservés
        </div>
      </aside>

      <div className="min-h-screen flex flex-col">
        <header className="header">
          <div className="inner">
            <div className="flex items-center gap-3">
              <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-gray-600">Système opérationnel</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <span className="hidden sm:inline text-gray-500">{userName ?? 'Administrateur'}</span>
              {onLogout && (
                <button
                  type="button"
                  onClick={onLogout}
                  className="text-xs px-2 py-1 rounded border border-gray-300 hover:bg-gray-50"
                >
                  Déconnexion
                </button>
              )}
              <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 text-xs font-bold">
                AD
              </div>
            </div>
          </div>
        </header>
        <main className="content">
          {children}
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout

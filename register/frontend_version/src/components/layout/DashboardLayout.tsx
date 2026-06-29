import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'

type Props = {
  children: React.ReactNode
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

const DashboardLayout: React.FC<Props> = ({ children }) => {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="h-9 w-9 rounded bg-secondary-500/10 flex items-center justify-center text-secondary-700 font-bold">FGP</div>
          <div>
            <div className="text-sm font-semibold">FGP | ONIP</div>
            <div className="text-xs text-gray-500">République Démocratique du Congo</div>
          </div>
        </div>
        <nav className="p-3 space-y-1">
          <NavLink href="/dashboard" label="Tableau de bord" />
          <NavLink href="/enrollment" label="Enrôlement" />
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
              <span className="hidden sm:inline text-gray-500">Agent</span>
              <div className="h-8 w-8 rounded-full bg-gray-200" />
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

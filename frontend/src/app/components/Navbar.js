'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navLinks = [
  { label: 'Dashboard', href: '/' },
  { label: 'Gallery', href: '/gallery' },
  { label: 'People', href: '/people' },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav
      className="w-full px-6 py-3 flex items-center justify-between z-50"
      style={{
        position: 'sticky',
        top: 0,
        backgroundColor: 'rgba(10, 10, 15, 0.8)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
      }}
    >
      {/* Brand */}
      <Link href="/" className="flex items-center gap-2 group">
        {/* Face / scan icon */}
        <svg
          className="w-7 h-7 text-indigo-400 group-hover:text-indigo-300 transition-colors duration-300"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          {/* Scan corners */}
          <path d="M3 7V5a2 2 0 0 1 2-2h2" />
          <path d="M17 3h2a2 2 0 0 1 2 2v2" />
          <path d="M21 17v2a2 2 0 0 1-2 2h-2" />
          <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
          {/* Face */}
          <circle cx="9" cy="10" r="1" fill="currentColor" stroke="none" />
          <circle cx="15" cy="10" r="1" fill="currentColor" stroke="none" />
          <path d="M9.5 15a3.5 3.5 0 0 0 5 0" />
        </svg>

        <span
          className="text-xl font-bold tracking-tight"
          style={{
            background: 'linear-gradient(135deg, #818cf8, #a78bfa, #c084fc)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          FaceVault
        </span>
      </Link>

      {/* Nav Links */}
      <div className="flex items-center gap-1">
        {navLinks.map(({ label, href }) => {
          const isActive =
            href === '/' ? pathname === '/' : pathname.startsWith(href);

          return (
            <Link
              key={href}
              href={href}
              className={`
                relative text-sm font-medium px-4 py-2 rounded-lg
                transition-all duration-300 ease-in-out
                ${
                  isActive
                    ? 'text-white bg-indigo-500/15'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                }
              `}
            >
              {label}
              {isActive && (
                <span
                  className="absolute bottom-0 left-1/2 -translate-x-1/2 h-0.5 w-6 rounded-full bg-indigo-500"
                  style={{ boxShadow: '0 0 8px rgba(99, 102, 241, 0.6)' }}
                />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

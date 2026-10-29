'use client'

import { createContext, useContext, useEffect, useSyncExternalStore, ReactNode } from 'react'

interface ThemeContextType {
  isDarkMode: boolean
  toggleDarkMode: () => void
}
const ThemeContext = createContext<ThemeContextType | undefined>(undefined)
function subscribe(callback: () => void) {
  window.addEventListener('storage', callback)
  window.addEventListener('theme-change', callback)
  return () => {
    window.removeEventListener('storage', callback)
    window.removeEventListener('theme-change', callback)
  }
}
const getSnapshot = () => localStorage.getItem('theme') === 'dark'
const getServerSnapshot = () => false

export function ThemeProvider({ children }: { children: ReactNode }) {
  const isDarkMode = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode)
  }, [isDarkMode])
  const toggleDarkMode = () => {
    localStorage.setItem('theme', isDarkMode ? 'light' : 'dark')
    window.dispatchEvent(new Event('theme-change'))
  }
  return <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>{children}</ThemeContext.Provider>
}
export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) throw new Error('useTheme must be used within ThemeProvider')
  return context
}

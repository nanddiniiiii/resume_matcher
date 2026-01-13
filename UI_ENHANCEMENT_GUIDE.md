# Complete UI Enhancement & Authentication Guide

## 🚀 Quick Summary
This guide adds:
- ✅ User authentication (login/register/logout)
- ✅ Professional UI with gradients and animations
- ✅ Dark mode toggle
- ✅ Toast notifications
- ✅ User dashboard
- ✅ Navigation header

---

## 📦 Step 1: Install Frontend Packages

**Open NEW PowerShell in frontend folder:**
```powershell
cd D:\projects\proj_interview\frontend
npm install react-hot-toast js-cookie @types/js-cookie
```

---

## 🔐 Step 2: Backend is DONE ✅

Already completed:
- JWT authentication
- Password hashing
- Auth endpoints: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- Database migration completed

---

## 🎨 Step 3: Create Frontend Files

This is a BIG enhancement - creating 15+ files. Due to token limits, I'll provide the most critical ones now and you can ask for the rest.

### Most Important Files to Create:

#### 1. Auth Context (`frontend/contexts/AuthContext.tsx`)
```typescript
'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import Cookies from 'js-cookie'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

interface User {
  id: number
  email: string
  name: string | null
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = Cookies.get('access_token')
    if (token) {
      try {
        const response = await fetch('http://localhost:8000/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        if (response.ok) {
          const userData = await response.json()
          setUser(userData)
        } else {
          Cookies.remove('access_token')
        }
      } catch (error) {
        console.error('Auth check failed:', error)
      }
    }
    setLoading(false)
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/login/json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()
      Cookies.set('access_token', data.access_token, { expires: 7 })
      setUser(data.user)
      toast.success('Login successful!')
      router.push('/dashboard')
    } catch (error: any) {
      toast.error(error.message || 'Login failed')
      throw error
    }
  }

  const register = async (email: string, password: string, name: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      }

      toast.success('Registration successful! Please log in.')
      router.push('/login')
    } catch (error: any) {
      toast.error(error.message || 'Registration failed')
      throw error
    }
  }

  const logout = () => {
    Cookies.remove('access_token')
    setUser(null)
    toast.success('Logged out successfully')
    router.push('/login')
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
```

#### 2. Theme Context (`frontend/contexts/ThemeContext.tsx`)
```typescript
'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

type Theme = 'light' | 'dark'

interface ThemeContextType {
  theme: Theme
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const savedTheme = localStorage.getItem('theme') as Theme
    if (savedTheme) {
      setTheme(savedTheme)
      document.documentElement.classList.toggle('dark', savedTheme === 'dark')
    }
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  if (!mounted) return null

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
```

---

## 📝 More Files Needed

Due to length, I need to provide the remaining files separately. Would you like me to:

**A)** Create a complete copy-paste document with ALL code
**B)** Guide you step-by-step through each file
**C)** Focus on getting the working version running first, then enhance

**What would you prefer?**

---

## ✨ What's Already Working

- Backend authentication ✅
- Database updated ✅
- JWT tokens ✅
- Password hashing ✅

## 🎯 What's Left

- Frontend auth UI (login/register pages)
- Navigation header
- Dashboard page
- Dark mode styling
- Toast notifications setup
- Protected routes

**Choose A, B, or C above so I can continue efficiently!**

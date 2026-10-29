'use client'

import { API_BASE_URL } from '@/lib/config'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import Cookies from 'js-cookie'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

interface User {
  id: number
  email: string
  name: string | null
  created_at?: string
}

interface AuthContextType {
  token: string | null
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const checkAuth = async () => {
    await Promise.resolve()
    const token = Cookies.get('access_token')
    if (token) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        if (response.ok) {
          const userData = await response.json()
          setUser(userData)
          setToken(token)
        } else {
          Cookies.remove('access_token')
        }
      } catch (error) {
        console.error('Auth check failed:', error)
      }
    }
    setLoading(false)
    }
    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login/json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(typeof error.detail === 'string' ? error.detail : 'Check your email and password')
    }

    const data = await response.json()
    Cookies.set('access_token', data.access_token, { expires: 7, sameSite: 'strict', secure: window.location.protocol === 'https:' })
    setToken(data.access_token)
    setUser(data.user)
    toast.success('Welcome back!')
    router.push('/')
  }

  const register = async (email: string, password: string, name: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ email, password, name })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(typeof error.detail === 'string' ? error.detail : 'Check your email and password requirements')
      }

      // Auto-login after registration
      await login(email, password)
      toast.success('Account created successfully!')
    } catch (error: any) {
      console.error('Registration error:', error)
      throw new Error(error.message || 'Failed to connect to server')
    }
  }

  const logout = () => {
    Cookies.remove('access_token')
    setUser(null)
    setToken(null)
    toast.success('Signed out successfully')
    router.push('/login')
  }

  return (
    <AuthContext.Provider value={{ updateUser: setUser, token, user, loading, login, register, logout, isAuthenticated: !!user }}>
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

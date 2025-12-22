"use client"

import { useState, useCallback } from "react"

export type UserRole = "tutor" | "user"

export interface AuthUser {
  id: string
  name: string
  email: string
  role: UserRole
}

// Mock user data
const mockUsers: Record<UserRole, AuthUser> = {
  tutor: {
    id: "user-tutor-01",
    name: "Tutor User",
    email: "tutor@xlearn.com",
    role: "tutor",
  },
  user: {
    id: "user-regular-02",
    name: "Regular User",
    email: "user@xlearn.com",
    role: "user",
  },
}

/**
 * Mock authentication hook. In a real app, this would be replaced
 * with a proper authentication context provider.
 */
export function useAuth() {
  const [currentUser, setCurrentUser] = useState<AuthUser>(mockUsers.tutor)

  const toggleRole = useCallback(() => {
    setCurrentUser((prevUser) => (prevUser.role === "tutor" ? mockUsers.user : mockUsers.tutor))
  }, [])

  const isTutor = currentUser.role === "tutor"

  return { user: currentUser, isTutor, toggleRole }
}

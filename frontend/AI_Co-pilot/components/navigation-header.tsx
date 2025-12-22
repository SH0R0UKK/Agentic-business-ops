"use client"

import { Button } from "@/components/ui/button"
import { ArrowLeft, Home } from "lucide-react"
import { useRouter, usePathname } from "next/navigation"
import Image from "next/image"

interface NavigationHeaderProps {
  title: string
  subtitle?: string
  showBackButton?: boolean
  showHomeButton?: boolean
}

export function NavigationHeader({
  title,
  subtitle,
  showBackButton = true,
  showHomeButton = true,
}: NavigationHeaderProps) {
  const router = useRouter()
  const pathname = usePathname()

  return (
    <div className="flex items-center justify-between p-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-b border-gray-200 dark:border-gray-700 rounded-lg mb-6">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <Image src="/images/xlearn-logo.png" alt="XLEARN" width={40} height={40} className="rounded-lg shadow-sm" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{title}</h1>
            {subtitle && <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{subtitle}</p>}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {showHomeButton && pathname !== "/" && (
          <Button variant="outline" size="sm" onClick={() => router.push("/")} className="flex items-center gap-2">
            <Home className="h-4 w-4" />
            Dashboard
          </Button>
        )}
        {showBackButton && (
          <Button variant="outline" size="sm" onClick={() => router.back()} className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
        )}
      </div>
    </div>
  )
}

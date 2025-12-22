"use client"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import type { ThemeProviderProps } from "next-themes"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return (
    <NextThemesProvider
      {...props}
      themes={["light", "dark"]}
      defaultTheme="light"
      enableSystem={true}
      attribute="class"
      storageKey="tutor-dashboard-theme"
    >
      {children}
    </NextThemesProvider>
  )
}

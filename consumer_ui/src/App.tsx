import { BrowserRouter, Routes, Route, Navigate, useLocation, useParams } from "react-router-dom"
import { Layout } from "@/components/layout"
import { HelpPage } from "@/pages/help"
import { EducationPage } from "@/pages/education"
import { InsightsPage } from "@/pages/insights"
import { TransactionsPage } from "@/pages/transactions"
import { OffersPage } from "@/pages/offers"
import { DashboardPage } from "@/pages/dashboard"
import { ProfilePage } from "@/pages/profile"
import { LoginPage } from "@/pages/login"
import { SettingsPage } from "@/pages/settings"
import { ChatWidget } from "@/components/chat-widget"
import { ChatProvider } from "@/contexts/chat-context"
import { AuthProvider } from "@/contexts/auth-context"
import { ProtectedRoute } from "@/components/protected-route"
import { DEFAULT_USER_ID, getValidUserId } from "@/lib/utils"

function ChatWidgetWrapper() {
  const { userId } = useParams<{ userId: string }>()
  const validUserId = getValidUserId(userId)
  
  return <ChatWidget userId={validUserId} />
}

function AppContent() {
  const { userId } = useParams<{ userId: string }>()
  const validUserId = getValidUserId(userId)
  
  return (
    <ChatProvider userId={validUserId}>
      <div className="min-h-screen bg-background">
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="help" element={<HelpPage />} />
            <Route path="education" element={<EducationPage />} />
            <Route path="transactions" element={<TransactionsPage />} />
            <Route path="offers" element={<OffersPage />} />
            <Route path="insights" element={<InsightsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Routes>
        </Layout>
        <ChatWidgetWrapper />
      </div>
    </ChatProvider>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/:userId/*" element={
            <ProtectedRoute>
              <AppContent />
            </ProtectedRoute>
          } />
          <Route path="/" element={<Navigate to={`/${DEFAULT_USER_ID}/dashboard`} replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App

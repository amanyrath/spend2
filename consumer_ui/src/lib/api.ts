const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export interface Account {
  id: string
  name: string
  type: string
  balance: number
  last_four?: string
  mask?: string
  subtype?: string
  account_id?: string
  limit?: number
  utilization?: number
  available?: number
}

export interface Transaction {
  id: string
  date: string
  merchant: string
  amount: number
  category: string
  account_id: string
  transaction_id?: string
  merchant_name?: string
  pending?: boolean
  authorized_date?: string
  payment_channel?: string
  location_city?: string
  location_region?: string
  location_address?: string
  location_postal_code?: string
  location_country?: string
  location_lat?: number
  location_lon?: number
  account_mask?: string
  iso_currency_code?: string
}

export interface EducationContent {
  id: string
  title: string
  description: string
  rationale: string
  category: string
}

export interface Recommendation {
  id: string
  title: string
  description: string
  rationale: string
  category: string
  type: string
}

export interface ProductOffer {
  id: string
  title: string
  description: string
  rationale: string
  partner: string
  eligibility: string
  type: string
}

export interface UserProfile {
  id: string
  email: string
  full_name: string
  persona: string
}

export interface InsightsData {
  spending_by_category: Array<{ category: string; amount: number }>
  utilization_trend: Array<{ date: string; utilization: number }>
  subscriptions: Array<{ merchant: string; amount: number }>
}

export interface OverviewData {
  accounts: Account[]
  total_balance: number
  total_available: number
}

export interface MissionData {
  missions: Array<{
    id: string
    title: string
    description: string
    progress: number
    completed: boolean
  }>
}

export interface AccountsResponse {
  accounts: Account[]
}

async function fetchAPI(endpoint: string, options?: RequestInit) {
  const token = localStorage.getItem('authToken')
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }

  return response.json()
}

export const api = {
  getUserProfile: () => fetchAPI('/users/me/profile'),
  getAccounts: () => fetchAPI('/users/me/accounts'),
  getTransactions: (filters?: any) => fetchAPI('/users/me/transactions', {
    method: 'POST',
    body: JSON.stringify(filters || {}),
  }),
  getInsights: () => fetchAPI('/users/me/insights'),
  getRecommendations: () => fetchAPI('/users/me/recommendations'),
  getEducation: () => fetchAPI('/users/me/education'),
  getOffers: () => fetchAPI('/users/me/offers'),
  chat: (message: string) => fetchAPI('/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  }),
  grantConsent: () => fetchAPI('/users/me/consent', { method: 'POST' }),
}

// Individual API functions
export const fetchTransactions = async (userId: string, filters?: any): Promise<Transaction[]> => {
  return fetchAPI(`/users/${userId}/transactions`, {
    method: 'POST',
    body: JSON.stringify(filters || {}),
  })
}

export const sendChatMessage = async (userId: string, message: string) => {
  return fetchAPI(`/users/${userId}/chat`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export const getConsentStatus = async (userId: string) => {
  return fetchAPI(`/users/${userId}/consent`)
}

export const grantConsent = async (userId: string) => {
  return fetchAPI(`/users/${userId}/consent`, { method: 'POST' })
}

export const revokeConsent = async (userId: string) => {
  return fetchAPI(`/users/${userId}/consent`, { method: 'DELETE' })
}

export const fetchRecommendations = async (userId: string): Promise<Recommendation[]> => {
  return fetchAPI(`/users/${userId}/recommendations`)
}

export const fetchCreditOffers = async (userId: string): Promise<ProductOffer[]> => {
  return fetchAPI(`/users/${userId}/offers`)
}

export const fetchInsights = async (userId: string): Promise<InsightsData> => {
  return fetchAPI(`/users/${userId}/insights`)
}

export const fetchMissionData = async (userId: string): Promise<MissionData> => {
  return fetchAPI(`/users/${userId}/missions`)
}

export const fetchOverview = async (userId: string): Promise<OverviewData> => {
  return fetchAPI(`/users/${userId}/overview`)
}

export const fetchAccountDetails = async (userId: string, accountId?: string): Promise<AccountsResponse> => {
  const endpoint = accountId ? `/users/${userId}/accounts/${accountId}` : `/users/${userId}/accounts`
  return fetchAPI(endpoint)
}

export const fetchAccountTransactions = async (userId: string, accountId: string): Promise<Transaction[]> => {
  return fetchAPI(`/users/${userId}/accounts/${accountId}/transactions`)
}

export const fetchUser = async (userId: string): Promise<UserProfile> => {
  return fetchAPI(`/users/${userId}`)
}

export interface BalanceTransferCalculation {
  current_interest: number
  projected_interest: number
  savings: number
}

export interface BudgetBreakdown {
  categories: Array<{ category: string; amount: number; percentage: number }>
  total: number
}

export interface SubscriptionSavingsCalculation {
  subscriptions: Array<{ name: string; amount: number; frequency: string }>
  total_monthly: number
  potential_savings: number
}

export interface SavingsGoalCalculation {
  current_savings: number
  goal_amount: number
  monthly_contribution: number
  months_to_goal: number
}

export const fetchSignals = async (userId: string) => {
  return fetchAPI(`/users/${userId}/signals`)
}

export const calculateBalanceTransfer = async (userId: string, amount: number): Promise<BalanceTransferCalculation> => {
  return fetchAPI(`/users/${userId}/calculate/balance-transfer`, {
    method: 'POST',
    body: JSON.stringify({ amount }),
  })
}

export const trackModuleInteraction = async (userId: string, module: string, action: string) => {
  return fetchAPI(`/users/${userId}/interactions`, {
    method: 'POST',
    body: JSON.stringify({ module, action }),
  })
}

export const fetchBudgetBreakdown = async (userId: string): Promise<BudgetBreakdown> => {
  return fetchAPI(`/users/${userId}/budget-breakdown`)
}

export const calculateSubscriptionSavings = async (userId: string): Promise<SubscriptionSavingsCalculation> => {
  return fetchAPI(`/users/${userId}/calculate/subscription-savings`)
}

export const calculateSavingsGoal = async (userId: string, goalAmount: number, monthlyContribution: number): Promise<SavingsGoalCalculation> => {
  return fetchAPI(`/users/${userId}/calculate/savings-goal`, {
    method: 'POST',
    body: JSON.stringify({ goalAmount, monthlyContribution }),
  })
}

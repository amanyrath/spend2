/**
 * API client utilities for SpendSense.
 * Provides functions to interact with the FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Fetch user profile data
 */
export async function fetchUserProfile(userId: string) {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/profile`)
  if (!response.ok) {
    throw new Error(`Failed to fetch user profile: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch user accounts
 */
export async function fetchUserAccounts(userId: string) {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/accounts`)
  if (!response.ok) {
    throw new Error(`Failed to fetch accounts: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch user transactions
 */
export async function fetchUserTransactions(
  userId: string,
  options?: {
    limit?: number
    offset?: number
    category?: string
    date_from?: string
    date_to?: string
  }
) {
  const params = new URLSearchParams()
  if (options?.limit) params.append('limit', options.limit.toString())
  if (options?.offset) params.append('offset', options.offset.toString())
  if (options?.category) params.append('category', options.category)
  if (options?.date_from) params.append('date_from', options.date_from)
  if (options?.date_to) params.append('date_to', options.date_to)

  const url = `${API_BASE_URL}/api/users/${userId}/transactions?${params.toString()}`
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(`Failed to fetch transactions: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch user insights (computed features)
 */
export async function fetchUserInsights(userId: string, timeWindow: string = '30d') {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/insights?time_window=${timeWindow}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch insights: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch user recommendations
 */
export async function fetchUserRecommendations(userId: string, timeWindow: string = '30d') {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/recommendations?time_window=${timeWindow}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch recommendations: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Update user consent
 */
export async function updateUserConsent(userId: string, granted: boolean) {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/consent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId, granted }),
  })

  if (!response.ok) {
    throw new Error(`Failed to update consent: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Send chat message
 */
export async function sendChatMessage(userId: string, message: string, transactionWindowDays: number = 30) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      message,
      transaction_window_days: transactionWindowDays,
    }),
  })

  if (!response.ok) {
    throw new Error(`Failed to send chat message: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch all users (operator endpoint)
 */
export async function fetchAllUsers() {
  const response = await fetch(`${API_BASE_URL}/api/operator/users`)
  if (!response.ok) {
    throw new Error(`Failed to fetch users: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch user detail (operator endpoint)
 */
export async function fetchUserDetail(userId: string) {
  const response = await fetch(`${API_BASE_URL}/api/operator/users/${userId}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch user detail: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch user signals (operator endpoint)
 */
export async function fetchUserSignals(userId: string, timeWindow: string = '30d') {
  const response = await fetch(`${API_BASE_URL}/api/operator/users/${userId}/signals?time_window=${timeWindow}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch user signals: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch decision traces (operator endpoint)
 */
export async function fetchDecisionTraces(userId: string) {
  const response = await fetch(`${API_BASE_URL}/api/operator/users/${userId}/traces`)
  if (!response.ok) {
    throw new Error(`Failed to fetch decision traces: ${response.statusText}`)
  }
  return response.json()
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

type ApiOptions = Omit<RequestInit, 'headers'> & {
  headers?: Record<string, string>
  skipAuth?: boolean
}

async function getToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

async function setToken(token: string): Promise<void> {
  localStorage.setItem('token', token)
  document.cookie = `token=${token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`
}

function removeToken(): void {
  localStorage.removeItem('token')
  document.cookie = 'token=; path=/; max-age=0'
}

async function apiFetch<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { skipAuth = false, headers = {}, ...rest } = options
  const token = await getToken()

  const reqHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  }

  if (token && !skipAuth) {
    reqHeaders['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    headers: reqHeaders,
  })

  if (response.status === 401 && !skipAuth) {
    removeToken()
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    const body = await response.text()
    throw new Error(body || `API error ${response.status}`)
  }

  if (response.status === 204) return undefined as T

  return response.json() as Promise<T>
}

export type AuthResponse = {
  token: string
  user: {
    id: string
    email: string
    name: string
  }
}

export type Product = {
  id: string
  name: string
  description: string
  price: number
  images: string[]
  colors: string[]
  sizes: string[]
  inStock: boolean
}

export type OrderItem = {
  productId: string
  name: string
  price: number
  quantity: number
  size: string
  color: string
}

export type CheckoutSessionRequest = {
  email: string
  items: OrderItem[]
  successUrl: string
  cancelUrl: string
}

export type CheckoutSessionResponse = {
  url: string
  sessionId: string
}

export type CreateOrderRequest = {
  email: string
  items: OrderItem[]
  paymentIntentId: string
}

export type Order = {
  id: string
  ref: string
  status: string
  items: OrderItem[]
  total: number
  estimatedDelivery: string
}

export const api = {
  auth: {
    login: async (email: string, password: string): Promise<AuthResponse> => {
      const data = await apiFetch<AuthResponse>('/api/auth/login', {
        method: 'POST',
        skipAuth: true,
        body: JSON.stringify({ email, password }),
      })
      await setToken(data.token)
      return data
    },
    register: async (name: string, email: string, password: string): Promise<AuthResponse> => {
      const data = await apiFetch<AuthResponse>('/api/auth/register', {
        method: 'POST',
        skipAuth: true,
        body: JSON.stringify({ name, email, password }),
      })
      await setToken(data.token)
      return data
    },
    logout: (): void => {
      removeToken()
    },
  },
  products: {
    list: (): Promise<Product[]> =>
      apiFetch<Product[]>('/api/products', { skipAuth: true }),
    get: (id: string): Promise<Product> =>
      apiFetch<Product>(`/api/products/${id}`, { skipAuth: true }),
  },
  payments: {
    createCheckoutSession: (req: CheckoutSessionRequest): Promise<CheckoutSessionResponse> =>
      apiFetch<CheckoutSessionResponse>('/api/payments/checkout-session', {
        method: 'POST',
        body: JSON.stringify(req),
      }),
  },
  orders: {
    create: (req: CreateOrderRequest): Promise<Order> =>
      apiFetch<Order>('/api/orders/create', {
        method: 'POST',
        body: JSON.stringify(req),
      }),
  },
}

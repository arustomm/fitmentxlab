import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

// Product queries
export async function getProducts(params?: {
  category?: string
  search?: string
  sortBy?: 'price-asc' | 'price-desc' | 'newest'
  limit?: number
}) {
  const { category, search, sortBy, limit } = params || {}

  const where: any = {}

  if (category && category !== 'all') {
    where.category = category
  }

  if (search) {
    where.OR = [
      { name: { contains: search, mode: 'insensitive' } },
      { brand: { contains: search, mode: 'insensitive' } },
      { description: { contains: search, mode: 'insensitive' } },
    ]
  }

  let orderBy: any = { createdAt: 'desc' }

  if (sortBy === 'price-asc') {
    orderBy = { price: 'asc' }
  } else if (sortBy === 'price-desc') {
    orderBy = { price: 'desc' }
  } else if (sortBy === 'newest') {
    orderBy = { createdAt: 'desc' }
  }

  return prisma.product.findMany({
    where,
    orderBy,
    take: limit,
  })
}

export async function getProductBySlug(slug: string) {
  return prisma.product.findUnique({
    where: { slug },
  })
}

export async function getFeaturedProducts(limit = 8) {
  return prisma.product.findMany({
    where: { isFeatured: true },
    orderBy: { createdAt: 'desc' },
    take: limit,
  })
}

export async function getProductsByCategory(category: string, limit = 12) {
  return prisma.product.findMany({
    where: { category },
    orderBy: { createdAt: 'desc' },
    take: limit,
  })
}


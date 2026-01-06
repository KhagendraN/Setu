/**
 * Document Cache Utility
 * Stores analyzed documents and generated letters separately in browser localStorage
 * Each user gets their own isolated storage
 */

export interface AnalyzedDocument {
  id: string
  filename: string
  analyzedAt: string
  result: {
    totalSentences?: number
    biasedCount?: number
    neutralCount?: number
    success: boolean
  }
  sessionId?: string
}

export interface GeneratedLetter {
  id: string
  filename: string
  templateName: string
  generatedAt: string
  success: boolean
}

const MAX_CACHE_SIZE = 100 // Maximum number of items to store per user

/**
 * Get storage keys for a specific user
 */
const getAnalyzedDocumentsKey = (userId: string) => `user_${userId}_analyzed_documents`
const getLettersGeneratedKey = (userId: string) => `user_${userId}_letters_generated`

// ==================== ANALYZED DOCUMENTS ====================

/**
 * Get all analyzed documents for a user
 */
export function getAnalyzedDocuments(userId: string): AnalyzedDocument[] {
  try {
    const cached = localStorage.getItem(getAnalyzedDocumentsKey(userId))
    if (!cached) return []
    return JSON.parse(cached)
  } catch (error) {
    console.error("Error reading analyzed documents cache:", error)
    return []
  }
}

/**
 * Add a new analyzed document to cache
 */
export function addAnalyzedDocument(
  userId: string,
  document: Omit<AnalyzedDocument, "id" | "analyzedAt">
): void {
  try {
    const documents = getAnalyzedDocuments(userId)

    const newDocument: AnalyzedDocument = {
      ...document,
      id: generateId("doc"),
      analyzedAt: new Date().toISOString(),
    }

    // Add to beginning of array (most recent first)
    documents.unshift(newDocument)

    // Limit cache size
    if (documents.length > MAX_CACHE_SIZE) {
      documents.splice(MAX_CACHE_SIZE)
    }

    localStorage.setItem(getAnalyzedDocumentsKey(userId), JSON.stringify(documents))
  } catch (error) {
    console.error("Error adding analyzed document to cache:", error)
  }
}

/**
 * Get statistics about analyzed documents
 */
export function getAnalyzedDocumentsStats(userId: string) {
  const documents = getAnalyzedDocuments(userId)

  const totalAnalyzed = documents.length
  let totalInclusive = 0
  let totalFlagged = 0

  documents.forEach((doc) => {
    if (doc.result.biasedCount === 0) {
      totalInclusive++
    } else if (doc.result.biasedCount && doc.result.biasedCount > 0) {
      totalFlagged++
    }
  })

  return {
    totalAnalyzed,
    totalInclusive,
    totalFlagged,
  }
}

/**
 * Clear all analyzed documents for a user
 */
export function clearAnalyzedDocuments(userId: string): void {
  try {
    localStorage.removeItem(getAnalyzedDocumentsKey(userId))
  } catch (error) {
    console.error("Error clearing analyzed documents cache:", error)
  }
}

// ==================== GENERATED LETTERS ====================

/**
 * Get all generated letters for a user
 */
export function getGeneratedLetters(userId: string): GeneratedLetter[] {
  try {
    const cached = localStorage.getItem(getLettersGeneratedKey(userId))
    if (!cached) return []
    return JSON.parse(cached)
  } catch (error) {
    console.error("Error reading generated letters cache:", error)
    return []
  }
}

/**
 * Add a new generated letter to cache
 */
export function addGeneratedLetter(
  userId: string,
  letter: Omit<GeneratedLetter, "id" | "generatedAt">
): void {
  try {
    const letters = getGeneratedLetters(userId)

    const newLetter: GeneratedLetter = {
      ...letter,
      id: generateId("letter"),
      generatedAt: new Date().toISOString(),
    }

    // Add to beginning of array (most recent first)
    letters.unshift(newLetter)

    // Limit cache size
    if (letters.length > MAX_CACHE_SIZE) {
      letters.splice(MAX_CACHE_SIZE)
    }

    localStorage.setItem(getLettersGeneratedKey(userId), JSON.stringify(letters))
  } catch (error) {
    console.error("Error adding generated letter to cache:", error)
  }
}

/**
 * Get statistics about generated letters
 */
export function getGeneratedLettersStats(userId: string) {
  const letters = getGeneratedLetters(userId)

  return {
    totalLetters: letters.length,
  }
}

/**
 * Clear all generated letters for a user
 */
export function clearGeneratedLetters(userId: string): void {
  try {
    localStorage.removeItem(getLettersGeneratedKey(userId))
  } catch (error) {
    console.error("Error clearing generated letters cache:", error)
  }
}

// ==================== COMBINED STATS (for Dashboard) ====================

/**
 * Get combined statistics for dashboard
 */
export function getDocumentStats(userId: string) {
  const analyzedStats = getAnalyzedDocumentsStats(userId)
  const letterStats = getGeneratedLettersStats(userId)

  return {
    ...analyzedStats,
    ...letterStats,
  }
}

// ==================== USER CLEANUP ====================

/**
 * Clear all cached data for a specific user (useful for logout)
 */
export function clearUserCache(userId: string): void {
  clearAnalyzedDocuments(userId)
  clearGeneratedLetters(userId)
}

/**
 * Clear all user caches (useful when switching users or full cleanup)
 */
export function clearAllUserCaches(): void {
  try {
    Object.keys(localStorage).forEach((key) => {
      if (
        (key.startsWith("user_") && key.includes("_analyzed_documents")) ||
        (key.startsWith("user_") && key.includes("_letters_generated"))
      ) {
        localStorage.removeItem(key)
      }
    })
  } catch (error) {
    console.error("Error clearing all user caches:", error)
  }
}

// ==================== UTILITY ====================

/**
 * Generate a unique ID
 */
function generateId(prefix: string): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`
}

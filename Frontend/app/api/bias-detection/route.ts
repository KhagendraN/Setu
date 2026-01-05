import { type NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function POST(req: NextRequest) {
  try {
    // Get Authorization header from incoming request
    const authHeader = req.headers.get("authorization")
    const headers: Record<string, string> = {}
    if (authHeader) {
      headers["Authorization"] = authHeader
    }

    const formData = await req.formData()
    const file = formData.get("file") as File | null
    const text = formData.get("text") as string | null
    const confidenceThreshold = parseFloat(formData.get("confidence_threshold") as string || "0.7")
    const useHITL = formData.get("use_hitl") === "true"

    // If using HITL workflow for PDF files
    if (file && useHITL) {
      console.log("Using HITL workflow for PDF processing...")
      const hitlFormData = new FormData()
      hitlFormData.append("file", file)
      hitlFormData.append("refine_with_llm", "true")
      hitlFormData.append("confidence_threshold", confidenceThreshold.toString())

      const response = await fetch(`${BACKEND_URL}/api/v1/bias-detection-hitl/start-review`, {
        method: "POST",
        headers,
        body: hitlFormData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || "Failed to start HITL review")
      }

      const data = await response.json()
      console.log("HITL session created:", data.session_id)

      // Return the HITL session data
      return NextResponse.json(data)
    }

    // Original non-HITL workflow for text or non-HITL PDF processing
    let sentences: string[] = []
    let filename: string | undefined

    if (file) {
      // Step 1: Process PDF to extract sentences with LLM refinement
      console.log("Step 1: Processing PDF to extract sentences...")
      const pdfFormData = new FormData()
      pdfFormData.append("file", file)
      pdfFormData.append("refine_with_llm", "true")

      const pdfResponse = await fetch(`${BACKEND_URL}/api/v1/process-pdf`, {
        method: "POST",
        headers,
        body: pdfFormData,
      })

      if (!pdfResponse.ok) {
        throw new Error("Failed to process PDF")
      }

      const pdfData = await pdfResponse.json()
      sentences = pdfData.sentences
      filename = pdfData.filename
      console.log(`Extracted ${sentences.length} sentences from PDF`)
    } else if (text) {
      // For text input, use single sentence as array
      sentences = [text]
    } else {
      return NextResponse.json({ error: "Either file or text must be provided" }, { status: 400 })
    }

    // Step 2: Detect bias using batch endpoint
    console.log("Step 2: Detecting bias in sentences...")
    const biasHeaders = { ...headers, "Content-Type": "application/json" }
    const batchBiasResponse = await fetch(`${BACKEND_URL}/api/v1/detect-bias/batch`, {
      method: "POST",
      headers: biasHeaders,
      body: JSON.stringify({
        texts: sentences,
        confidence_threshold: confidenceThreshold,
      }),
    })

    if (!batchBiasResponse.ok) {
      throw new Error("Failed to detect bias")
    }

    const batchBiasData = await batchBiasResponse.json()

    // Count biased and unbiased sentences
    let biasedCount = 0
    let unbiasedCount = 0
    const biasedSentencesData: Array<{
      sentence: string
      category: string
      confidence: number
      explanation?: string
    }> = []

    // Process batch results
    for (const item of batchBiasData.items) {
      const result = item.result
      if (result.success && result.results) {
        for (const sentenceResult of result.results) {
          if (sentenceResult.is_biased) {
            biasedCount++
            biasedSentencesData.push({
              sentence: sentenceResult.sentence,
              category: sentenceResult.category,
              confidence: sentenceResult.confidence,
            })
          } else {
            unbiasedCount++
          }
        }
      }
    }

    console.log(`Found ${biasedCount} biased sentences and ${unbiasedCount} unbiased sentences`)

    // Step 3: Get debiasing suggestions for biased sentences
    console.log("Step 3: Getting debiasing suggestions...")
    const suggestionsData: Array<{
      original: string
      category: string
      confidence: number
      suggestion: string | null
      explanation: string | null
      success: boolean
    }> = []

    if (biasedSentencesData.length > 0) {
      // Prepare batch debias request
      const debiasItems = biasedSentencesData.map((item) => ({
        sentence: item.sentence,
        category: item.category,
        context: null,
      }))

      const debiasResponse = await fetch(`${BACKEND_URL}/api/v1/debias-sentence/batch`, {
        method: "POST",
        headers: biasHeaders,
        body: JSON.stringify({
          items: debiasItems,
        }),
      })

      if (debiasResponse.ok) {
        const debiasData = await debiasResponse.json()

        for (let i = 0; i < biasedSentencesData.length; i++) {
          const original = biasedSentencesData[i]
          const debiasResult = debiasData.items?.[i]?.result

          // Generate explanation based on category
          const categoryExplanations: Record<string, string> = {
            gender: "This sentence contains gender-based bias, using language that may stereotype, exclude, or unfairly characterize individuals based on their gender.",
            religional: "This sentence contains religious bias, using language that may discriminate against or unfairly characterize individuals based on their religious beliefs.",
            caste: "This sentence contains caste-based bias, using language that may perpetuate discrimination or unfair treatment based on caste identity.",
            religion: "This sentence contains religious bias, with language that may show prejudice or discrimination based on religious affiliation.",
            appearence: "This sentence contains appearance-based bias, using language that may judge or discriminate based on physical appearance or looks.",
            socialstatus: "This sentence contains social status bias, using language that may discriminate or show prejudice based on socioeconomic status or class.",
            political: "This sentence contains political bias, showing unfair preference or prejudice toward a particular political viewpoint or party.",
            Age: "This sentence contains age-based bias, using language that may stereotype or discriminate based on age or generation.",
            Disablity: "This sentence contains disability-based bias, using language that may discriminate against or unfairly characterize individuals with disabilities.",
            amiguity: "This sentence contains ambiguous language that may lead to misinterpretation or unclear bias.",
          }

          const explanation = categoryExplanations[original.category] || "This sentence has been flagged for potential bias."

          suggestionsData.push({
            original: original.sentence,
            category: original.category,
            confidence: original.confidence,
            suggestion: debiasResult?.suggestion || null,
            explanation: explanation,
            success: debiasResult?.success || false,
          })
        }
      } else {
        // If debias fails, still return results without suggestions
        console.warn("Debiasing failed, returning results without suggestions")
        for (const item of biasedSentencesData) {
          suggestionsData.push({
            original: item.sentence,
            category: item.category,
            confidence: item.confidence,
            suggestion: null,
            explanation: null,
            success: false,
          })
        }
      }
    }

    console.log("Analysis complete!")

    // Return formatted response
    return NextResponse.json({
      success: true,
      biasedCount,
      unbiasedCount,
      totalSentences: biasedCount + unbiasedCount,
      biasedSentences: suggestionsData,
      filename,
    })
  } catch (error) {
    console.error("[Bias Detection API Error]:", error)
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Failed to analyze bias. Please ensure the backend server is running.",
      },
      { status: 500 }
    )
  }
}

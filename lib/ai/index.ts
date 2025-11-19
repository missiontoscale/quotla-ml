import { generateDescription as generateWithAnthropic } from './anthropic'
import { generateDescriptionWithOpenAI } from './openai'
import { generateDescriptionWithGemini } from './gemini'

type AIProvider = 'anthropic' | 'openai' | 'gemini' | 'none'

const AI_PROVIDER = (process.env.AI_PROVIDER || 'anthropic') as AIProvider

export async function generateDescription(prompt: string): Promise<string> {
  // Try the primary provider first
  let primaryError: Error | null = null

  switch (AI_PROVIDER) {
    case 'openai':
      try {
        return await generateDescriptionWithOpenAI(prompt)
      } catch (error) {
        primaryError = error instanceof Error ? error : new Error('OpenAI failed')
        console.log('Primary provider (OpenAI) failed, trying fallback...', primaryError.message)
      }
      break

    case 'gemini':
      try {
        return await generateDescriptionWithGemini(prompt)
      } catch (error) {
        primaryError = error instanceof Error ? error : new Error('Gemini failed')
        console.log('Primary provider (Gemini) failed, trying fallback...', primaryError.message)
      }
      break

    case 'anthropic':
      try {
        return await generateWithAnthropic(prompt)
      } catch (error) {
        primaryError = error instanceof Error ? error : new Error('Anthropic failed')
        console.log('Primary provider (Anthropic) failed, trying fallback...', primaryError.message)
      }
      break

    case 'none':
      throw new Error('AI generation is disabled. Please enable an AI provider in your environment variables.')
  }

  // If primary provider failed, try fallback providers
  if (primaryError) {
    console.log('Attempting fallback providers...')

    // Try all providers except the one that already failed
    const providers = [
      { name: 'anthropic', fn: generateWithAnthropic },
      { name: 'openai', fn: generateDescriptionWithOpenAI },
      { name: 'gemini', fn: generateDescriptionWithGemini },
    ].filter(p => p.name !== AI_PROVIDER)

    for (const provider of providers) {
      try {
        console.log(`Trying fallback provider: ${provider.name}`)
        return await provider.fn(prompt)
      } catch (error) {
        console.log(`Fallback provider ${provider.name} failed:`, error instanceof Error ? error.message : 'Unknown error')
      }
    }

    // All providers failed
    throw new Error(`AI generation failed. Primary provider error: ${primaryError.message}`)
  }

  // This should never happen, but TypeScript needs it
  throw new Error('Unexpected error in AI generation')
}

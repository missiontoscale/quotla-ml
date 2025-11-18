import { generateDescription as generateWithAnthropic } from './anthropic'
import { generateDescriptionWithOpenAI } from './openai'
import { generateDescriptionWithGemini } from './gemini'

type AIProvider = 'anthropic' | 'openai' | 'gemini' | 'none'

const AI_PROVIDER = (process.env.AI_PROVIDER || 'anthropic') as AIProvider

export async function generateDescription(prompt: string): Promise<string> {
  switch (AI_PROVIDER) {
    case 'openai':
      return await generateDescriptionWithOpenAI(prompt)

    case 'gemini':
      return await generateDescriptionWithGemini(prompt)

    case 'anthropic':
      return await generateWithAnthropic(prompt)

    case 'none':
      throw new Error('AI generation is disabled. Please enable an AI provider in your environment variables.')

    default:
      // Try providers in order until one works
      try {
        return await generateWithAnthropic(prompt)
      } catch (anthropicError) {
        console.log('Anthropic failed, trying OpenAI...', anthropicError)
        try {
          return await generateDescriptionWithOpenAI(prompt)
        } catch (openaiError) {
          console.log('OpenAI failed, trying Gemini...', openaiError)
          try {
            return await generateDescriptionWithGemini(prompt)
          } catch (geminiError) {
            console.error('All AI providers failed')
            throw new Error('AI generation failed. Please check your API keys.')
          }
        }
      }
  }
}

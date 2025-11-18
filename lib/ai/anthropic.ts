import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
})

export async function generateDescription(prompt: string): Promise<string> {
  try {
    const message = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 500,
      messages: [
        {
          role: 'user',
          content: `You are a professional business writer helping to create clear, professional descriptions for quotes and invoices.

The user will describe a service or product, and you should generate a concise, professional description suitable for a business quote or invoice line item.

Keep it professional, clear, and focused on the value provided. Use 2-4 sentences maximum.

User request: ${prompt}

Generate only the description, without any preamble or additional commentary.`,
        },
      ],
    })

    const content = message.content[0]
    if (content.type === 'text') {
      return content.text.trim()
    }

    throw new Error('Unexpected response format')
  } catch (error) {
    console.error('AI generation error:', error)
    throw new Error('Failed to generate description')
  }
}

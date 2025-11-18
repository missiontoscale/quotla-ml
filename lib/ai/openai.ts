import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

export async function generateDescriptionWithOpenAI(prompt: string): Promise<string> {
  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: 'You are a professional business writer helping to create clear, professional descriptions for quotes and invoices. Keep it professional, clear, and focused on the value provided. Use 2-4 sentences maximum. Generate only the description, without any preamble or additional commentary.',
        },
        {
          role: 'user',
          content: `Create a professional description for this service: ${prompt}`,
        },
      ],
      max_tokens: 300,
      temperature: 0.7,
    })

    const description = completion.choices[0]?.message?.content?.trim()

    if (!description) {
      throw new Error('No description generated')
    }

    return description
  } catch (error) {
    console.error('OpenAI generation error:', error)
    throw new Error('Failed to generate description with OpenAI')
  }
}

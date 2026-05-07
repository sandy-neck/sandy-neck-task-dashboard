import Anthropic from '@anthropic-ai/sdk'
import { NextResponse } from 'next/server'
import { fetchOfficialImage } from '@/lib/pokemon-tcg'

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY! })

export async function POST(req: Request) {
  try {
    const { cardName, setName, cardNumber, rarity, condition } = await req.json()

    if (!cardName) {
      return NextResponse.json({ error: 'Card name required' }, { status: 400 })
    }

    const [aiResponse, official_image_url] = await Promise.all([
      client.messages.create({
        model: 'claude-sonnet-4-6',
        max_tokens: 256,
        messages: [
          {
            role: 'user',
            content: `You are a Pokémon card market expert. Estimate the current market value for:

Card: ${cardName}
Set: ${setName || 'Unknown'}
Number: ${cardNumber || 'Unknown'}
Rarity: ${rarity || 'Unknown'}
Condition: ${condition || 'Near Mint'}

Return ONLY a JSON object:
{
  "estimated_value_usd": 0.00,
  "notes": "1-2 sentences on current market conditions and what drives this card's value"
}`,
          },
        ],
      }),
      fetchOfficialImage(cardName, setName, cardNumber),
    ])

    const content = aiResponse.content[0]
    if (content.type !== 'text') {
      return NextResponse.json({ error: 'Unexpected AI response' }, { status: 500 })
    }

    const cleaned = content.text.trim().replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '')
    const result = JSON.parse(cleaned)
    return NextResponse.json({ ...result, official_image_url })
  } catch (error) {
    console.error('Revalue error:', error)
    return NextResponse.json({ error: 'Failed to re-value card' }, { status: 500 })
  }
}

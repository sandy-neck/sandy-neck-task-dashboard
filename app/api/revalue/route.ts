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
        model: 'claude-sonnet-5',
        max_tokens: 400,
        thinking: { type: 'disabled' },
        messages: [
          {
            role: 'user',
            content: `You are a Pokémon card market expert with deep knowledge of TCGPlayer and eBay sold-listing prices. Estimate the current market value for:

Card: ${cardName}
Set: ${setName || 'Unknown'}
Number: ${cardNumber || 'Unknown'}
Rarity: ${rarity || 'Unknown'}
Condition: ${condition || 'Near Mint'}

Base your estimate on this specific card's known sales history, not a generic price tier for its rarity. Two cards of the same rarity from the same era can differ significantly in value based on character popularity, print run, and demand — do not default to a common "round number" estimate. Use cents-level precision when the real market price supports it (e.g. $3.85 or $6.20 rather than always $3.50 or $6.50 or $4.50).

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

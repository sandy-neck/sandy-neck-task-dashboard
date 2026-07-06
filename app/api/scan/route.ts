import Anthropic from '@anthropic-ai/sdk'
import { NextResponse } from 'next/server'
import { fetchOfficialImage } from '@/lib/pokemon-tcg'

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY! })

export async function POST(req: Request) {
  try {
    const { imageBase64, mimeType } = await req.json()

    if (!imageBase64) {
      return NextResponse.json({ error: 'No image provided' }, { status: 400 })
    }

    const response = await client.messages.create({
      model: 'claude-sonnet-5',
      max_tokens: 1400,
      thinking: { type: 'disabled' },
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'image',
              source: {
                type: 'base64',
                media_type: mimeType || 'image/jpeg',
                data: imageBase64,
              },
            },
            {
              type: 'text',
              text: `You are a Pokémon card expert and professional grader. Analyze this card image carefully and return a JSON object with exactly these fields:

{
  "name": "the exact card name",
  "set_name": "the set or expansion name",
  "card_number": "card number like 25/102",
  "rarity": "Common, Uncommon, Rare, Holo Rare, Ultra Rare, Secret Rare, etc",
  "hp": "HP number as string, or empty string if not a Pokemon card",
  "card_type": "Pokemon, Trainer, or Energy",
  "pokemon_type": "Fire, Water, Grass, Lightning, Psychic, Fighting, Darkness, Metal, Dragon, Fairy, Colorless, or empty string",
  "condition": "Mint, Near Mint, Lightly Played, Moderately Played, Heavily Played, or Damaged",
  "condition_notes": "1-2 sentences describing visible wear, edge whitening, scratches, centering",
  "estimated_value_usd": 0.00,
  "ai_description": "1-2 sentence description of the card",
  "ai_valuation_notes": "1-2 sentences explaining what drives this card's value"
}

For estimated_value_usd: use your best knowledge of this specific card's actual TCGPlayer/eBay sold-listing prices — not a generic price tier for its rarity. Two cards of the same rarity and era can differ significantly in value based on character popularity, print run, and demand, so do not default to a common "round number" estimate. Use cents-level precision when the real market price supports it (e.g. $3.85 or $6.20 rather than always $3.50 or $6.50 or $4.50). Consider the set era, rarity, card popularity, and the condition you observed. Be realistic and grounded.

Return ONLY the JSON object. No markdown, no code blocks, no other text.`,
            },
          ],
        },
      ],
    })

    const content = response.content[0]
    if (content.type !== 'text') {
      return NextResponse.json({ error: 'Unexpected response from AI' }, { status: 500 })
    }

    const cleaned = content.text.trim().replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '')
    const result = JSON.parse(cleaned)

    // Fetch official card image from Pokémon TCG API
    const official_image_url = await fetchOfficialImage(result.name, result.set_name, result.card_number)

    return NextResponse.json({ ...result, official_image_url })
  } catch (error) {
    console.error('Scan error:', error)
    return NextResponse.json({ error: 'Failed to analyze card' }, { status: 500 })
  }
}

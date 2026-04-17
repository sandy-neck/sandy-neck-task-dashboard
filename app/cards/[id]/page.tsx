'use client'

export const dynamic = 'force-dynamic'

import { useCallback, useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Image from 'next/image'
import { supabase } from '@/lib/supabase'
import { Card, PriceSnapshot } from '@/lib/types'
import PriceChart from '@/components/PriceChart'

function conditionBadge(condition: string | null) {
  if (!condition) return 'bg-zinc-700 text-zinc-400'
  const c = condition.toLowerCase()
  if (c.includes('mint')) return 'bg-green-900/60 text-green-400'
  if (c.includes('lightly')) return 'bg-yellow-900/60 text-yellow-400'
  if (c.includes('moderately')) return 'bg-orange-900/60 text-orange-400'
  return 'bg-red-900/60 text-red-400'
}

export default function CardDetailPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const [card, setCard] = useState<Card | null>(null)
  const [snapshots, setSnapshots] = useState<PriceSnapshot[]>([])
  const [loading, setLoading] = useState(true)
  const [revaluing, setRevaluing] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const loadCard = useCallback(async () => {
    const [cardRes, snapshotsRes] = await Promise.all([
      supabase.from('cards').select('*').eq('id', id).single(),
      supabase.from('price_snapshots').select('*').eq('card_id', id).order('created_at', { ascending: true }),
    ])
    if (cardRes.data) setCard(cardRes.data)
    if (snapshotsRes.data) setSnapshots(snapshotsRes.data)
    setLoading(false)
  }, [id])

  useEffect(() => { loadCard() }, [loadCard])

  async function handleRevalue() {
    if (!card) return
    setRevaluing(true)
    try {
      const res = await fetch('/api/revalue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cardName: card.name,
          setName: card.set_name,
          cardNumber: card.card_number,
          rarity: card.rarity,
          condition: card.condition,
        }),
      })
      const data = await res.json()
      const newValue = Number(data.estimated_value_usd)

      if (data.error) {
        alert(`Re-value error: ${data.error}`)
        setRevaluing(false)
        return
      }

      if (newValue > 0) {
        const update: Record<string, unknown> = { current_value: newValue, updated_at: new Date().toISOString() }
        if (data.official_image_url) update.image_url = data.official_image_url

        await Promise.all([
          supabase.from('cards').update(update).eq('id', card.id),
          supabase.from('price_snapshots').insert({ card_id: card.id, estimated_value: newValue, notes: data.notes }),
        ])
      } else {
        alert(`Got value: ${data.estimated_value_usd} — check API key in Vercel env vars`)
      }

      await loadCard()
    } catch (err) {
      alert(`Re-value failed: ${err}`)
    }
    setRevaluing(false)
  }

  async function handleDelete() {
    if (!card || !confirm(`Remove ${card.name} from your collection?`)) return
    setDeleting(true)

    if (card.image_url?.includes('/card-images/')) {
      const path = card.image_url.split('/card-images/')[1]
      if (path) await supabase.storage.from('card-images').remove([path])
    }

    await supabase.from('cards').delete().eq('id', card.id)
    router.push('/cards')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-amber-400 text-lg">Loading...</p>
      </div>
    )
  }

  if (!card) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-zinc-400">Card not found.</p>
      </div>
    )
  }

  const details = [
    { label: 'Rarity', value: card.rarity },
    { label: 'Card Type', value: card.card_type },
    { label: 'Pokémon Type', value: card.pokemon_type },
    { label: 'HP', value: card.hp },
    { label: 'Set', value: card.set_name },
    { label: 'Number', value: card.card_number },
  ]

  return (
    <div className="max-w-lg mx-auto" style={{ paddingBottom: 'calc(6rem + env(safe-area-inset-bottom))' }}>
      <div className="px-4 pt-6 mb-4">
        <button onClick={() => router.back()} className="text-amber-400 text-sm">
          ← Back
        </button>
      </div>

      {/* Card Image */}
      <div className="px-8 mb-6 flex justify-center">
        {card.image_url ? (
          <Image
            src={card.image_url}
            alt={card.name}
            width={220}
            height={308}
            className="rounded-2xl shadow-2xl shadow-amber-400/10 object-cover"
          />
        ) : (
          <div className="w-52 h-72 bg-zinc-800 rounded-2xl flex items-center justify-center text-6xl">
            🃏
          </div>
        )}
      </div>

      <div className="px-4 space-y-4">
        {/* Name + Value */}
        <div>
          <h1 className="text-2xl font-bold text-white">{card.name}</h1>
          {card.set_name && (
            <p className="text-zinc-400 text-sm">
              {card.set_name}{card.card_number ? ` · ${card.card_number}` : ''}
            </p>
          )}
        </div>

        {/* Value Card */}
        <div className="bg-zinc-900 rounded-2xl p-4 border border-zinc-800">
          <p className="text-zinc-400 text-sm mb-1">Estimated Value</p>
          <p className="text-3xl font-bold text-amber-400">${(Number(card.current_value) || 0).toFixed(2)}</p>
          <button
            onClick={handleRevalue}
            disabled={revaluing}
            className="mt-3 w-full py-2 rounded-xl bg-amber-400/10 text-amber-400 text-sm font-medium border border-amber-400/20 hover:bg-amber-400/20 transition-colors disabled:opacity-40"
          >
            {revaluing ? '⏳ Re-valuing...' : '🔄 Re-value Card'}
          </button>
        </div>

        {/* Details */}
        <div className="bg-zinc-900 rounded-2xl p-4 border border-zinc-800 space-y-3">
          <h2 className="text-white font-semibold">Card Details</h2>
          {details.map(({ label, value }) =>
            value ? (
              <div key={label} className="flex justify-between text-sm">
                <span className="text-zinc-400">{label}</span>
                <span className="text-white">{value}</span>
              </div>
            ) : null
          )}
          <div className="flex justify-between items-center text-sm">
            <span className="text-zinc-400">Condition</span>
            <span className={`text-xs px-2 py-1 rounded-full ${conditionBadge(card.condition)}`}>
              {card.condition || 'Unknown'}
            </span>
          </div>
          {card.condition_notes && (
            <p className="text-zinc-400 text-xs border-t border-zinc-800 pt-3">{card.condition_notes}</p>
          )}
        </div>

        {/* Price History */}
        {snapshots.length > 1 && (
          <div className="bg-zinc-900 rounded-2xl p-4 border border-zinc-800">
            <h2 className="text-white font-semibold mb-3">Price History</h2>
            <PriceChart data={snapshots} />
          </div>
        )}

        {/* AI Analysis */}
        {(card.ai_description || card.ai_valuation_notes) && (
          <div className="bg-zinc-900 rounded-2xl p-4 border border-zinc-800 space-y-3">
            <h2 className="text-white font-semibold">AI Analysis</h2>
            {card.ai_description && <p className="text-zinc-400 text-sm">{card.ai_description}</p>}
            {card.ai_valuation_notes && (
              <p className="text-zinc-400 text-sm border-t border-zinc-800 pt-3">{card.ai_valuation_notes}</p>
            )}
          </div>
        )}

        {/* Delete */}
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="w-full py-3 rounded-xl bg-red-900/20 text-red-400 text-sm font-medium border border-red-900/40 hover:bg-red-900/30 transition-colors disabled:opacity-40"
        >
          {deleting ? 'Removing...' : 'Remove from Collection'}
        </button>
      </div>
    </div>
  )
}

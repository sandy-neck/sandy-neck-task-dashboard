'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { supabase } from '@/lib/supabase'
import { Card } from '@/lib/types'

function conditionBadge(condition: string | null) {
  if (!condition) return 'bg-zinc-700 text-zinc-400'
  const c = condition.toLowerCase()
  if (c.includes('mint')) return 'bg-green-900/60 text-green-400'
  if (c.includes('lightly')) return 'bg-yellow-900/60 text-yellow-400'
  if (c.includes('moderately')) return 'bg-orange-900/60 text-orange-400'
  return 'bg-red-900/60 text-red-400'
}

function rarityRank(rarity: string | null): number {
  if (!rarity) return 0
  const r = rarity.toLowerCase()
  if (r.includes('secret')) return 6
  if (r.includes('ultra')) return 5
  if (r.includes('holo')) return 4
  if (r.includes('rare')) return 3
  if (r.includes('uncommon')) return 2
  if (r.includes('common')) return 1
  return 0
}

type SortKey = 'value-desc' | 'value-asc' | 'name' | 'rarity' | 'newest'

const SORTS: { key: SortKey; label: string }[] = [
  { key: 'value-desc', label: 'Value ↓' },
  { key: 'value-asc', label: 'Value ↑' },
  { key: 'name', label: 'Name' },
  { key: 'rarity', label: 'Rarity' },
  { key: 'newest', label: 'Newest' },
]

function sortCards(cards: Card[], sort: SortKey): Card[] {
  return [...cards].sort((a, b) => {
    switch (sort) {
      case 'value-desc': return (Number(b.current_value) || 0) - (Number(a.current_value) || 0)
      case 'value-asc':  return (Number(a.current_value) || 0) - (Number(b.current_value) || 0)
      case 'name':       return a.name.localeCompare(b.name)
      case 'rarity':     return rarityRank(b.rarity) - rarityRank(a.rarity)
      case 'newest':     return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    }
  })
}

export default function CardsPage() {
  const [cards, setCards] = useState<Card[]>([])
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState<SortKey>('newest')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase
      .from('cards')
      .select('*')
      .then(({ data }) => {
        if (data) setCards(data)
        setLoading(false)
      })
  }, [])

  const filtered = sortCards(
    cards.filter(
      (c) =>
        c.name.toLowerCase().includes(search.toLowerCase()) ||
        (c.set_name || '').toLowerCase().includes(search.toLowerCase())
    ),
    sort
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-amber-400 text-lg">Loading...</p>
      </div>
    )
  }

  return (
    <div className="px-4 pt-6 max-w-lg mx-auto" style={{ paddingBottom: 'calc(6rem + env(safe-area-inset-bottom))' }}>
      <h1 className="text-2xl font-bold text-white mb-4">My Cards</h1>

      <input
        type="text"
        placeholder="Search by name or set..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-4 py-3 text-white placeholder-zinc-500 mb-3 focus:outline-none focus:border-amber-400 transition-colors"
      />

      {/* Sort bar */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-1 scrollbar-none">
        {SORTS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setSort(key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
              sort === key
                ? 'bg-amber-400 text-black'
                : 'bg-zinc-900 text-zinc-400 border border-zinc-800 hover:border-zinc-600'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-zinc-400 text-sm">
            {cards.length === 0 ? 'No cards yet — scan one to get started!' : 'No cards match your search.'}
          </p>
          {cards.length === 0 && (
            <Link href="/scan" className="inline-block mt-4 bg-amber-400 text-black font-bold px-6 py-3 rounded-xl text-sm">
              Scan a Card
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {filtered.map((card) => (
            <Link key={card.id} href={`/cards/${card.id}`}>
              <div className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden hover:border-zinc-600 transition-colors">
                {card.image_url ? (
                  <Image
                    src={card.image_url}
                    alt={card.name}
                    width={200}
                    height={280}
                    className="w-full object-cover"
                    style={{ aspectRatio: '2/3' }}
                  />
                ) : (
                  <div className="flex items-center justify-center bg-zinc-800 text-4xl" style={{ aspectRatio: '2/3' }}>
                    🃏
                  </div>
                )}
                <div className="p-3">
                  <p className="text-white font-medium text-sm truncate">{card.name}</p>
                  <p className="text-zinc-500 text-xs truncate mb-2">{card.set_name || 'Unknown Set'}</p>
                  <div className="flex items-center justify-between gap-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full truncate ${conditionBadge(card.condition)}`}>
                      {card.condition?.split(' ')[0] ?? 'N/A'}
                    </span>
                    <span className="text-amber-400 text-sm font-semibold whitespace-nowrap">
                      ${(Number(card.current_value) || 0).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

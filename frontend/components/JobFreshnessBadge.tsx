interface JobFreshnessBadgeProps {
  scrapedAt: string | null
  isActive: boolean
}

export default function JobFreshnessBadge({ scrapedAt, isActive }: JobFreshnessBadgeProps) {
  if (!scrapedAt) {
    return null
  }

  const getDaysAgo = (dateString: string): number => {
    const scraped = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - scraped.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const daysAgo = getDaysAgo(scrapedAt)
  
  const getBadgeStyle = (days: number, active: boolean) => {
    if (!active) {
      return 'bg-gray-200 text-gray-700'
    }
    if (days <= 7) {
      return 'bg-green-100 text-green-800'
    }
    if (days <= 14) {
      return 'bg-yellow-100 text-yellow-800'
    }
    if (days <= 30) {
      return 'bg-orange-100 text-orange-800'
    }
    return 'bg-red-100 text-red-800'
  }

  const getTimeText = (days: number) => {
    if (days === 0) return 'Posted today'
    if (days === 1) return 'Posted yesterday'
    if (days <= 7) return `Posted ${days} days ago`
    if (days <= 14) return `Posted ${Math.floor(days / 7)} week ago`
    if (days <= 30) return `Posted ${Math.floor(days / 7)} weeks ago`
    return `Posted ${Math.floor(days / 30)} month${Math.floor(days / 30) > 1 ? 's' : ''} ago`
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBadgeStyle(daysAgo, isActive)}`}
    >
      {!isActive ? '⛔ Expired' : `🕐 ${getTimeText(daysAgo)}`}
    </span>
  )
}

interface JobSourceBadgeProps {
  source: string | null
  sourceUrl: string | null
}

export default function JobSourceBadge({ source, sourceUrl }: JobSourceBadgeProps) {
  if (!source || source === 'manual') {
    return null
  }

  const getSourceDisplay = (src: string): string => {
    switch (src.toLowerCase()) {
      case 'remoteok':
        return 'RemoteOK'
      case 'adzuna':
        return 'Adzuna'
      case 'indeed':
        return 'Indeed'
      case 'linkedin':
        return 'LinkedIn'
      default:
        return src.charAt(0).toUpperCase() + src.slice(1)
    }
  }

  const getSourceIcon = (src: string): string => {
    switch (src.toLowerCase()) {
      case 'remoteok':
        return '🌍'
      case 'adzuna':
        return '🔍'
      case 'indeed':
        return '💼'
      case 'linkedin':
        return '💻'
      default:
        return '🔗'
    }
  }

  const badge = (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
      {getSourceIcon(source)} {getSourceDisplay(source)}
    </span>
  )

  if (sourceUrl) {
    return (
      <a
        href={sourceUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="hover:opacity-75 transition-opacity"
        title={`View on ${getSourceDisplay(source)}`}
      >
        {badge}
      </a>
    )
  }

  return badge
}

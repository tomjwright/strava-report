'use client'

import { useEffect, useState } from 'react'
import { supabase, StravaActivity } from '@/lib/supabase'
import { Activity, BarChart3, Clock, Mountain, TrendingUp } from 'lucide-react'

export default function Dashboard() {
  const [activities, setActivities] = useState<StravaActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchActivities()
  }, [])

  const fetchActivities = async () => {
    try {
      const { data, error } = await supabase
        .from('strava_activities')
        .select('*')
        .order('start_date', { ascending: false })

      if (error) throw error
      setActivities(data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch activities')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading activities...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="text-center text-red-400">
          <p className="text-xl mb-2">Error loading activities</p>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  const stats = calculateStats(activities)

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Strava Dashboard</h1>
          <p className="text-gray-400">Track your athletic performance</p>
        </header>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Activities"
            value={stats.totalActivities}
            icon={<Activity className="w-6 h-6" />}
          />
          <StatCard
            title="Total Distance"
            value={`${stats.totalDistance.toFixed(2)} km`}
            icon={<TrendingUp className="w-6 h-6" />}
          />
          <StatCard
            title="Total Time"
            value={`${formatTime(stats.totalTime)}`}
            icon={<Clock className="w-6 h-6" />}
          />
          <StatCard
            title="Total Elevation"
            value={`${stats.totalElevation.toFixed(0)} m`}
            icon={<Mountain className="w-6 h-6" />}
          />
        </div>

        {/* Activity Types */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ActivityTypesCard activities={activities} />
          <RecentActivitiesCard activities={activities.slice(0, 5)} />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DistanceChart activities={activities} />
          <TimeChart activities={activities} />
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon }: { title: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="bg-card border border-border rounded-lg p-6 hover:bg-card-hover transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
        <div className="text-primary">{icon}</div>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  )
}

function ActivityTypesCard({ activities }: { activities: StravaActivity[] }) {
  const activityTypes = activities.reduce((acc, activity) => {
    acc[activity.type] = (acc[activity.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <BarChart3 className="w-5 h-5 text-primary" />
        Activity Types
      </h3>
      <div className="space-y-3">
        {Object.entries(activityTypes).map(([type, count]) => (
          <div key={type} className="flex justify-between items-center">
            <span className="text-gray-300 capitalize">{type}</span>
            <span className="font-semibold">{count}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function RecentActivitiesCard({ activities }: { activities: StravaActivity[] }) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Activity className="w-5 h-5 text-primary" />
        Recent Activities
      </h3>
      <div className="space-y-3">
        {activities.map((activity) => (
          <div key={activity.id} className="border-b border-border pb-3 last:border-0">
            <p className="font-medium capitalize">{activity.name}</p>
            <p className="text-sm text-gray-400">
              {activity.type} • {formatDate(activity.start_date)}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

function DistanceChart({ activities }: { activities: StravaActivity[] }) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">Distance Over Time</h3>
      <p className="text-gray-400">Chart implementation pending</p>
    </div>
  )
}

function TimeChart({ activities }: { activities: StravaActivity[] }) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">Time Distribution</h3>
      <p className="text-gray-400">Chart implementation pending</p>
    </div>
  )
}

function calculateStats(activities: StravaActivity[]) {
  return {
    totalActivities: activities.length,
    totalDistance: activities.reduce((sum, a) => sum + (a.distance / 1000), 0),
    totalTime: activities.reduce((sum, a) => sum + a.moving_time, 0),
    totalElevation: activities.reduce((sum, a) => sum + a.total_elevation_gain, 0),
  }
}

function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}
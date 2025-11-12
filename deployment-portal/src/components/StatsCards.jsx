import { Server, Activity, DollarSign, Users } from 'lucide-react'

export default function StatsCards({ regions }) {
  const totalCost = regions.reduce((sum, r) => sum + r.monthlyCost, 0)
  
  const stats = [
    {
      label: 'Active Regions',
      value: regions.length,
      icon: Server,
      color: 'bg-blue-500'
    },
    {
      label: 'System Uptime',
      value: '99.9%',
      icon: Activity,
      color: 'bg-green-500'
    },
    {
      label: 'Total Users',
      value: '847',
      icon: Users,
      color: 'bg-purple-500'
    },
    {
      label: 'Monthly Cost',
      value: `$${totalCost}`,
      icon: DollarSign,
      color: 'bg-yellow-500'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => {
        const Icon = stat.icon
        return (
          <div key={index} className="bg-slate-800 rounded-lg shadow-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">{stat.label}</p>
                <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

import { useState } from 'react'
import DeploymentMap from './components/DeploymentMap'
import DeploymentForm from './components/DeploymentForm'
import StatsCards from './components/StatsCards'
import DeploymentProgress from './components/DeploymentProgress'
import { Building2 } from 'lucide-react'

function App() {
  const [showForm, setShowForm] = useState(false)
  const [deploying, setDeploying] = useState(false)
  const [deploymentData, setDeploymentData] = useState(null)

  // Existing regions
  const regions = [
    {
      id: 'ny',
      name: 'Mount Sinai Hospital',
      city: 'New York',
      state: 'NY',
      coordinates: [40.7128, -74.0060],
      status: 'active',
      ip: '98.93.145.193',
      monthlyCost: 147
    },
    {
      id: 'ca',
      name: 'UCLA Medical Center',
      city: 'Los Angeles',
      state: 'CA',
      coordinates: [34.0522, -118.2437],
      status: 'active',
      ip: '3.88.0.224',
      monthlyCost: 147
    }
  ]

  const handleDeploy = (formData) => {
    setDeploymentData(formData)
    setShowForm(false)
    setDeploying(true)
    
    // Simulate deployment
    setTimeout(() => {
      setDeploying(false)
      alert(`✅ ${formData.hospitalName} deployed successfully!`)
    }, 10000)
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Building2 className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">Hospital Deployment Platform</h1>
                <p className="text-sm text-slate-400">Self-service multi-region infrastructure</p>
              </div>
            </div>
            <div className="flex space-x-4">
              <a href="https://github.com/henry-ibe/hipaa-hospital-system" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-white">
                Documentation
              </a>
              <button className="text-slate-400 hover:text-white">Logout</button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <StatsCards regions={regions} />

        {/* Main Content */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Map Section */}
          <div className="lg:col-span-2">
            <div className="bg-slate-800 rounded-lg shadow-xl overflow-hidden">
              <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">🗺️ Deployed Regions</h2>
                <button
                  onClick={() => setShowForm(!showForm)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                >
                  + Deploy New Region
                </button>
              </div>
              <div className="h-96">
                <DeploymentMap regions={regions} />
              </div>
            </div>

            {/* Region List */}
            <div className="mt-6 bg-slate-800 rounded-lg shadow-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Active Regions</h3>
              <div className="space-y-3">
                {regions.map(region => (
                  <div key={region.id} className="flex items-center justify-between p-4 bg-slate-700 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold">{region.state}</span>
                      </div>
                      <div>
                        <p className="font-semibold text-white">{region.name}</p>
                        <p className="text-sm text-slate-400">{region.city}, {region.state}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-green-400">● Active</p>
                      <p className="text-xs text-slate-400">{region.ip}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Form/Progress Section */}
          <div className="lg:col-span-1">
            {deploying ? (
              <DeploymentProgress data={deploymentData} />
            ) : showForm ? (
              <DeploymentForm onDeploy={handleDeploy} onCancel={() => setShowForm(false)} />
            ) : (
              <div className="bg-slate-800 rounded-lg shadow-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <button
                    onClick={() => setShowForm(true)}
                    className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-left"
                  >
                    🚀 Deploy New Region
                  </button>
                  <button className="w-full px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors text-left">
                    📊 View Metrics
                  </button>
                  <button className="w-full px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors text-left">
                    📜 Deployment History
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App

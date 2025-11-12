import { useState } from 'react'
import { MapPin, Building2, Cloud, Network, DollarSign } from 'lucide-react'

const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

const REGION_MAP = {
  'TX': 'us-south-1',
  'CA': 'us-west-2',
  'NY': 'us-east-1',
  'FL': 'us-east-1',
  'IL': 'us-east-2',
  'WA': 'us-west-2'
}

const API_ENDPOINT = 'https://mz94g5wdhj.execute-api.us-east-1.amazonaws.com/prod/deploy'

export default function DeploymentForm({ onDeploy, onCancel }) {
  const [formData, setFormData] = useState({
    city: '',
    state: '',
    hospitalName: '',
  })
  const [deploying, setDeploying] = useState(false)

  const awsRegion = REGION_MAP[formData.state] || 'us-east-1'
  const cidr = `10.${Math.floor(Math.random() * 200 + 2)}.0.0/16`
  const regionCode = formData.state.toLowerCase()
  
  const estimatedCost = {
    ec2: 25,
    alb: 22,
    dataTransfer: 10,
    cloudfront: 5,
    total: 62
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.city || !formData.state || !formData.hospitalName) {
      alert('Please fill in all fields!')
      return
    }

    setDeploying(true)

    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          city: formData.city,
          state: formData.state,
          hospitalName: formData.hospitalName,
          regionCode: regionCode,
          awsRegion: awsRegion,
          cidr: cidr
        })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        alert(`✅ ${data.message}

Deployment started for ${formData.city}, ${formData.state}!

Region Code: ${regionCode}
AWS Region: ${awsRegion}
CIDR Block: ${cidr}

Track progress at:
${data.workflowUrl}

The deployment will take approximately 10 minutes.`)
        
        onDeploy({
          ...formData,
          awsRegion,
          cidr,
          regionCode,
          estimatedCost: estimatedCost.total
        })
      } else {
        throw new Error(data.message || 'Deployment failed')
      }
    } catch (error) {
      console.error('Deployment error:', error)
      alert(`❌ Deployment failed: ${error.message}

Please try again or contact support.`)
    } finally {
      setDeploying(false)
    }
  }

  return (
    <div className="bg-slate-800 rounded-lg shadow-xl p-6">
      <h3 className="text-xl font-bold text-white mb-6">🚀 Deploy New Hospital Region</h3>
      
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            <MapPin className="w-4 h-4 inline mr-1" />
            City *
          </label>
          <input
            type="text"
            value={formData.city}
            onChange={(e) => setFormData({...formData, city: e.target.value})}
            placeholder="e.g., Dallas, Chicago"
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
            disabled={deploying}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            📍 State *
          </label>
          <select
            value={formData.state}
            onChange={(e) => setFormData({...formData, state: e.target.value})}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
            disabled={deploying}
          >
            <option value="">Select State</option>
            {US_STATES.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            <Building2 className="w-4 h-4 inline mr-1" />
            Hospital Name *
          </label>
          <input
            type="text"
            value={formData.hospitalName}
            onChange={(e) => setFormData({...formData, hospitalName: e.target.value})}
            placeholder="e.g., Baylor Medical Center"
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
            disabled={deploying}
          />
        </div>

        {formData.state && (
          <div className="bg-slate-700 rounded-lg p-4 space-y-2">
            <p className="text-sm font-medium text-green-400">✅ Auto-detected:</p>
            <div className="space-y-1 text-sm text-slate-300">
              <p><Cloud className="w-4 h-4 inline mr-1" />AWS Region: <span className="font-mono">{awsRegion}</span></p>
              <p><Network className="w-4 h-4 inline mr-1" />CIDR Block: <span className="font-mono">{cidr}</span></p>
              <p>Region Code: <span className="font-mono">{regionCode}</span></p>
            </div>
          </div>
        )}

        {formData.state && (
          <div className="bg-slate-700 rounded-lg p-4">
            <p className="text-sm font-medium text-slate-300 mb-3">
              <DollarSign className="w-4 h-4 inline mr-1" />
              Cost Estimate:
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between text-slate-400">
                <span>EC2 (t3.micro x2):</span>
                <span>${estimatedCost.ec2}/mo</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>ALB:</span>
                <span>${estimatedCost.alb}/mo</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Data Transfer:</span>
                <span>${estimatedCost.dataTransfer}/mo</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>CloudFront:</span>
                <span>${estimatedCost.cloudfront}/mo</span>
              </div>
              <div className="border-t border-slate-600 pt-2 flex justify-between text-white font-semibold">
                <span>Total:</span>
                <span>${estimatedCost.total}/mo</span>
              </div>
            </div>
          </div>
        )}

        <div className="flex space-x-3 pt-4">
          <button
            type="submit"
            disabled={deploying}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center"
          >
            {deploying ? (
              <>⏳ Deploying...</>
            ) : (
              <>🚀 Deploy Region</>
            )}
          </button>
          <button
            type="button"
            onClick={onCancel}
            disabled={deploying}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-gray-700 text-white rounded-lg font-medium transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

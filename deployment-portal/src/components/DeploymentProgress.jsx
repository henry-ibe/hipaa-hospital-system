import { useState, useEffect } from 'react'
import { CheckCircle, Clock, Loader } from 'lucide-react'

export default function DeploymentProgress({ data }) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    { name: 'VPC Created', duration: 1000 },
    { name: 'Subnets Created', duration: 1500 },
    { name: 'Security Groups Configured', duration: 1000 },
    { name: 'EC2 Instances Launching', duration: 2000 },
    { name: 'Load Balancer Provisioning', duration: 2000 },
    { name: 'CloudFront Distribution', duration: 1500 },
    { name: 'Application Deployment', duration: 1000 },
    { name: 'Monitoring Configuration', duration: 1000 }
  ]

  useEffect(() => {
    const totalDuration = steps.reduce((sum, step) => sum + step.duration, 0)
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + (100 / totalDuration) * 100
      })
    }, 100)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    let elapsed = 0
    steps.forEach((step, index) => {
      elapsed += step.duration
      setTimeout(() => setCurrentStep(index + 1), elapsed)
    })
  }, [])

  return (
    <div className="bg-slate-800 rounded-lg shadow-xl p-6">
      <h3 className="text-xl font-bold text-white mb-6">
        ⏳ Deploying {data.city} Region...
      </h3>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-slate-400 mb-2">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
          <div
            className="bg-blue-600 h-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-3">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center space-x-3">
            {index < currentStep ? (
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
            ) : index === currentStep ? (
              <Loader className="w-5 h-5 text-blue-400 animate-spin flex-shrink-0" />
            ) : (
              <Clock className="w-5 h-5 text-slate-600 flex-shrink-0" />
            )}
            <span className={`text-sm ${
              index < currentStep ? 'text-green-400' :
              index === currentStep ? 'text-blue-400' :
              'text-slate-500'
            }`}>
              {step.name}
            </span>
          </div>
        ))}
      </div>

      {/* Info */}
      <div className="mt-6 p-4 bg-slate-700 rounded-lg space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-400">Region:</span>
          <span className="text-white font-mono">{data.regionCode}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">CIDR:</span>
          <span className="text-white font-mono">{data.cidr}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">AWS Region:</span>
          <span className="text-white font-mono">{data.awsRegion}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Est. Time:</span>
          <span className="text-white">~10 minutes</span>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-6 flex space-x-3">
        <button className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors">
          📊 View Logs
        </button>
        <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-colors">
          ❌ Cancel
        </button>
      </div>
    </div>
  )
}

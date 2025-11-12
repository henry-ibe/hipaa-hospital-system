import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons in Leaflet with bundlers
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

export default function DeploymentMap({ regions }) {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)

  useEffect(() => {
    if (!mapRef.current) return

    // Initialize map
    if (!mapInstanceRef.current) {
      mapInstanceRef.current = L.map(mapRef.current).setView([39.8283, -98.5795], 4)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        className: 'map-tiles'
      }).addTo(mapInstanceRef.current)
    }

    // Clear existing markers
    mapInstanceRef.current.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        mapInstanceRef.current.removeLayer(layer)
      }
    })

    // Add markers for each region
    regions.forEach(region => {
      const marker = L.marker(region.coordinates).addTo(mapInstanceRef.current)
      
      marker.bindPopup(`
        <div style="font-family: system-ui; padding: 4px;">
          <strong style="font-size: 14px; color: #1e293b;">${region.name}</strong>
          <p style="margin: 4px 0; font-size: 12px; color: #475569;">
            ${region.city}, ${region.state}
          </p>
          <p style="margin: 4px 0; font-size: 11px; color: #64748b;">
            IP: ${region.ip}
          </p>
          <span style="display: inline-block; margin-top: 4px; padding: 2px 8px; background: #10b981; color: white; border-radius: 12px; font-size: 10px;">
            ● Active
          </span>
        </div>
      `)
    })

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [regions])

  return (
    <div 
      ref={mapRef} 
      className="w-full h-full"
      style={{ 
        background: '#1e293b',
        minHeight: '400px'
      }}
    />
  )
}

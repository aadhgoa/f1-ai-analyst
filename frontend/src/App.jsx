import { useState } from 'react'
import Header from './components/Header'
import ControlPanel from './components/ControlPanel'
import Dashboard from './components/Dashboard'
import ReportZone from './components/ReportZone'
import EmptyState from './components/EmptyState'
import './index.css'

function App() {
  const [year, setYear] = useState('2024')
  const [gp, setGp] = useState('Japan')
  
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)

  const [dashData, setDashData] = useState(null)
  const [dashLoading, setDashLoading] = useState(false)
  const [dashError, setDashError] = useState(null)

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const analyzeRace = () => {
    setDashLoading(true)
    setDashError(null)
    setDashData(null)
    
    setLoading(true)
    setError(null)
    setReport(null)

    fetchDashboardData()
    fetchRaceReport()
  }

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/dashboard-data?year=${year}&gp=${gp}`)
      if (!response.ok) throw new Error('Failed to load telemetry dashboard')
      const data = await response.json()
      setDashData(data)
    } catch (err) {
      setDashError(err.message)
    } finally {
      setDashLoading(false)
    }
  }

  const fetchRaceReport = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/race-summary?year=${year}&gp=${gp}`)
      if (!response.ok) throw new Error('Agent failed to complete race analysis')
      const data = await response.json()
      setReport(data.summary)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen pt-8 pb-16 px-4 sm:px-8">
      <Header />
      
      <ControlPanel 
        year={year} 
        setYear={setYear} 
        gp={gp} 
        setGp={setGp} 
        analyzeRace={analyzeRace} 
        loading={loading} 
        dashLoading={dashLoading} 
      />

      <main className="max-w-5xl mx-auto space-y-12">
        <Dashboard 
          dashData={dashData} 
          dashLoading={dashLoading} 
          dashError={dashError} 
        />

        <ReportZone 
          loading={loading} 
          error={error} 
          report={report} 
        />

        <EmptyState 
          dashData={dashData} 
          dashLoading={dashLoading} 
          report={report} 
          loading={loading} 
          error={error} 
        />
      </main>
    </div>
  )
}

export default App

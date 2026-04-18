import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Search, Loader2 } from 'lucide-react';

const DoctorDashboard: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    fetch(`http://localhost:5000/api/dashboard-data?role=doctor&user_id=${user?.id}`)
      .then(res => res.json())
      .then(res => {
        if(res.status === 'success') {
          setData(res.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [user]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    try {
      const res = await fetch('http://localhost:5000/api/patient-history/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery })
      });
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch (e) {
      console.error(e);
    }
    setSearching(false);
  };

  if(loading) return <div className="text-white p-8">Loading Doctor Dashboard...</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Clinical Dashboard - Dr. {user?.name}
        </h1>
        <p className="text-sm text-white/70 mt-1">Total Assigned Patients: {data?.patients_count || 0}</p>
      </div>

      {/* Semantic Search */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Patient Intelligence Search</h2>
        <form onSubmit={handleSearch} className="flex gap-4">
          <input 
            type="text" 
            placeholder="e.g. 'Show me diabetic patients with high blood pressure'"
            className="flex-1 bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-cyan-500 transition-colors"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button 
            type="submit"
            disabled={searching}
            className="px-6 py-3 bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-lg hover:bg-cyan-500/30 transition-colors font-medium flex items-center gap-2"
          >
            {searching ? <Loader2 className="w-5 h-5 animate-spin"/> : <Search className="w-5 h-5"/>}
            Query NLP
          </button>
        </form>

        {/* Results */}
        {searchResults.length > 0 && (
          <div className="mt-6 space-y-4">
            <h3 className="text-sm font-semibold text-white/60 uppercase tracking-widest">Search Results</h3>
            {searchResults.map((res: any, idx: number) => (
              <div key={idx} className="bg-white/5 p-4 rounded-lg flex justify-between">
                <div>
                  <p className="text-white font-medium">Patient ID: {res.patient_id}</p>
                  <p className="text-sm text-white/70 mt-1">{res.description}</p>
                </div>
                <div className="text-right text-sm text-cyan-400">
                  {res.diagnosis && <span className="px-2 py-1 bg-cyan-500/10 rounded uppercase inline-block">{res.diagnosis}</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Records */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Recent Patient Records</h2>
        {data?.recent_records?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.recent_records.map((r: any, idx: number) => (
              <div key={idx} className="bg-black/20 p-4 border border-white/5 rounded-xl">
                <div className="flex justify-between text-xs text-white/40 mb-2">
                  <span>{new Date(r.date || Date.now()).toLocaleDateString()}</span>
                  <span>Patient #{r.patient_id?.substring(0,6) || "N/A"}</span>
                </div>
                <p className="text-white text-sm">{r.diagnosis || "No Diagnosis Logged"}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-white/40 text-sm">No recent records available.</p>
        )}
      </div>
    </div>
  );
};

export default DoctorDashboard;

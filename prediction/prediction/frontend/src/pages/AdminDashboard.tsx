import React, { useState, useEffect } from 'react';
import { Activity, Mail, Search, Shield, ChevronDown, ChevronUp, Users, TrendingUp, AlertTriangle } from 'lucide-react';
import { getAdminPatientsAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, LineChart, Line, ResponsiveContainer } from 'recharts';
import DoctorPatientAssignment from '../components/DoctorPatientAssignment';

interface PatientData {
  patient_id: string;
  patient_name: string;
  doctor_id: string;
  doctor_name: string;
  doctor_email: string;
  timestamp: string;
  disease: string;
  risk: string;
  confidence: number;
  glucose: number;
  blood_pressure: number;
  bmi: number;
  matched_drugs: string[];
  recommendations: any;
  auto_medications: any[];
}

interface AdminData {
  patients: PatientData[];
  total_count: number;
}

const AdminDashboard: React.FC = () => {
  const [adminData, setAdminData] = useState<AdminData | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [diseaseFilter, setDiseaseFilter] = useState('all');
  const [expandedPatientId, setExpandedPatientId] = useState<string | null>(null);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      const result = await getAdminPatientsAPI();
      
      if (result && result.status === 'success') {
        setAdminData(result.data);
      } else {
        console.error('Failed to fetch admin data:', result?.error || 'Unknown error');
      }
    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredPatients = adminData?.patients?.filter(patient => {
    const matchesSearch = 
      patient.patient_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (patient.patient_name && patient.patient_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      patient.doctor_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.doctor_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.disease.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRisk = riskFilter === 'all' || patient.risk === riskFilter;
    const matchesDisease = diseaseFilter === 'all' || patient.disease === diseaseFilter;
    
    return matchesSearch && matchesRisk && matchesDisease;
  }) || [];

  // Prepare data for charts
  const riskDistribution = [
    { name: 'High', value: adminData?.patients?.filter(p => p.risk === 'High').length || 0, color: '#ef4444' },
    { name: 'Moderate', value: adminData?.patients?.filter(p => p.risk === 'Moderate').length || 0, color: '#f59e0b' },
    { name: 'Low', value: adminData?.patients?.filter(p => p.risk === 'Low').length || 0, color: '#10b981' }
  ];

  const diseaseDistribution = adminData?.patients?.reduce((acc: any[], patient) => {
    const existing = acc.find(item => item.name === patient.disease);
    if (existing) {
      existing.value += 1;
    } else {
      acc.push({ name: patient.disease, value: 1 });
    }
    return acc;
  }, []) || [];

  const doctorPatientCount = adminData?.patients?.reduce((acc: any[], patient) => {
    const existing = acc.find(item => item.name === patient.doctor_name);
    if (existing) {
      existing.patients += 1;
    } else {
      acc.push({ name: patient.doctor_name, patients: 1 });
    }
    return acc;
  }, []) || [];

  const riskBadge = (risk: string) => {
    if (risk === 'High') return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider bg-red-50 text-red-600 border border-red-100">
        <Shield size={11} /> High
      </span>
    );
    if (risk === 'Moderate') return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider bg-amber-50 text-amber-600 border border-amber-100">
        <Activity size={11} /> Moderate
      </span>
    );
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider bg-emerald-50 text-emerald-600 border border-emerald-100">
        <Shield size={11} /> Low
      </span>
    );
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-gray-900 tracking-tight">
            Admin Dashboard
          </h1>
          <p className="text-sm text-gray-600 mt-0.5">
            Manage all patients and monitor healthcare activities
          </p>
        </div>
        {adminData && (
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">{adminData.total_count}</div>
            <div className="text-xs text-gray-500 uppercase tracking-wider">Total Patients</div>
          </div>
        )}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({name, value}) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Disease Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={diseaseDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Doctor Workload</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={doctorPatientCount}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="patients" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-sm flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
            <Search size={16} />
          </div>
          <input
            type="text"
            className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 text-sm text-gray-900 placeholder-gray-500 transition-all"
            placeholder="Search patients, doctors, or diseases..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
        </div>
        <select
          value={riskFilter}
          onChange={e => setRiskFilter(e.target.value)}
          className="px-4 py-2.5 bg-white border border-gray-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 text-sm text-gray-900 transition-all"
        >
          <option value="all">All Risk Levels</option>
          <option value="High">High Risk Only</option>
          <option value="Moderate">Moderate Risk Only</option>
          <option value="Low">Low Risk Only</option>
        </select>
        <select
          value={diseaseFilter}
          onChange={e => setDiseaseFilter(e.target.value)}
          className="px-4 py-2.5 bg-white border border-gray-300 rounded-xl outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 text-sm text-gray-900 transition-all"
        >
          <option value="all">All Diseases</option>
          <option value="diabetes">Diabetes</option>
          <option value="heart">Heart Disease</option>
          <option value="mental">Mental Health</option>
        </select>
      </div>

      {/* Patient Table */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[10px] text-gray-600 uppercase tracking-widest bg-gray-50 border-b border-gray-200 font-bold">
              <tr>
                <th className="px-5 py-4">Patient ID</th>
                <th className="px-5 py-4">Patient Name</th>
                <th className="px-5 py-4">Doctor Name</th>
                <th className="px-5 py-4">Doctor Email</th>
                <th className="px-5 py-4">Date</th>
                <th className="px-5 py-4">Disease</th>
                <th className="px-5 py-4">Risk</th>
                <th className="px-5 py-4">Confidence</th>
                <th className="px-5 py-4">Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatients.length > 0 ? (
                filteredPatients.map((patient) => (
                  <React.Fragment key={patient.patient_id}>
                    <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      <td className="px-5 py-4 font-medium text-gray-900">{patient.patient_id}</td>
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-2">
                          <div className="h-6 w-6 rounded-full bg-green-100 flex items-center justify-center text-green-600 text-xs font-bold">
                            {patient.patient_name ? patient.patient_name.charAt(0).toUpperCase() : 'P'}
                          </div>
                          <span className="text-gray-900">{patient.patient_name || 'Unknown Patient'}</span>
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-2">
                          <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-xs font-bold">
                            {patient.doctor_name.charAt(0).toUpperCase()}
                          </div>
                          <span className="text-gray-900">{patient.doctor_name}</span>
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-1 text-gray-600">
                          <Mail size={12} />
                          <span className="text-xs">{patient.doctor_email}</span>
                        </div>
                      </td>
                      <td className="px-5 py-4 text-gray-600">
                        {new Date(patient.timestamp).toLocaleDateString()}
                      </td>
                      <td className="px-5 py-4">
                        <span className="inline-block text-xs bg-gray-100 border border-gray-200 rounded-full px-2.5 py-0.5 font-medium capitalize text-gray-700">
                          {patient.disease}
                        </span>
                      </td>
                      <td className="px-5 py-4">{riskBadge(patient.risk)}</td>
                      <td className="px-5 py-4">
                        <span className="font-semibold text-gray-900">{(patient.confidence * 100).toFixed(1)}%</span>
                      </td>
                      <td className="px-5 py-4">
                        <button
                          type="button"
                          onClick={() => setExpandedPatientId(expandedPatientId === patient.patient_id ? null : patient.patient_id)}
                          className="inline-flex items-center gap-1 rounded-lg border border-gray-300 px-2 py-1 text-xs font-semibold text-gray-600 hover:bg-gray-50"
                        >
                          {expandedPatientId === patient.patient_id ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                          {expandedPatientId === patient.patient_id ? 'Hide' : 'Expand'}
                        </button>
                      </td>
                    </tr>

                    {expandedPatientId === patient.patient_id && (
                      <tr className="border-b border-gray-100 bg-gray-50/60">
                        <td colSpan={9} className="px-5 py-4">
                          <div className="grid gap-4 md:grid-cols-3">
                            <div className="rounded-xl border border-gray-200 bg-white p-3">
                              <p className="text-[10px] uppercase tracking-widest text-blue-600 mb-2 font-semibold">Patient Metrics</p>
                              <div className="space-y-1 text-xs">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Glucose:</span>
                                  <span className="font-medium text-gray-900">{patient.glucose} mg/dL</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Blood Pressure:</span>
                                  <span className="font-medium text-gray-900">{patient.blood_pressure} mmHg</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">BMI:</span>
                                  <span className="font-medium text-gray-900">{patient.bmi}</span>
                                </div>
                              </div>
                            </div>

                            <div className="rounded-xl border border-blue-200 bg-blue-50 p-3">
                              <p className="text-[10px] uppercase tracking-widest text-blue-700 mb-2 font-semibold">Medications</p>
                              {patient.auto_medications && patient.auto_medications.length > 0 ? (
                                <div className="space-y-2">
                                  {patient.auto_medications.slice(0, 3).map((med, idx) => (
                                    <div key={`med-${idx}`} className="rounded-lg border border-gray-200 p-2">
                                      <p className="text-xs font-semibold text-gray-900">{med.name || 'Medication'}</p>
                                      <p className="text-xs text-gray-600">{med.dosage || 'Dose N/A'} {med.frequency ? `- ${med.frequency}` : ''}</p>
                                    </div>
                                  ))}
                                </div>
                              ) : patient.matched_drugs && patient.matched_drugs.length > 0 ? (
                                <div className="space-y-1">
                                  {patient.matched_drugs.slice(0, 3).map((drug, idx) => (
                                    <p key={`drug-${idx}`} className="text-xs text-gray-700">- {drug}</p>
                                  ))}
                                </div>
                              ) : (
                                <p className="text-xs text-gray-600">No medications recorded</p>
                              )}
                            </div>

                            <div className="rounded-xl border border-green-200 bg-green-50 p-3">
                              <p className="text-[10px] uppercase tracking-widest text-green-700 mb-2 font-semibold">Recommendations</p>
                              {patient.recommendations && (
                                <div className="space-y-1">
                                  {[
                                    ...(patient.recommendations.lifestyle || []),
                                    ...(patient.recommendations.medical || []),
                                    ...(patient.recommendations.precautions || [])
                                  ].slice(0, 4).map((item, idx) => (
                                    <p key={`rec-${idx}`} className="text-xs text-green-800">- {item}</p>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="px-6 py-14 text-center">
                    <p className="text-gray-600 text-sm font-medium">No patients found.</p>
                    <p className="text-gray-500 text-xs mt-1">Adjust your filters or wait for patient data to be available.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Doctor-Patient Assignment Management */}
      <DoctorPatientAssignment userRole="admin" />
    </div>
  );
};

export default AdminDashboard;

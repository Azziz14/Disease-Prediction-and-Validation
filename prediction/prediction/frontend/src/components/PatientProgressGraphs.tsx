import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, Calendar, Activity, Heart, Brain } from 'lucide-react';

interface PatientData {
  timestamp: string;
  glucose?: number;
  blood_pressure?: number;
  bmi?: number;
  risk: string;
  confidence: number;
  disease: string;
}

interface PatientProgressGraphsProps {
  patientId?: string;
  patientData?: PatientData[];
  timeRange: 'week' | 'month' | 'quarter';
  onTimeRangeChange?: (range: 'week' | 'month' | 'quarter') => void;
}

const PatientProgressGraphs: React.FC<PatientProgressGraphsProps> = ({ 
  patientId, 
  patientData = [], 
  timeRange = 'month',
  onTimeRangeChange 
}) => {
  const [processedData, setProcessedData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    processPatientData();
  }, [patientData, timeRange]);

  const processPatientData = () => {
    setLoading(true);
    
    if (!patientData || patientData.length === 0) {
      setProcessedData([]);
      setLoading(false);
      return;
    }

    // Sort data by timestamp
    const sortedData = [...patientData].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    // Filter data based on time range
    const now = new Date();
    let cutoffDate = new Date();

    switch (timeRange) {
      case 'week':
        cutoffDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        cutoffDate.setMonth(now.getMonth() - 1);
        break;
      case 'quarter':
        cutoffDate.setMonth(now.getMonth() - 3);
        break;
    }

    const filteredData = sortedData.filter(item => 
      new Date(item.timestamp) >= cutoffDate
    );

    // Process data for charts
    const chartData = filteredData.map((item, index) => {
      const date = new Date(item.timestamp);
      return {
        date: date.toLocaleDateString(),
        fullDate: item.timestamp,
        glucose: item.glucose || 0,
        bloodPressure: item.blood_pressure || 0,
        bmi: item.bmi || 0,
        risk: item.risk,
        confidence: item.confidence,
        riskScore: getRiskScore(item.risk),
        improvement: calculateImprovement(filteredData, index)
      };
    });

    setProcessedData(chartData);
    setLoading(false);
  };

  const getRiskScore = (risk: string): number => {
    switch (risk) {
      case 'Low': return 1;
      case 'Moderate': return 2;
      case 'High': return 3;
      default: return 0;
    }
  };

  const calculateImprovement = (data: PatientData[], currentIndex: number): number => {
    if (currentIndex === 0) return 0;
    
    const current = data[currentIndex];
    const previous = data[currentIndex - 1];
    
    // Simple improvement calculation based on risk level change
    const currentScore = getRiskScore(current.risk);
    const previousScore = getRiskScore(previous.risk);
    
    return previousScore - currentScore; // Positive means improvement
  };

  const getOverallTrend = (): 'improving' | 'declining' | 'stable' => {
    if (processedData.length < 2) return 'stable';
    
    const recent = processedData.slice(-3);
    const avgImprovement = recent.reduce((sum, item) => sum + item.improvement, 0) / recent.length;
    
    if (avgImprovement > 0.1) return 'improving';
    if (avgImprovement < -0.1) return 'declining';
    return 'stable';
  };

  const getDiseaseIcon = (disease: string) => {
    switch (disease) {
      case 'diabetes': return <Activity className="text-blue-500" />;
      case 'heart': return <Heart className="text-red-500" />;
      case 'mental': return <Brain className="text-purple-500" />;
      default: return <Activity className="text-gray-500" />;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="text-green-500" />;
      case 'declining': return <TrendingDown className="text-red-500" />;
      default: return <Activity className="text-yellow-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const overallTrend = getOverallTrend();
  const latestData = processedData[processedData.length - 1];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Patient Progress Analysis</h3>
          <p className="text-sm text-gray-600">Track health metrics and improvement over time</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={timeRange}
            onChange={(e) => onTimeRangeChange?.(e.target.value as 'week' | 'month' | 'quarter')}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Overall Trend</p>
              <p className="text-lg font-semibold text-gray-900 capitalize">{overallTrend}</p>
            </div>
            <div className="p-2 bg-gray-50 rounded-lg">
              {getTrendIcon(overallTrend)}
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Current Risk Level</p>
              <p className="text-lg font-semibold text-gray-900">{latestData?.risk || 'N/A'}</p>
            </div>
            <div className="p-2 bg-gray-50 rounded-lg">
              {latestData && getDiseaseIcon(latestData.disease || 'diabetes')}
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Assessments</p>
              <p className="text-lg font-semibold text-gray-900">{processedData.length}</p>
            </div>
            <div className="p-2 bg-gray-50 rounded-lg">
              <Calendar className="text-gray-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      {processedData.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Level Over Time */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Risk Level Progression</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={processedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 4]} ticks={[0, 1, 2, 3]} tickFormatter={(value) => ['None', 'Low', 'Moderate', 'High'][value]} />
                <Tooltip 
                  formatter={(value: any) => [
                    ['None', 'Low', 'Moderate', 'High'][value] || value,
                    'Risk Level'
                  ]}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="riskScore" 
                  stroke="#ef4444" 
                  strokeWidth={2}
                  dot={{ fill: '#ef4444' }}
                  name="Risk Level"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Health Metrics */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Health Metrics</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={processedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="glucose" stroke="#3b82f6" name="Glucose" />
                <Line type="monotone" dataKey="bloodPressure" stroke="#10b981" name="Blood Pressure" />
                <Line type="monotone" dataKey="bmi" stroke="#f59e0b" name="BMI" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Improvement Trend */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Improvement Trend</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={processedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="improvement" fill="#10b981" name="Improvement Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Confidence Levels */}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Prediction Confidence</h4>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={processedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                <Tooltip formatter={(value: any) => [`${(value * 100).toFixed(1)}%`, 'Confidence']} />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="confidence" 
                  stroke="#8b5cf6" 
                  fill="#8b5cf6" 
                  fillOpacity={0.3}
                  name="Confidence"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="bg-white p-8 rounded-lg border border-gray-200 text-center">
          <Activity className="mx-auto text-gray-300 mb-4" size={48} />
          <p className="text-gray-600">No progress data available for the selected time period</p>
          <p className="text-sm text-gray-500 mt-1">Patient assessments will appear here once available</p>
        </div>
      )}

      {/* Insights */}
      {processedData.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Key Insights</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li> Patient shows {overallTrend === 'improving' ? 'positive' : overallTrend === 'declining' ? 'negative' : 'stable'} health trend</li>
            <li> Current risk level: {latestData?.risk} with {(latestData?.confidence || 0) * 100}% confidence</li>
            <li> Total of {processedData.length} assessments in the selected period</li>
            {processedData.length >= 2 && (
              <li> Average improvement score: {(processedData.reduce((sum, item) => sum + item.improvement, 0) / processedData.length).toFixed(2)}</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PatientProgressGraphs;

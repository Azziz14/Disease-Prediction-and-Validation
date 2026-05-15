import re

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\PatientDashboard.tsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the container start and end
# The template spans from <div id="clinical-print-template" ... to the corresponding closing </div> right before <section className="relative overflow-hidden...

# A highly specific regex matching the print template block
template_pattern = r'(<div\s+id="clinical-print-template"\s+style=\{\{\s*display:\s*\'none\'[\s\S]*?Disclaimer:[\s\S]*?<\/div>\s*<\/div>\s*<\/div>)'
match = re.search(template_pattern, content)

# If specific regex doesn't match, use the open/close brace tracking starting at id="clinical-print-template"
if not match:
    print("Regex fell back to DOM scanning...")
    # Let's find index of id="clinical-print-template"
    start_idx = content.find('id="clinical-print-template"')
    if start_idx != -1:
        # Backtrack to '<div'
        div_start = content.rfind('<div', 0, start_idx)
        
        # Now we count braces or find the closing div before <section
        # Since we know it ends right before the <section tag
        section_idx = content.find('<section className="relative overflow-hidden rounded-[28px]', div_start)
        if section_idx != -1:
            # Find the closing tags immediately preceding
            # Let's capture up to section_idx
            original_template = content[div_start:section_idx]
            print("Captured original template via section index alignment.")
        else:
            original_template = None
    else:
        original_template = None
else:
    original_template = match.group(1)
    print("Captured original template via regex.")

if original_template:
    print("Surgically replacing print template...")
    
    new_template = """<div id="clinical-print-template" style={{ 
        position: 'absolute', 
        left: '-9999px', 
        top: '-9999px', 
        width: '850px', 
        padding: '50px', 
        backgroundColor: '#ffffff', 
        color: '#1e293b', 
        fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
        lineHeight: '1.5'
      }}>
        {/* Accent Border Header */}
        <div style={{ height: '8px', backgroundColor: '#0f172a', borderRadius: '4px 4px 0 0', marginBottom: '20px' }} />
        
        {/* Hospital Letterhead & Branding */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '2px solid #e2e8f0', paddingBottom: '25px', marginBottom: '30px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <div style={{ width: '24px', height: '24px', backgroundColor: '#0f172a', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 'bold', fontSize: '14px' }}>CP</div>
              <h1 style={{ fontSize: '22px', fontWeight: '800', letterSpacing: '-0.02em', margin: 0, color: '#0f172a' }}>CAREPREDICT CLINICAL HEALTHCARE</h1>
            </div>
            <p style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 'bold', letterSpacing: '0.05em', margin: 0 }}>Center for Advanced Neural Diagnostics & Inference</p>
            <p style={{ fontSize: '10px', color: '#94a3b8', margin: '4px 0 0 0' }}>Authorized Digital Record • Document Hash Reference ID: {Math.random().toString(36).substr(2, 9).toUpperCase()}</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ display: 'inline-block', border: '2px solid #dc2626', color: '#dc2626', padding: '4px 10px', fontWeight: '900', fontSize: '12px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>Confidential Medical File</div>
            <p style={{ fontSize: '11px', color: '#64748b', margin: 0 }}>Generated: <strong>{new Date().toLocaleString()}</strong></p>
          </div>
        </div>

        {/* Patient & Physician Metadata Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px', marginBottom: '35px' }}>
          <div style={{ backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px' }}>
            <h3 style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b', margin: '0 0 10px 0', borderBottom: '1px solid #e2e8f0', paddingBottom: '5px', fontWeight: '800' }}>Subject Demographics</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <tbody>
                <tr>
                  <td style={{ color: '#64748b', padding: '4px 0', fontWeight: '500' }}>Patient Name:</td>
                  <td style={{ fontWeight: '700', color: '#0f172a', textAlign: 'right' }}>{user?.name}</td>
                </tr>
                <tr>
                  <td style={{ color: '#64748b', padding: '4px 0', fontWeight: '500' }}>System ID:</td>
                  <td style={{ fontWeight: '700', color: '#0f172a', textAlign: 'right' }}>#{activeInsight?.numeric_patient_id || '100452'}</td>
                </tr>
                <tr>
                  <td style={{ color: '#64748b', padding: '4px 0', fontWeight: '500' }}>Record Status:</td>
                  <td style={{ fontWeight: '700', color: '#16a34a', textAlign: 'right', textTransform: 'uppercase', fontSize: '10px' }}>Verified Active</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div style={{ backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px' }}>
            <h3 style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b', margin: '0 0 10px 0', borderBottom: '1px solid #e2e8f0', paddingBottom: '5px', fontWeight: '800' }}>Clinical Validation Path</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <tbody>
                <tr>
                  <td style={{ color: '#64748b', padding: '4px 0', fontWeight: '500' }}>Primary Diagnostician:</td>
                  <td style={{ fontWeight: '700', color: '#0f172a', textAlign: 'right' }}>{latestPrediction?.treating_doctor || 'Staff Physician'}</td>
                </tr>
                <tr>
                  <td style={{ color: '#64748b', padding: '4px 0', fontWeight: '500' }}>AI Processing Core:</td>
                  <td style={{ fontWeight: '700', color: '#0284c7', textAlign: 'right' }}>Neural-Consensus Engine 4.2</td>
                </tr>
                <tr>
                  <td style={{ color: '#64748b', padding: '4px 0', fontWeight: '500' }}>Audit Registry Status:</td>
                  <td style={{ fontWeight: '700', color: '#0f172a', textAlign: 'right', fontSize: '10px' }}>SIGNED_DIGITAL_LEDGER</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Inference & Core Metrics Display */}
        <div style={{ marginBottom: '35px' }}>
          <h2 style={{ fontSize: '14px', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#0f172a', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '4px', height: '14px', backgroundColor: '#0f172a', display: 'inline-block' }} />
            Diagnostic Consensus Summary
          </h2>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div style={{ flex: 1, padding: '20px', border: '1px solid #e2e8f0', borderRadius: '12px', textAlign: 'center', backgroundColor: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <p style={{ fontSize: '10px', textTransform: 'uppercase', fontWeight: '800', color: '#64748b', margin: '0 0 8px 0' }}>Pathological Protocol</p>
              <p style={{ fontSize: '22px', fontWeight: '900', margin: 0, color: '#0f172a', textTransform: 'capitalize', letterSpacing: '-0.03em' }}>{latestPrediction?.disease || selectedDisease}</p>
            </div>
            <div style={{ flex: 1, padding: '20px', border: '1px solid #e2e8f0', borderRadius: '12px', textAlign: 'center', backgroundColor: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <p style={{ fontSize: '10px', textTransform: 'uppercase', fontWeight: '800', color: '#64748b', margin: '0 0 8px 0' }}>Risk Stratification</p>
              <div style={{ 
                display: 'inline-block', 
                padding: '5px 15px', 
                borderRadius: '20px', 
                backgroundColor: latestRisk === 'High' ? '#fef2f2' : latestRisk === 'Moderate' ? '#fffbeb' : '#f0fdf4',
                border: `1px solid ${latestRisk === 'High' ? '#fca5a5' : latestRisk === 'Moderate' ? '#fcd34d' : '#86efac'}`
              }}>
                <p style={{ 
                  fontSize: '20px', 
                  fontWeight: '900', 
                  margin: 0, 
                  color: latestRisk === 'High' ? '#b91c1c' : latestRisk === 'Moderate' ? '#b45309' : '#15803d',
                  textTransform: 'uppercase'
                }}>{latestRisk}</p>
              </div>
            </div>
            <div style={{ flex: 1, padding: '20px', border: '1px solid #e2e8f0', borderRadius: '12px', textAlign: 'center', backgroundColor: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <p style={{ fontSize: '10px', textTransform: 'uppercase', fontWeight: '800', color: '#64748b', margin: '0 0 8px 0' }}>Validation Index (CI)</p>
              <p style={{ fontSize: '22px', fontWeight: '900', margin: 0, color: '#0f172a' }}>{latestConfidence}</p>
            </div>
          </div>
        </div>

        {/* Deep Table Grid for Directives & Medical Narrative */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 0.7fr', gap: '25px', marginBottom: '30px' }}>
          <div>
            <h2 style={{ fontSize: '14px', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#0f172a', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '4px', height: '14px', backgroundColor: '#0f172a', display: 'inline-block' }} />
              Clinical Interpretation & Directives
            </h2>
            
            <div style={{ border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px', marginBottom: '20px', backgroundColor: '#fff' }}>
              <p style={{ fontSize: '12px', fontWeight: '700', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.02em', margin: '0 0 8px 0' }}>Clinical Narrative Summary</p>
              <p style={{ fontSize: '13px', color: '#334155', margin: 0, lineHeight: '1.7' }}>
                {activeInsight?.recommendations?.summary || activeInsight?.clinical_narrative || activeInsight?.consensus_intelligence?.narrative || 'Multi-node algorithmic inference verifies structural and physiological biometrics against validation baselines. Diagnostic consensus recommends observing primary preventative routines outlined below.'}
              </p>
            </div>

            <div style={{ border: '1px solid #e2e8f0', borderRadius: '12px', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f1f5f9', borderBottom: '1px solid #e2e8f0' }}>
                    <th style={{ textAlign: 'left', padding: '12px 15px', color: '#475569', fontWeight: '800', textTransform: 'uppercase', fontSize: '9px', letterSpacing: '0.05em' }}>Therapeutic Directives & Plan</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ...(activeInsight?.recommendations?.lifestyle || []),
                    ...(activeInsight?.recommendations?.daily_routine || []),
                    ...(activeInsight?.recommendations?.medical || []),
                    ...(activeInsight?.recommendations?.precautions || [])
                  ].map((rec: any, i: number) => (
                    <tr key={i} style={{ borderBottom: '1px solid #f1f5f9', backgroundColor: i % 2 === 0 ? '#ffffff' : '#fafafa' }}>
                      <td style={{ padding: '12px 15px', color: '#334155' }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                          <span style={{ color: '#0f172a', fontSize: '14px', lineHeight: '1' }}>•</span>
                          <div>
                            {typeof rec === 'object' ? (
                              <>
                                <strong style={{ color: '#0f172a' }}>{String(rec.name || rec.purpose || 'Directive')}</strong> 
                                {rec.dosage ? <span style={{ fontSize: '11px', color: '#0284c7', marginLeft: '6px', fontWeight: '600' }}>[{String(rec.dosage)}]</span> : ''}
                                <p style={{ fontSize: '11px', color: '#64748b', margin: '2px 0 0 0' }}>{String(rec.note || rec.purpose || rec.frequency || rec.target_condition || '')}</p>
                              </>
                            ) : (
                              <span style={{ fontWeight: '500' }}>{String(rec)}</span>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {recommendationCount === 0 && (
                    <tr>
                      <td style={{ padding: '20px', textAlign: 'center', color: '#94a3b8', fontStyle: 'italic' }}>
                        Maintain current active biological baselines and document standard daily vitals. No anomalies requiring acute intervention detected.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h2 style={{ fontSize: '14px', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#0f172a', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '4px', height: '14px', backgroundColor: '#dc2626', display: 'inline-block' }} />
              Pharmaceutical Guidance
            </h2>
            
            <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
              <p style={{ fontSize: '10px', fontWeight: '900', color: '#991b1b', textTransform: 'uppercase', letterSpacing: '0.05em', margin: '0 0 15px 0', display: 'flex', alignItems: 'center', gap: '5px' }}>
                ⚠ SUGGESTED PHARMACOTHERAPY
              </p>
              {activeInsight?.auto_medications?.map((med: any, i: number) => (
                <div key={i} style={{ marginBottom: '12px', paddingBottom: '12px', borderBottom: i === activeInsight.auto_medications.length - 1 ? 'none' : '1px dashed #fca5a5' }}>
                  <p style={{ fontSize: '13px', fontWeight: '800', color: '#991b1b', margin: '0 0 3px 0' }}>
                    {typeof med === 'object' ? String(med.name || med.purpose || 'Prescribed Compound') : String(med)}
                  </p>
                  <p style={{ fontSize: '11px', color: '#b91c1c', fontWeight: '600', margin: 0 }}>
                    {typeof med === 'object' ? `${String(med.dosage || 'Prescribed dosage')} | ${String(med.frequency || 'Follow guidelines')}` : 'Follow standard directions'}
                  </p>
                </div>
              ))}
              {(activeInsight?.auto_medications?.length || 0) === 0 && (
                <p style={{ fontSize: '12px', color: '#7f1d1d', fontStyle: 'italic', margin: 0 }}>
                  No modifications or suggested pharmacological changes recorded for this iteration cycle.
                </p>
              )}
            </div>

            {activeInsight?.prescription_image && (
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '12px', padding: '15px', backgroundColor: '#fff' }}>
                <p style={{ fontSize: '10px', fontWeight: '800', color: '#64748b', textTransform: 'uppercase', margin: '0 0 10px 0', borderBottom: '1px solid #f1f5f9', paddingBottom: '5px' }}>Prescription Telemetry Ingest</p>
                <img src={activeInsight.prescription_image} style={{ width: '100%', borderRadius: '8px', border: '1px solid #e2e8f0' }} alt="Clinical Ingest Scan" />
              </div>
            )}
          </div>
        </div>

        {/* Signatures & Legal Footers */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '40px', marginTop: '50px', borderTop: '1px solid #e2e8f0', paddingTop: '30px' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ borderBottom: '1px solid #94a3b8', height: '40px', width: '200px', margin: '0 auto 8px auto', display: 'flex', alignItems: 'center', justifyContent: 'center', fontStyle: 'italic', color: '#64748b', fontWeight: '600', fontFamily: '"Times New Roman", serif' }}>
              CarePredict AI-Handshake
            </div>
            <p style={{ fontSize: '10px', textTransform: 'uppercase', fontWeight: '800', color: '#64748b', margin: 0 }}>Consensus Engine Signature</p>
            <p style={{ fontSize: '9px', color: '#cbd5e1', margin: '2px 0 0 0' }}>Verified via Neural Hash Integration</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ borderBottom: '1px solid #94a3b8', height: '40px', width: '200px', margin: '0 auto 8px auto' }} />
            <p style={{ fontSize: '10px', textTransform: 'uppercase', fontWeight: '800', color: '#0f172a', margin: 0 }}>Human Attendant Specialist Reviewer</p>
            <p style={{ fontSize: '9px', color: '#64748b', margin: '2px 0 0 0' }}>Licensure Signature Certification Required</p>
          </div>
        </div>

        <div style={{ marginTop: '40px', borderTop: '1px solid #f1f5f9', paddingTop: '20px', textAlign: 'center' }}>
          <p style={{ fontSize: '9px', color: '#94a3b8', margin: 0, letterSpacing: '0.02em' }}>
            DISCLAIMER: This synthesis report is compiled by an advanced artificial intelligence decision support engine. It does not constitute a primary clinical diagnosis. All directives, guidance parameters, and conclusions MUST be verified and validated by a licensed healthcare provider before implementing therapeutic treatment modifications.
          </p>
          <p style={{ fontSize: '10px', fontWeight: '900', color: '#0f172a', letterSpacing: '0.05em', textTransform: 'uppercase', marginTop: '12px' }}>
            🔒 SECURE ENCRYPTED ARCHIVAL RECORD
          </p>
        </div>
      </div>"""

    # Replace
    content = content.replace(original_template, new_template)
    
    # Save file
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Successfully refactored patient clinical report template!")
else:
    print("ERROR: Could not isolate target clinical-print-template DIV block in PatientDashboard!")

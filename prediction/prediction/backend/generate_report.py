from fpdf import FPDF
import datetime

class ClinicalReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(6, 182, 212) # Cyber Cyan
        self.cell(0, 15, 'System Intelligence & Architecture Report', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'AntiGravity Systems | Clinical Diagnostic Platform | Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, label):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(168, 85, 247) # Cyber Purple
        self.cell(0, 10, label, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, text):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 7, text)
        self.ln(5)

pdf = ClinicalReportPDF()
pdf.add_page()

# 1. Tech Stack
pdf.section_title("1. Technology Stack")
pdf.chapter_body(
    " - Frontend: React 18, TypeScript, Framer Motion (Cyberpunk/Clinical Aesthetics).\n"
    " - Backend: Flask (Python 3.10+) Orchestration Engine.\n"
    " - Database: MongoDB (Persistence for Medical Records & Predictions).\n"
    " - AI Integration: Groq/OpenRouter (Llama 3.1 70B AI Narrative Engine)."
)

# 2. ML Models
pdf.section_title("2. Machine Learning Architecture")
pdf.chapter_body(
    " - Ensemble Engine: Distributed Voting between XGBoost, Random Forest, and Gradient Boosting.\n"
    " - Clinical Registry: Unified index mapping for Diabetes, Cardiac, and Mental Health protocols.\n"
    " - Data Pipeline: Robust automated feature scaling and clinical data integrity layers."
)

# 3. AI & Multimodal Pipelines
pdf.section_title("3. Generative AI & Multimodal Pipelines")
pdf.chapter_body(
    " - Clinical Fusion: Hand-in-Hand synchronization between statistical ML and Generative AI narratives.\n"
    " - Risk Escalation: AI-Driven Guardrail forced escalation for catastrophic biomarkers (BP 160+, BMI 45+).\n"
    " - Vision Audit: EasyOCR handwriting clarity audit and pharmacological education logic.\n"
    " - Voice Intelligence: Real-time STT with context-aware parameter extraction."
)

# 4. Features & Guardrails
pdf.section_title("4. Security & Clinical Features")
pdf.chapter_body(
    " - Fingerprint Persistence: Full historical logging of manual entry and visual scan evidence.\n"
    " - Zero-Trust Guardrails: Absolute safety overrides prioritizing clinical consensus over ML probability.\n"
    " - Multi-Language Intelligence: High-fidelity 'Hinglish' clinical transcreation engine."
)

output_path = "System_Architecture_and_Intelligence.pdf"
pdf.output(output_path)
print(f"PDF Successfully generated at: {output_path}")

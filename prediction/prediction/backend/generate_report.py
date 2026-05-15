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
    "   [File Location: frontend/package.json]\n"
    " - Backend: Flask (Python 3.10+) Orchestration Engine.\n"
    "   [File Location: backend/app.py, backend/requirements.txt]\n"
    " - Database: MongoDB (Persistence for Medical Records & Predictions).\n"
    "   [File Location: backend/utils/db.py, backend/services/prediction_service.py]\n"
    " - AI Integration: Groq/OpenRouter (Llama 3.3 70B, 3.2 11B Vision, 3.1 8B Instant Neural Engines).\n"
    "   [File Location: backend/services/clinical_intelligence.py, backend/utils/translation.py]"
)

# 2. ML Models
pdf.section_title("2. Machine Learning Architecture")
pdf.chapter_body(
    " - Ensemble Engine: Bayesian-weighted soft voting & stacking combining XGBoost, Random Forest, Gradient Boosting, SVM, and Logistic Regression.\n"
    "   [File Location: backend/models/ensemble_optimizer.py, backend/models/ml_models_enhanced.py]\n"
    " - Clinical Registry: Unified index mapping for Diabetes, Cardiac, and Mental Health protocols.\n"
    "   [File Location: backend/utils/clinical_registry.py, backend/stabilize_registry.py]\n"
    " - Data Pipeline: Robust automated feature scaling and clinical data integrity layers.\n"
    "   [File Location: backend/models/dl_models_enhanced.py, backend/models/ml_models_enhanced.py]"
)

# 3. AI & Multimodal Pipelines
pdf.section_title("3. Generative AI & Multimodal Pipelines")
pdf.chapter_body(
    " - Clinical Fusion: Synchronization between statistical ML probability and Generative AI narratives.\n"
    "   [File Location: backend/services/prediction_service.py]\n"
    " - Risk Escalation: Forced escalation logic for catastrophic biomarkers (Glucose 250+, BP 160+, BMI 45+).\n"
    "   [File Location: backend/services/prediction_service.py]\n"
    " - Vision Audit: EasyOCR handwriting clarity audit and pharmacological recognition.\n"
    "   [File Location: backend/services/ocr_service.py, backend/api/routes/ocr_routes.py]\n"
    " - Voice Intelligence: AssemblyAI & Google Web STT with context-aware parameter extraction.\n"
    "   [File Location: backend/services/audio_service.py, backend/services/voice_intake_service.py]"
)

# 4. Features & Guardrails
pdf.section_title("4. Security & Clinical Features")
pdf.chapter_body(
    " - Fingerprint Persistence: Historical logging of prediction entries and diagnostic events.\n"
    "   [File Location: backend/services/prediction_service.py (MongoDB collections: medical_records, predictions)]\n"
    " - Zero-Trust Guardrails: Safety overrides prioritizing clinical consensus protocols over raw ML probability.\n"
    "   [File Location: backend/services/prediction_service.py]\n"
    " - Multi-Language Intelligence: High-fidelity 'Hinglish' clinical transcreation using Llama 3.1 8B.\n"
    "   [File Location: backend/utils/translation.py]"
)

output_path = "System_Architecture_and_Intelligence.pdf"
pdf.output(output_path)
print(f"PDF Successfully generated at: {output_path}")


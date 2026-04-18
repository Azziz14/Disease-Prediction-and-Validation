export interface DrugDetail {
  usage: string;
  type: string;
}

const DRUG_CATALOG: Record<string, DrugDetail> = {
  metformin: {
    usage: 'First-line medication to lower blood glucose and improve insulin sensitivity.',
    type: 'Biguanide antidiabetic'
  },
  insulin: {
    usage: 'Direct hormone replacement used to control elevated blood sugar levels.',
    type: 'Hormone therapy'
  },
  glipizide: {
    usage: 'Stimulates pancreatic insulin release for glucose control.',
    type: 'Sulfonylurea antidiabetic'
  },
  gliclazide: {
    usage: 'Supports insulin secretion for type 2 diabetes control.',
    type: 'Sulfonylurea antidiabetic'
  },
  glimepiride: {
    usage: 'Helps reduce post-meal and fasting glucose in type 2 diabetes.',
    type: 'Sulfonylurea antidiabetic'
  },
  pioglitazone: {
    usage: 'Improves insulin sensitivity in peripheral tissues.',
    type: 'Thiazolidinedione'
  },
  sitagliptin: {
    usage: 'Enhances incretin effect to increase insulin release and reduce glucagon.',
    type: 'DPP-4 inhibitor'
  },
  empagliflozin: {
    usage: 'Promotes urinary glucose excretion and supports cardiometabolic control.',
    type: 'SGLT2 inhibitor'
  },
  dapagliflozin: {
    usage: 'Lowers blood glucose through renal glucose elimination.',
    type: 'SGLT2 inhibitor'
  },
  semaglutide: {
    usage: 'Improves glycemic control and supports weight reduction in diabetes care.',
    type: 'GLP-1 receptor agonist'
  }
};

const normalizeDrug = (value: string): string => value.toLowerCase().replace(/[^a-z0-9]/g, '');

export const getDrugDetail = (drugName: string): DrugDetail | null => {
  const normalized = normalizeDrug(drugName);
  const direct = DRUG_CATALOG[normalized];
  if (direct) {
    return direct;
  }

  const key = Object.keys(DRUG_CATALOG).find((entry) => normalized.includes(entry));
  return key ? DRUG_CATALOG[key] : null;
};

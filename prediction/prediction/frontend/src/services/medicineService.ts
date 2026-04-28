interface Medicine {
  name: string;
  dosage: string;
  frequency: string;
  category: string;
  alternatives: string[];
}

const MEDICINE_DATABASE: Medicine[] = [
  // Diabetes medications
  { name: "Metformin", dosage: "500mg", frequency: "twice daily", category: "diabetes", alternatives: ["Glucophage", "Riomet"] },
  { name: "Insulin", dosage: "10-100 units", frequency: "as prescribed", category: "diabetes", alternatives: ["Humalog", "Novolog", "Lantus"] },
  { name: "Glipizide", dosage: "5mg", frequency: "once daily", category: "diabetes", alternatives: ["Glucotrol"] },
  { name: "Empagliflozin", dosage: "10mg", frequency: "once daily", category: "diabetes", alternatives: ["Jardiance"] },
  { name: "Sitagliptin", dosage: "100mg", frequency: "once daily", category: "diabetes", alternatives: ["Januvia"] },
  
  // Heart medications
  { name: "Atorvastatin", dosage: "10-80mg", frequency: "once daily", category: "heart", alternatives: ["Lipitor"] },
  { name: "Lisinopril", dosage: "10-40mg", frequency: "once daily", category: "heart", alternatives: ["Zestril", "Prinivil"] },
  { name: "Aspirin", dosage: "81-325mg", frequency: "once daily", category: "heart", alternatives: ["Ecotrin"] },
  { name: "Metoprolol", dosage: "25-200mg", frequency: "twice daily", category: "heart", alternatives: ["Lopressor", "Toprol"] },
  { name: "Amlodipine", dosage: "5-10mg", frequency: "once daily", category: "heart", alternatives: ["Norvasc"] },
  
  // Mental health medications
  { name: "Sertraline", dosage: "25-200mg", frequency: "once daily", category: "mental", alternatives: ["Zoloft"] },
  { name: "Fluoxetine", dosage: "20-80mg", frequency: "once daily", category: "mental", alternatives: ["Prozac"] },
  { name: "Escitalopram", dosage: "5-20mg", frequency: "once daily", category: "mental", alternatives: ["Lexapro"] },
  { name: "Duloxetine", dosage: "30-60mg", frequency: "once daily", category: "mental", alternatives: ["Cymbalta"] },
  { name: "Bupropion", dosage: "150-450mg", frequency: "twice daily", category: "mental", alternatives: ["Wellbutrin"] },
];

// Simple string similarity function (Levenshtein distance approximation)
function stringSimilarity(str1: string, str2: string): number {
  const longer = str1.length > str2.length ? str1 : str2;
  const shorter = str1.length > str2.length ? str2 : str1;
  
  if (longer.length === 0) return 1.0;
  
  const distance = levenshteinDistance(longer, shorter);
  return (longer.length - distance) / longer.length;
}

function levenshteinDistance(str1: string, str2: string): number {
  const matrix = [];
  
  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  
  return matrix[str2.length][str1.length];
}

export function findMedicineSuggestions(input: string, disease: string = 'diabetes'): Medicine[] {
  const normalizedInput = input.toLowerCase().trim();
  const suggestions: Medicine[] = [];
  
  // Filter medicines by category
  const relevantMedicines = MEDICINE_DATABASE.filter(med => 
    med.category === disease || disease === 'diabetes'
  );
  
  // Find exact matches first
  const exactMatches = relevantMedicines.filter(med => 
    med.name.toLowerCase() === normalizedInput ||
    med.alternatives.some(alt => alt.toLowerCase() === normalizedInput)
  );
  
  if (exactMatches.length > 0) {
    return exactMatches;
  }
  
  // Find fuzzy matches
  const fuzzyMatches = relevantMedicines.map(med => {
    const nameSimilarity = stringSimilarity(normalizedInput, med.name.toLowerCase());
    const altSimilarity = med.alternatives.reduce((max, alt) => {
      const similarity = stringSimilarity(normalizedInput, alt.toLowerCase());
      return Math.max(max, similarity);
    }, 0);
    
    const bestSimilarity = Math.max(nameSimilarity, altSimilarity);
    
    return { medicine: med, similarity: bestSimilarity };
  })
  .filter(match => match.similarity > 0.6) // Only include matches with >60% similarity
  .sort((a, b) => b.similarity - a.similarity)
  .slice(0, 5) // Return top 5 matches
  .map(match => match.medicine);
  
  return fuzzyMatches;
}

export function getMedicineVariations(medicineName: string, disease: string = 'diabetes'): Medicine[] {
  const medicine = MEDICINE_DATABASE.find(med => 
    med.name.toLowerCase() === medicineName.toLowerCase() ||
    med.alternatives.some(alt => alt.toLowerCase() === medicineName.toLowerCase())
  );
  
  if (!medicine) return [];
  
  // Return the medicine and its alternatives
  return [medicine, ...MEDICINE_DATABASE.filter(med => 
    med.category === medicine.category && 
    med.name !== medicine.name &&
    medicine.alternatives.includes(med.name)
  )].slice(0, 3);
}

export function generateDosageVariations(baseMedicine: Medicine): string[] {
  const variations: string[] = [];
  
  // Generate different dosage options based on the medicine
  if (baseMedicine.category === 'diabetes') {
    if (baseMedicine.name === 'Metformin') {
      variations.push('500mg twice daily', '850mg twice daily', '1000mg twice daily', '500mg once daily');
    } else if (baseMedicine.name === 'Insulin') {
      variations.push('10 units before meals', '20 units before breakfast and dinner', 'basal insulin 20 units at bedtime');
    }
  } else if (baseMedicine.category === 'heart') {
    if (baseMedicine.name === 'Atorvastatin') {
      variations.push('10mg once daily', '20mg once daily', '40mg once daily', '80mg once daily');
    } else if (baseMedicine.name === 'Lisinopril') {
      variations.push('10mg once daily', '20mg once daily', '40mg once daily');
    }
  } else if (baseMedicine.category === 'mental') {
    if (baseMedicine.name === 'Sertraline') {
      variations.push('25mg once daily', '50mg once daily', '100mg once daily', '200mg once daily');
    }
  }
  
  // If no specific variations, return the base dosage
  if (variations.length === 0) {
    variations.push(baseMedicine.dosage + ' ' + baseMedicine.frequency);
  }
  
  return variations;
}

export function getMedicineInteractions(medicines: string[]): Array<{medicine: string, interactsWith: string[], severity: 'mild' | 'moderate' | 'severe'}> {
  const interactions: Array<{medicine: string, interactsWith: string[], severity: 'mild' | 'moderate' | 'severe'}> = [];
  
  // Common drug interactions
  const knownInteractions = {
    'Metformin': { 'Iodinated contrast': 'severe', 'Alcohol': 'moderate' },
    'Insulin': { 'Beta blockers': 'moderate', 'Aspirin': 'mild' },
    'Atorvastatin': { 'Grapefruit juice': 'severe', 'Clarithromycin': 'severe' },
    'Lisinopril': { 'Potassium supplements': 'severe', 'NSAIDs': 'moderate' },
    'Sertraline': { 'MAO inhibitors': 'severe', 'Warfarin': 'moderate' },
  };
  
  medicines.forEach(med => {
    const medLower = med.toLowerCase();
    const interaction = knownInteractions[medLower as keyof typeof knownInteractions];
    
    if (interaction) {
      interactions.push({
        medicine: med,
        interactsWith: Object.keys(interaction),
        severity: Object.values(interaction)[0] as 'mild' | 'moderate' | 'severe'
      });
    }
  });
  
  return interactions;
}

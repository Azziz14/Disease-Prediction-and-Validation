import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Bot, Languages, Loader2, Mic, Send, Square, Volume2 } from 'lucide-react';

interface PredictionRecord {
  id?: string;
  disease?: string;
  risk?: string;
  confidence?: number;
  timestamp?: string;
  matched_drugs?: string[];
  auto_medications?: MedicationSuggestion[];
  recommendations?: {
    lifestyle?: string[];
    medical?: string[];
    precautions?: string[];
  };
  drug_interactions?: string[];
  prescription_evaluation?: {
    provided?: boolean;
    status?: string;
    message?: string;
    details?: string[];
  };
}

interface MedicationSuggestion {
  name?: string;
  dosage?: string;
  frequency?: string;
  note?: string;
}

interface InsightData {
  prediction?: {
    disease?: string;
    risk?: string;
    confidence?: number;
    model_metadata?: {
      trained_artifacts_available?: boolean;
      prediction_method?: string;
      best_ml_model?: string;
      best_ml_accuracy?: number;
      ensemble_accuracy?: number;
      ensemble_auc?: number;
      training_samples?: number;
    };
  };
  auto_medications?: MedicationSuggestion[];
  recommendations?: {
    lifestyle?: string[];
    medical?: string[];
    precautions?: string[];
  };
}

interface AssistantMessage {
  role: 'user' | 'assistant';
  text: string;
}

interface PatientVoiceAssistantProps {
  patientName?: string;
  predictions?: PredictionRecord[];
  activeInsight?: InsightData | null;
  selectedLog?: PredictionRecord | null;
}

interface SpeechRecognitionInstance {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: ((event: any) => void) | null;
  onerror: ((event: any) => void) | null;
  onend: (() => void) | null;
}

type SpeechRecognitionCtor = new () => SpeechRecognitionInstance;
type AssistantLanguage = 'en' | 'hi';
type ListeningMode = 'auto' | 'en-IN' | 'hi-IN';

const getSpeechRecognition = (): SpeechRecognitionCtor | null => {
  const scopedWindow = window as Window & {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };

  return scopedWindow.SpeechRecognition || scopedWindow.webkitSpeechRecognition || null;
};

const HINDI_KEYWORDS = [
  'namaste', 'kya', 'kaise', 'mera', 'meri', 'mujhe', 'dawai', 'davai',
  'natija', 'batao', 'samjhao', 'savdhani', 'ilaaj', 'pakka'
];

const containsHindiScript = (text: string): boolean => /[\u0900-\u097F]/.test(text);

const detectAssistantLanguage = (question: string): AssistantLanguage => {
  const normalized = question.toLowerCase();
  if (containsHindiScript(question)) {
    return 'hi';
  }

  if (HINDI_KEYWORDS.some((keyword) => normalized.includes(keyword))) {
    return 'hi';
  }

  return 'en';
};

const formatConfidence = (value?: number): string => {
  if (typeof value !== 'number') {
    return 'not available';
  }

  return `${(value * 100).toFixed(1)}%`;
};

const formatModelName = (value?: string): string => {
  if (!value) {
    return 'the trained model stack';
  }

  const mapping: Record<string, string> = {
    rf: 'Random Forest',
    xgb: 'XGBoost',
    svm: 'Support Vector Machine',
    lr: 'Logistic Regression',
    gb: 'Gradient Boosting',
    lgbm: 'LightGBM'
  };

  return mapping[value] || value.toUpperCase();
};

const translateDiseaseName = (disease?: string, language: AssistantLanguage = 'en'): string => {
  if (!disease) {
    return 'condition';
  }

  if (language === 'en') {
    return disease;
  }

  const mapping: Record<string, string> = {
    diabetes: 'diabetes',
    heart: 'heart condition',
    mental: 'mental health'
  };

  return mapping[disease] || disease;
};

const formatPredictionSummary = (
  prediction?: PredictionRecord,
  language: AssistantLanguage = 'en'
): string | null => {
  if (!prediction?.disease || !prediction?.risk) {
    return null;
  }

  const timestamp = prediction.timestamp
    ? new Date(prediction.timestamp).toLocaleString()
    : language === 'hi' ? 'abhi haal mein' : 'recently';

  const disease = translateDiseaseName(prediction.disease, language);
  const risk = prediction.risk.toLowerCase();
  const confidence = formatConfidence(prediction.confidence);

  if (language === 'hi') {
    return `Aapka latest ${disease} result ${risk} risk dikhata hai. Confidence index ${confidence} hai. Yeh diagnostic record ${timestamp} ko system mein save kiya gaya tha. Kya aap handles, precautions, ya medications ke baare mein jaanna chahte hain?`;
  }

  return `Your latest ${disease} result shows ${risk} risk, with a confidence of ${confidence}. This was recorded on ${timestamp}.`;
};

const buildGreeting = (patientName?: string, language: AssistantLanguage = 'en'): string => {
  if (language === 'hi') {
    return `Namaste! Main aapki sehat ka khayal rakhne wali CarePredict assistant hoon. Main aapke clinical records aur diagnostics aasan bhasha mein samjha sakti hoon. Aaj main aapki kaise madad karun?`;
  }

  return `Hello${patientName ? ` ${patientName}` : ''}, I am your CarePredict voice assistant. I can explain your results and records accurately. How can I assist you?`;
};

const buildAssistantReply = (
  question: string,
  patientName?: string,
  predictions: PredictionRecord[] = [],
  activeInsight?: InsightData | null,
  selectedLog?: PredictionRecord | null
): { text: string; language: AssistantLanguage } => {
  const normalized = question.toLowerCase();
  const language = detectAssistantLanguage(question);
  const latestPrediction = activeInsight?.prediction
    ? {
        disease: activeInsight.prediction.disease,
        risk: activeInsight.prediction.risk,
        confidence: activeInsight.prediction.confidence
      }
    : predictions[0];
  const contextLog = selectedLog || predictions[0];
  const riskScore = (risk?: string) => (risk === 'High' ? 3 : risk === 'Moderate' ? 2 : 1);

  const latestPredictionSummary = formatPredictionSummary(latestPrediction, language);
  const modelMetadata = activeInsight?.prediction?.model_metadata;

  if (
    normalized.includes('hello') || normalized.includes('hi') || normalized.includes('hey') ||
    normalized.includes('namaste') || normalized.includes('sun rahe')
  ) {
    return { text: buildGreeting(patientName, language), language };
  }

  if (
    normalized.includes('latest') || normalized.includes('result') || normalized.includes('risk') ||
    normalized.includes('prediction') || normalized.includes('natija') || normalized.includes('report')
  ) {
    return {
      text: latestPredictionSummary || (
        language === 'hi'
          ? 'Abhi mujhe koi completed prediction nahi dikh raha. Pehle diagnosis run kijiye, phir main result ko aasan bhaasha mein samjha dungi.'
          : 'I do not see a completed prediction yet. Run a diagnosis first, and then I can explain the result in a simple and human way.'
      ),
      language
    };
  }

  if (normalized.includes('history') || normalized.includes('recent') || normalized.includes('pichle') || normalized.includes('purane')) {
    if (!predictions.length) {
      return {
        text: language === 'hi'
          ? 'Aapke dashboard mein abhi tak koi recent prediction saved nahi hai.'
          : 'There are no recent predictions in your dashboard yet.',
        language
      };
    }

    const recentSummary = predictions
      .slice(0, 3)
      .map((entry) => {
        const disease = translateDiseaseName(entry.disease || 'unknown condition', language);
        const risk = (entry.risk || 'unknown risk').toLowerCase();
        return language === 'hi'
          ? `${disease} mein ${risk} risk tha`
          : `${disease} was ${risk} risk`;
      })
      .join(', ');

    return {
      text: language === 'hi'
        ? `Mujhe aapki ${predictions.length} recent predictions mili hain. Sabse recent entries yeh hain: ${recentSummary}.`
        : `I found ${predictions.length} recent predictions. The most recent ones are: ${recentSummary}.`,
      language
    };
  }

  if (
    normalized.includes('improvement') || normalized.includes('better') || normalized.includes('worse') ||
    normalized.includes('compare') || normalized.includes('progress') || normalized.includes('sudhar')
  ) {
    if (!contextLog || !contextLog.timestamp) {
      return {
        text: language === 'hi'
          ? 'Comparison ke liye mujhe kam se kam do saved tests chahiye.'
          : 'I need at least two saved tests to compare progress.',
        language
      };
    }

    const previousSameDisease = predictions
      .filter((entry) => entry.disease === contextLog.disease && entry.timestamp && entry.timestamp < contextLog.timestamp)
      .sort((a, b) => (b.timestamp || '').localeCompare(a.timestamp || ''))[0];

    if (!previousSameDisease) {
      return {
        text: language === 'hi'
          ? 'Is condition ke liye pehle ka test nahi mila. Ek aur test ke baad main clear progress comparison de sakti hoon.'
          : 'I could not find an older test for this condition yet. After one more test, I can give a clear progress comparison.',
        language
      };
    }

    const trend =
      riskScore(contextLog.risk) < riskScore(previousSameDisease.risk)
        ? (language === 'hi' ? 'risk improve hua hai' : 'risk has improved')
        : riskScore(contextLog.risk) > riskScore(previousSameDisease.risk)
          ? (language === 'hi' ? 'risk worse hua hai' : 'risk has worsened')
          : (language === 'hi' ? 'risk same hai' : 'risk is unchanged');
    const delta = ((Number(contextLog.confidence || 0) - Number(previousSameDisease.confidence || 0)) * 100).toFixed(1);

    return {
      text: language === 'hi'
        ? `Selected test ko previous test se compare karne par ${trend}. Confidence change ${delta}% hai.`
        : `Compared with your previous test, ${trend}. Confidence change is ${delta}%.`,
      language
    };
  }

  if (
    normalized.includes('medicine') || normalized.includes('medication') || normalized.includes('drug') ||
    normalized.includes('tablet') || normalized.includes('dawai') || normalized.includes('davai')
  ) {
    const medications = activeInsight?.auto_medications || contextLog?.auto_medications || [];
    const matchedDrugs = contextLog?.matched_drugs || [];

    if (!medications.length && !matchedDrugs.length) {
      return {
        text: language === 'hi'
          ? 'Latest insight mein mujhe abhi koi medicine suggestion nahi dikh raha. Diagnosis run karne ke baad main suggested medicines ko simple language mein bata sakti hoon.'
          : 'I do not see any current medication suggestions in the latest insight. Run a diagnosis and I can summarize the suggested medicines.',
        language
      };
    }

    const medicationSummary = medications.length > 0
      ? medications
          .slice(0, 3)
          .map((item) => {
            const name = typeof item === 'object' ? (item.name || item.purpose || 'Medication') : String(item);
            const dosage = (typeof item === 'object' && item.dosage) ? ` at ${String(item.dosage)}` : '';
            const frequency = (typeof item === 'object' && item.frequency) ? `, ${String(item.frequency)}` : '';
            return `${name}${dosage}${frequency}`;
          })
          .join('; ')
      : matchedDrugs.slice(0, 4).join(', ');

    return {
      text: language === 'hi'
        ? `Latest insight ke hisaab se suggested medicines yeh hain: ${medicationSummary}. Koi bhi treatment shuru karne se pehle doctor se confirm zaroor kijiye.`
        : `Based on the latest insight, the suggested medications are ${medicationSummary}. Please confirm any treatment with a qualified doctor before taking anything.`,
      language
    };
  }

  if (
    normalized.includes('wrong medicine') || normalized.includes('unsafe') || normalized.includes('interaction') ||
    normalized.includes('contra') || normalized.includes('galat dawai') || normalized.includes('nuksan')
  ) {
    const unsafeMeds = contextLog?.drug_interactions || [];
    const rxIssues = contextLog?.prescription_evaluation?.details || [];
    const issues = [...unsafeMeds, ...rxIssues].filter(Boolean);

    if (!issues.length) {
      return {
        text: language === 'hi'
          ? 'Selected log mein mujhe koi specific unsafe medicine warning ya interaction issue nahi mila.'
          : 'I do not see any specific unsafe medicine warning or interaction issue for the selected log.',
        language
      };
    }

    return {
      text: language === 'hi'
        ? `Selected log ke hisaab se medicine safety concerns yeh hain: ${issues.slice(0, 4).join(' ')}. Koi bhi medicine change doctor ki salah se hi karein.`
        : `For the selected log, these medication safety concerns were flagged: ${issues.slice(0, 4).join(' ')}. Please make medication changes only with clinician guidance.`,
      language
    };
  }

  if (
    normalized.includes('precaution') || normalized.includes('care') || normalized.includes('recommend') ||
    normalized.includes('what should i do') || normalized.includes('savdhani') || normalized.includes('kya karun') ||
    normalized.includes('exercise') || normalized.includes('routine') || normalized.includes('daily') ||
    normalized.includes('eat') || normalized.includes('food') || normalized.includes('diet') || normalized.includes('khana')
  ) {
    const precautions = activeInsight?.recommendations?.precautions || contextLog?.recommendations?.precautions || [];
    const lifestyle = activeInsight?.recommendations?.lifestyle || contextLog?.recommendations?.lifestyle || [];
    const medical = activeInsight?.recommendations?.medical || contextLog?.recommendations?.medical || [];
    const guidance = [...precautions, ...medical, ...lifestyle].filter(Boolean);

    if (!guidance.length) {
      return {
        text: language === 'hi'
          ? 'CLINICAL NOTE: Abhi medical suggestions available nahi hain. Pehle diagnosis run karein.'
          : 'CLINICAL NOTE: Recommendation data unavailable. Execute a diagnostic scan first.',
        language
      };
    }

    const clinicalDirectives = guidance.slice(0, 4).join(' ');
    return {
      text: language === 'hi'
        ? `CLINICAL DIRECTIVE: Aapka local status "Active" hai. Yeh hai aapki health precautions: ${clinicalDirectives}.`
        : `CLINICAL DIRECTIVE: Local health status is active. Follow these directives: ${clinicalDirectives}.`,
      language
    };
  }

  if (normalized.includes('confidence') || normalized.includes('accurate') || normalized.includes('sure') || normalized.includes('pakka')) {
    if (!latestPrediction) {
      return {
        text: language === 'hi'
          ? 'Abhi koi diagnosis result loaded nahi hai, isliye confidence value available nahi hai.'
          : 'There is no prediction confidence available yet because no diagnosis result is loaded.',
        language
      };
    }

    return {
      text: language === 'hi'
        ? `Latest prediction ka confidence ${formatConfidence(latestPrediction.confidence)} hai. Yeh sirf AI estimate hai, isliye final diagnosis aur treatment ke liye doctor par bharosa kijiye.`
        : `The latest prediction confidence is ${formatConfidence(latestPrediction.confidence)}. That is only an AI estimate, so you should still rely on a clinician for diagnosis and treatment decisions.`,
      language
    };
  }

  if (
    normalized.includes('model') || normalized.includes('accuracy') || normalized.includes('trained') ||
    normalized.includes('algorithm') || normalized.includes('which model') || normalized.includes('kitni accuracy')
  ) {
    if (!modelMetadata?.trained_artifacts_available) {
      return {
        text: language === 'hi'
          ? 'Is disease ke liye trained artifact metadata mujhe abhi available nahi dikh raha. Iska matlab ya to trained model save nahi hai, ya uska manifest present nahi hai.'
          : 'I do not see trained artifact metadata for this disease right now. That usually means a disease-specific trained manifest is missing or not yet loaded.',
        language
      };
    }

    const bestModel = formatModelName(modelMetadata.best_ml_model);
    const bestAccuracy = modelMetadata.best_ml_accuracy ? formatConfidence(modelMetadata.best_ml_accuracy) : 'not available';
    const ensembleAccuracy = modelMetadata.ensemble_accuracy ? formatConfidence(modelMetadata.ensemble_accuracy) : 'not available';
    const auc = modelMetadata.ensemble_auc ? modelMetadata.ensemble_auc.toFixed(3) : 'not available';
    const sampleCount = modelMetadata.training_samples || 'unknown';

    return {
      text: language === 'hi'
        ? `Yeh result trained model stack se aaya hai. Best base model ${bestModel} hai. Best model accuracy ${bestAccuracy} hai, aur ensemble accuracy ${ensembleAccuracy} hai. Ensemble AUC ${auc} hai, aur training samples ${sampleCount} the.`
        : `This result comes from the trained model stack. The best base model is ${bestModel}. Its recorded test accuracy is ${bestAccuracy}, while the ensemble accuracy is ${ensembleAccuracy}. The ensemble AUC is ${auc}, and it was trained on ${sampleCount} samples.`,
      language
    };
  }

  if (!predictions.length && !activeInsight) {
    return {
      text: language === 'hi'
        ? `Namaste! Mujhe dikh raha hai ki humare paas abhi aapka koi health log nahi hai. Aap aaj kaisa mehsoos kar rahe hain? Main yahan aapki sehat samajhne mein madad karne ke liye hoon.`
        : `Hello! I notice we don't have your health data logs yet. How are you feeling today? I am here to help you understand your health and answer any questions.`,
      language
    };
  }

  return {
    text: latestPredictionSummary
      ? (language === 'hi'
          ? `${latestPredictionSummary} Aap mujhse medicines, precautions, ya general health ke baare mein bhi pooch sakte hain.`
          : `${latestPredictionSummary} You can also ask me about medications, precautions, or any general health questions.`)
      : (language === 'hi'
          ? `Main aapke dashboard ko samjha sakti hoon aur general health questions ka jawab de sakti hoon. Aaj aap kaisa mehsoos kar rahe hain?`
          : 'I can help explain your dashboard and answer general health questions. How are you feeling today?'),
    language
  };
};

const PatientVoiceAssistant: React.FC<PatientVoiceAssistantProps> = ({
  patientName,
  predictions = [],
  activeInsight,
  selectedLog
}) => {
  const [listeningMode, setListeningMode] = useState<ListeningMode>('auto');
  const [messages, setMessages] = useState<AssistantMessage[]>([
    {
      role: 'assistant',
      text: buildGreeting(patientName, 'en')
    }
  ]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [assistantError, setAssistantError] = useState('');
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const hasGreetedRef = useRef(false);

  const speechRecognitionAvailable = useMemo(() => !!getSpeechRecognition(), []);
  const speechSynthesisAvailable = typeof window !== 'undefined' && 'speechSynthesis' in window;

  const speakText = (text: string, language: AssistantLanguage = 'en') => {
    if (!speechSynthesisAvailable) {
      return;
    }

    // Clean text: remove markdown symbols, hashtags, and brackets that sound annoying in voice
    const voiceCleanText = text
      .replace(/\*\*?|__/g, '') 
      .replace(/#+/g, '')       
      .replace(/[\[\]]/g, ' ')  
      .replace(/([.?!])\s*/g, '$1   '); 

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(voiceCleanText);
    
    // Find a "Natural" or "Google" voice for high quality
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
      (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Female')) && 
      v.lang.includes(language === 'hi' ? 'hi' : 'en')
    );

    if (preferredVoice) utterance.voice = preferredVoice;
    
    utterance.rate = 0.95; // Slightly slower for clinical clarity
    utterance.pitch = 1.05; // Slightly higher for warmth
    utterance.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if (speechSynthesisAvailable) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  useEffect(() => {
    if (hasGreetedRef.current) {
      return;
    }

    hasGreetedRef.current = true;
    // Removed automatic speakText to prevent agent from speaking on its own during dashboard load
  }, [patientName]);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (speechSynthesisAvailable) {
        window.speechSynthesis.cancel();
      }
    };
  }, [speechSynthesisAvailable]);

  const respondToQuestion = async (question: string) => {
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      return;
    }

    const detectedLanguage = detectAssistantLanguage(trimmedQuestion);
    let finalReplyText = '';
    let usedAPICall = false;
    setIsThinking(true);

    // 1. ALWAYS Try the OpenAI API first for a generative, non-robotic response
    try {
      const apiResponse = await fetch(`${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}/api/assistant-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: trimmedQuestion,
          language: detectedLanguage,
          patientName,
          predictions,
          selectedLog,
          messages: messages.slice(-6)
        })
      });
      
      if (apiResponse.ok) {
        const body = await apiResponse.json();
        if (body?.text) {
          finalReplyText = body.text;
          usedAPICall = true;
        }
      }
    } catch (err) {
      console.warn("API Assistant failed, falling back to local rules:", err);
    }

    // 2. ONLY Fall back to "inbuilt" messages if API is unavailable or failed
    if (!usedAPICall) {
      const localReply = buildAssistantReply(trimmedQuestion, patientName, predictions, activeInsight, selectedLog);
      finalReplyText = localReply.text;
      // Indicate to user we are in safe local fallback
      setAssistantError('Cloud AI unreachable. Local Clinical Brain engaged.');
    }

    setMessages((current) => [
      ...current,
      { role: 'user', text: trimmedQuestion },
      { role: 'assistant', text: finalReplyText }
    ]);
    
    setInput('');
    setIsThinking(false);
    setAssistantError('');
    speakText(finalReplyText, detectedLanguage);
  };

  const startListening = () => {
    if (!speechRecognitionAvailable) {
      setAssistantError('Speech recognition is not available in this browser. You can still type your question below.');
      return;
    }

    const Recognition = getSpeechRecognition();
    if (!Recognition) {
      setAssistantError('Speech recognition is not available in this browser. You can still type your question below.');
      return;
    }

    const recognition = new Recognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    
    // Balanced Auto-Mode: Start with en-IN but keep it ready for Hindi phonetics
    recognition.lang = listeningMode === 'auto' ? 'en-IN' : listeningMode;

    if (speechSynthesisAvailable) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }

    recognition.onresult = (event: any) => {
      const transcript = event.results?.[0]?.[0]?.transcript || '';
      // Only set input and respond once we have the final transcript to avoid "part by part" professional look
      setInput(transcript);
      void respondToQuestion(transcript);
    };

    recognition.onerror = (event: any) => {
      setAssistantError(`Voice assistant could not understand the request: ${event.error}.`);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    setAssistantError('');
    setIsListening(true);
    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const handleVoiceAssistantStop = () => {
    stopListening();
    stopSpeaking();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void respondToQuestion(input);
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Bot size={18} className="text-cyan-400" />
            Voice Assistant
          </h2>
          <p className="text-sm text-white/60 mt-1">
            I greet the patient, answer in a more human way, and can listen in English or Hindi.
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs uppercase tracking-widest text-white/45">
          {isSpeaking && (
            <button
              onClick={stopSpeaking}
              className="flex items-center gap-1.5 px-2 py-1 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg hover:bg-red-500/20 transition-all animate-pulse"
            >
              <Volume2 size={12} /> Stop
            </button>
          )}
          {isSpeaking ? <span className="text-cyan-400">Speaking</span> : <span>Ready</span>}
        </div>
      </div>

      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-2 text-xs uppercase tracking-widest text-white/45">
          <Languages size={14} className="text-cyan-400" />
          Voice Language
        </div>

        <select
          value={listeningMode}
          onChange={(e) => setListeningMode(e.target.value as ListeningMode)}
          className="bg-black/20 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
        >
          <option value="auto" className="bg-[#0a0a0f]">Auto / Hindi priority</option>
          <option value="en-IN" className="bg-[#0a0a0f]">English</option>
          <option value="hi-IN" className="bg-[#0a0a0f]">Hindi</option>
        </select>
      </div>

      <div className="flex flex-wrap gap-2">
        {[
          'Hello, how are you?',
          'What is my latest result?',
          'Which trained model gave this result?',
          'What medicines were suggested?',
          'Any wrong medicine or interaction warning?',
          'Compare this test with my previous one',
          'What daily exercise and routine should I follow?',
          'What precautions should I take?',
          'Show my recent prediction history',
          'Mera latest result kya hai?'
        ].map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => void respondToQuestion(prompt)}
            className="px-3 py-2 rounded-full border border-cyan-500/20 bg-cyan-500/10 text-cyan-200 text-xs hover:bg-cyan-500/20 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`rounded-2xl px-4 py-3 text-sm border ${
              message.role === 'assistant'
                ? 'bg-cyan-500/10 border-cyan-500/20 text-white/85'
                : 'bg-white/5 border-white/10 text-cyan-100'
            }`}
          >
            <p className="text-[10px] uppercase tracking-widest mb-1 text-white/45">
              {message.role === 'assistant' ? 'Assistant' : 'You'}
            </p>
            <p>{message.text}</p>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3 md:flex-row">
        <div className="flex-1">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask in English or Hindi, for example: Mera latest result kya hai?"
            className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/35 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        <div className="flex gap-2">
          {!isListening ? (
            <button
              type="button"
              onClick={startListening}
              className="px-4 py-3 rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/30 transition-colors flex items-center gap-2"
            >
              <Mic size={16} />
              {speechRecognitionAvailable ? 'Speak' : 'Voice Off'}
            </button>
          ) : (
            <button
              type="button"
              onClick={handleVoiceAssistantStop}
              className="px-4 py-3 rounded-xl bg-red-500/20 text-red-300 border border-red-500/30 hover:bg-red-500/30 transition-colors flex items-center gap-2"
            >
              <Square size={16} />
              Stop
            </button>
          )}

          <button
            type="submit"
            disabled={!input.trim()}
            className="px-4 py-3 rounded-xl bg-white/10 text-white border border-white/10 hover:bg-white/15 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={16} />
            Ask
          </button>
        </div>
      </form>

      {isListening && (
        <div className="flex items-center gap-2 text-sm text-cyan-300">
          <Loader2 size={16} className="animate-spin" />
          Assistant is listening... (Language: {listeningMode === 'hi-IN' ? 'Hindi' : listeningMode === 'en-IN' ? 'English' : 'Auto'})
        </div>
      )}

      {isThinking && (
        <div className="flex items-center gap-2 text-sm text-amber-300 animate-pulse">
          <Loader2 size={16} className="animate-spin" />
          Medical AI is thinking authoritative suggestions...
        </div>
      )}

      {assistantError && (
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
          {assistantError}
        </div>
      )}
    </div>
  );
};

export default PatientVoiceAssistant;

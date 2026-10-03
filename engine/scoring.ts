import { Food, DimensionScore } from './types';
import { THRESHOLDS as T } from './config';

// Helpers
export const clamp = (x: number, min: number, max: number) => Math.max(min, Math.min(max, x));
export const m1 = (x: number) => clamp(x, 0, 1);
export const round2 = (x: number) => Math.round(x * 100) / 100;

export function calcMacroQuality(food: Food): DimensionScore {
  if (food.kcal === 0) return { score: 100, explanation: "Zero calories." };
  const pShare = (food.protein * 4) / food.kcal;
  const sShare = (food.sugar * 4) / food.kcal;
  const fShare = (food.fat * 9) / food.kcal;
  
  const pScore = m1(pShare / T.macroQuality.proteinShare);
  const sScore = 1 - m1(sShare / T.macroQuality.sugarShare);
  const fScore = 1 - m1(Math.max(fShare - T.macroQuality.fatShareBase, 0) / T.macroQuality.fatShareRange);
  
  const score = 100 * (T.macroQuality.proteinWeight * pScore + T.macroQuality.sugarWeight * sScore + T.macroQuality.fatWeight * fScore);
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `${round2(pShare*100)}% protein, ${round2(sShare*100)}% sugar, ${round2(fShare*100)}% fat` 
  };
}

export function calcMicronutrientDensity(food: Food): DimensionScore {
  if (food.micronutrientIndex === null) return { score: 0, explanation: "Missing micronutrient data" };
  if (food.kcal === 0) return { score: 100, explanation: "Zero calories." };
  
  const microPer100Kcal = (food.micronutrientIndex / food.kcal) * 100;
  const score = (microPer100Kcal / T.micronutrientDensity.microPer100KcalTarget) * 100;
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `${round2(microPer100Kcal)}% average DV per 100 kcal` 
  };
}

export function calcProteinPerCalorie(food: Food): DimensionScore {
  if (food.kcal === 0) return { score: 0, explanation: "Zero calories." };
  const pShare = (food.protein * 4) / food.kcal;
  const score = (pShare / T.proteinPerCalorie.proteinShareTarget) * 100;
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `${round2(food.protein)}g protein per 100g (${round2(pShare*100)}% of kcal)` 
  };
}

export function calcAminoAcidProfile(food: Food): DimensionScore {
  if (food.aminoAcidScore === null) return { score: 0, explanation: "Missing amino acid data" };
  return { 
    score: clamp(food.aminoAcidScore, 0, 100), 
    explanation: `Amino acid score: ${round2(food.aminoAcidScore)}` 
  };
}

export function calcSatiety(food: Food): DimensionScore {
  if (food.kcal === 0) return { score: 100, explanation: "Zero calories." };
  const pPer100Kcal = (food.protein / food.kcal) * 100;
  const fPer100Kcal = (food.fiber / food.kcal) * 100;
  const kcalPerGram = food.kcal / 100;
  
  const pScore = m1(pPer100Kcal / T.satiety.proteinPer100KcalTarget);
  const fScore = m1(fPer100Kcal / T.satiety.fiberPer100KcalTarget);
  const edScore = m1(1 - (kcalPerGram - T.satiety.kcalPerGramBase) / T.satiety.kcalPerGramRange);
  
  const score = 100 * (T.satiety.proteinWeight * pScore + T.satiety.fiberWeight * fScore + T.satiety.energyDensityWeight * edScore);
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `${round2(pPer100Kcal)}g protein and ${round2(fPer100Kcal)}g fiber per 100 kcal` 
  };
}

export function calcEnergyDensity(food: Food): DimensionScore {
  const kcalPerGram = food.kcal / 100;
  const score = 100 * (1 - (kcalPerGram - T.energyDensity.kcalPerGramBase) / T.energyDensity.kcalPerGramRange);
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `${round2(kcalPerGram)} kcal/g` 
  };
}

export function calcFiberAndSugar(food: Food): DimensionScore {
  if (food.kcal === 0) return { score: 100, explanation: "Zero calories." };
  const fPer100Kcal = (food.fiber / food.kcal) * 100;
  const sShare = (food.sugar * 4) / food.kcal;
  
  const fScore = m1(fPer100Kcal / T.fiberAndSugar.fiberPer100KcalTarget);
  const sScore = 1 - m1(sShare / T.fiberAndSugar.sugarShareTarget);
  
  const score = 100 * (T.fiberAndSugar.fiberWeight * fScore + T.fiberAndSugar.sugarWeight * sScore);
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `${round2(fPer100Kcal)}g fiber per 100 kcal, ${round2(sShare*100)}% sugar kcal` 
  };
}

export function calcFatQuality(food: Food): DimensionScore {
  if (food.fat < T.fatQuality.lowFatThreshold) {
    return { score: T.fatQuality.lowFatScore, explanation: `Low fat (${round2(food.fat)}g)` };
  }
  const satShare = food.saturatedFat / food.fat;
  const score = 100 * (1 - m1(satShare / T.fatQuality.satFatShareTarget));
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `${round2(satShare*100)}% of fat is saturated` 
  };
}

export function calcSodiumPotassium(food: Food): DimensionScore {
  const naScore = 1 - m1(food.sodium / T.sodiumPotassium.sodiumTarget);
  const kScore = m1(food.potassium / T.sodiumPotassium.potassiumTarget);
  
  const score = 100 * (T.sodiumPotassium.sodiumWeight * naScore + T.sodiumPotassium.potassiumWeight * kScore);
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `${round2(food.sodium)}mg sodium, ${round2(food.potassium)}mg potassium` 
  };
}

export function calcGlycemicImpact(food: Food): DimensionScore {
  if (food.glycemicIndex === null) return { score: 0, explanation: "Missing glycemic index data" };
  const glycemicLoadPer100g = (food.glycemicIndex * food.carbs) / 100;
  const score = 100 * (1 - m1(glycemicLoadPer100g / T.glycemicImpact.glycemicLoadTarget));
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `Glycemic Load: ${round2(glycemicLoadPer100g)} per 100g` 
  };
}

export function calcProcessingLevel(food: Food): DimensionScore {
  if (food.novaGroup === null) return { score: 0, explanation: "Missing NOVA data" };
  
  let score = 0;
  if (food.novaGroup === 1) score = T.processingLevel.nova1;
  else if (food.novaGroup === 2) score = T.processingLevel.nova2;
  else if (food.novaGroup === 3) score = T.processingLevel.nova3;
  else if (food.novaGroup === 4) score = T.processingLevel.nova4;
  
  return { 
    score: clamp(score, 0, 100), 
    explanation: `NOVA Group ${food.novaGroup}` 
  };
}

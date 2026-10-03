import { Food, ScoreResult, ScoreWeights } from './types';
import { WEIGHT_PRESETS } from './config';
import {
  calcMacroQuality,
  calcMicronutrientDensity,
  calcProteinPerCalorie,
  calcAminoAcidProfile,
  calcSatiety,
  calcEnergyDensity,
  calcFiberAndSugar,
  calcFatQuality,
  calcSodiumPotassium,
  calcGlycemicImpact,
  calcProcessingLevel,
} from './scoring';

export function scoreFood(food: Food, weights: ScoreWeights = WEIGHT_PRESETS.default): ScoreResult {
  const subscores = {
    macroQuality: calcMacroQuality(food),
    micronutrientDensity: calcMicronutrientDensity(food),
    proteinPerCalorie: calcProteinPerCalorie(food),
    aminoAcidProfile: calcAminoAcidProfile(food),
    satiety: calcSatiety(food),
    energyDensity: calcEnergyDensity(food),
    fiberAndSugar: calcFiberAndSugar(food),
    fatQuality: calcFatQuality(food),
    sodiumPotassium: calcSodiumPotassium(food),
    glycemicImpact: calcGlycemicImpact(food),
    processingLevel: calcProcessingLevel(food),
  };

  const scoresArray = [
    subscores.macroQuality.score,
    subscores.micronutrientDensity.score,
    subscores.proteinPerCalorie.score,
    subscores.aminoAcidProfile.score,
    subscores.satiety.score,
    subscores.energyDensity.score,
    subscores.fiberAndSugar.score,
    subscores.fatQuality.score,
    subscores.sodiumPotassium.score,
    subscores.glycemicImpact.score,
    subscores.processingLevel.score,
  ];

  let totalWeight = 0;
  let weightedSum = 0;

  for (let i = 0; i < 11; i++) {
    totalWeight += weights[i];
    weightedSum += scoresArray[i] * weights[i];
  }

  const overallScore = totalWeight > 0 ? weightedSum / totalWeight : 0;

  return {
    overallScore: Math.round(overallScore * 100) / 100, // round to 2 decimals
    subscores,
  };
}

export * from './types';
export * from './config';
export * from './scoring';

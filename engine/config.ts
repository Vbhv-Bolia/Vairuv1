import { ScoreWeights } from './types';

export const WEIGHT_PRESETS = {
  default: [8, 8, 6, 5, 6, 5, 5, 4, 4, 5, 4] as ScoreWeights,
  muscle: [5, 5, 9, 9, 5, 3, 3, 3, 2, 3, 3] as ScoreWeights,
  weightLoss: [6, 6, 5, 3, 9, 9, 7, 3, 3, 6, 4] as ScoreWeights,
  heartHealth: [6, 7, 3, 2, 4, 4, 7, 9, 9, 5, 5] as ScoreWeights,
};

// Thresholds used in scoring formulas
export const THRESHOLDS = {
  macroQuality: {
    proteinWeight: 0.45,
    sugarWeight: 0.30,
    fatWeight: 0.25,
    proteinShare: 0.30,
    sugarShare: 0.25,
    fatShareBase: 0.35,
    fatShareRange: 0.40,
  },
  micronutrientDensity: {
    microPer100KcalTarget: 20,
  },
  proteinPerCalorie: {
    proteinShareTarget: 0.40,
  },
  satiety: {
    proteinWeight: 0.40,
    fiberWeight: 0.30,
    energyDensityWeight: 0.30,
    proteinPer100KcalTarget: 10,
    fiberPer100KcalTarget: 3,
    kcalPerGramBase: 0.5,
    kcalPerGramRange: 3.5,
  },
  energyDensity: {
    kcalPerGramBase: 0.6,
    kcalPerGramRange: 3.4,
  },
  fiberAndSugar: {
    fiberWeight: 0.60,
    sugarWeight: 0.40,
    fiberPer100KcalTarget: 4,
    sugarShareTarget: 0.20,
  },
  fatQuality: {
    lowFatThreshold: 1, // g
    lowFatScore: 85,
    satFatShareTarget: 0.50,
  },
  sodiumPotassium: {
    sodiumWeight: 0.65,
    potassiumWeight: 0.35,
    sodiumTarget: 500, // mg
    potassiumTarget: 400, // mg
  },
  glycemicImpact: {
    glycemicLoadTarget: 20,
  },
  processingLevel: {
    nova1: 100,
    nova2: 80,
    nova3: 50,
    nova4: 10,
  }
};

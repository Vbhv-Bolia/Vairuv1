export interface Food {
  name: string;
  kcal: number;
  protein: number;
  carbs: number;
  fiber: number;
  sugar: number;
  fat: number;
  saturatedFat: number;
  sodium: number;
  potassium: number;
  micronutrientIndex: number | null; // average % daily value
  aminoAcidScore: number | null; // 0-100
  glycemicIndex: number | null;
  novaGroup: number | null; // 1-4
}

export interface DimensionScore {
  score: number; // 0-100
  explanation: string;
}

export interface ScoreResult {
  overallScore: number;
  subscores: {
    macroQuality: DimensionScore;
    micronutrientDensity: DimensionScore;
    proteinPerCalorie: DimensionScore;
    aminoAcidProfile: DimensionScore;
    satiety: DimensionScore;
    energyDensity: DimensionScore;
    fiberAndSugar: DimensionScore;
    fatQuality: DimensionScore;
    sodiumPotassium: DimensionScore;
    glycemicImpact: DimensionScore;
    processingLevel: DimensionScore;
  };
}

export type ScoreWeights = [number, number, number, number, number, number, number, number, number, number, number];

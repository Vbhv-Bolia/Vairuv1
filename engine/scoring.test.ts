import { describe, it, expect } from 'vitest';
import { scoreFood } from './index';
import { Food, ScoreWeights } from './types';

const lentils: Food = {
  name: 'Lentils, boiled',
  kcal: 116,
  protein: 9.02,
  carbs: 20.13,
  fiber: 7.9,
  sugar: 1.8,
  fat: 0.38,
  saturatedFat: 0.05,
  sodium: 2,
  potassium: 369,
  micronutrientIndex: 12, 
  aminoAcidScore: 85,
  glycemicIndex: 29,
  novaGroup: 1,
};

const cola: Food = {
  name: 'Cola',
  kcal: 38,
  protein: 0,
  carbs: 9.8,
  fiber: 0,
  sugar: 9.8,
  fat: 0,
  saturatedFat: 0,
  sodium: 4,
  potassium: 0,
  micronutrientIndex: 0,
  aminoAcidScore: 0,
  glycemicIndex: 63,
  novaGroup: 4,
};

const zeroProteinFood: Food = {
  name: 'Sugar Cube',
  kcal: 400,
  protein: 0,
  carbs: 100,
  fiber: 0,
  sugar: 100,
  fat: 0,
  saturatedFat: 0,
  sodium: 0,
  potassium: 0,
  micronutrientIndex: 0,
  aminoAcidScore: 0,
  glycemicIndex: 100,
  novaGroup: 4,
};

describe('OpenNutritionScore Engine', () => {
  it('lentils should score higher than cola overall', () => {
    const lentilsScore = scoreFood(lentils);
    const colaScore = scoreFood(cola);
    
    expect(lentilsScore.overallScore).toBeGreaterThan(colaScore.overallScore);
  });

  it('a zero-protein food scores 0 on protein per calorie', () => {
    const result = scoreFood(zeroProteinFood);
    expect(result.subscores.proteinPerCalorie.score).toBe(0);
  });

  it('weights of all zero except one dimension make overall equal that subscore', () => {
    // Only macroQuality gets weight 10, rest get 0
    const testWeights: ScoreWeights = [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    const result = scoreFood(lentils, testWeights);
    
    // Check with a small tolerance due to rounding
    expect(Math.abs(result.overallScore - result.subscores.macroQuality.score)).toBeLessThan(0.1);
  });

  it('all scores are always bounded between 0 and 100', () => {
    const lentilsScore = scoreFood(lentils);
    const colaScore = scoreFood(cola);
    const zeroScore = scoreFood(zeroProteinFood);

    const checkBounds = (score: number) => {
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    };

    [lentilsScore, colaScore, zeroScore].forEach(result => {
      checkBounds(result.overallScore);
      Object.values(result.subscores).forEach(dim => {
        checkBounds(dim.score);
      });
    });
  });
});

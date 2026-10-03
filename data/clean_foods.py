#!/usr/bin/env python3
"""
clean_foods.py

Downloads and parses the USDA FoodData Central SR Legacy database,
extracting 200-500 common whole and basic foods strictly adhering
to the Food interface in engine/types.ts.
"""

import os
import sys
import json
import urllib.request
import zipfile
from typing import Dict, Any, List, Optional, Tuple

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(DATA_DIR, "raw")
RAW_ZIP = os.path.join(RAW_DIR, "FoodData_Central_sr_legacy_food_json_2018-04.zip")
OUTPUT_JSON = os.path.join(DATA_DIR, "cleaned_foods.json")
DOWNLOAD_URL = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip"

# FDA Daily Values (DVs) for adults for the 10 key micronutrients
DAILY_VALUES = {
    "303": ("Iron", 18.0),             # mg (Nutrient 303)
    "301": ("Calcium", 1300.0),         # mg (Nutrient 301)
    "304": ("Magnesium", 420.0),        # mg (Nutrient 304)
    "306": ("Potassium", 4700.0),       # mg (Nutrient 306)
    "309": ("Zinc", 11.0),              # mg (Nutrient 309)
    "417": ("Folate", 400.0),           # mcg (Nutrient 417 - Folate, total)
    "418": ("Vitamin B12", 2.4),        # mcg (Nutrient 418 - Vitamin B-12)
    "401": ("Vitamin C", 90.0),         # mg (Nutrient 401 - Vitamin C, total ascorbic acid)
    "320": ("Vitamin A", 900.0),        # mcg RAE (Nutrient 320 - Vitamin A, RAE)
    "328": ("Vitamin D", 20.0),         # mcg (Nutrient 328 - Vitamin D (D2 + D3))
}

# USDA core nutrient IDs per 100g
CORE_NUTRIENTS = {
    "208": "kcal",          # Energy (kcal)
    "203": "protein",       # Protein (g)
    "205": "carbs",         # Carbohydrate, by difference (g)
    "291": "fiber",         # Fiber, total dietary (g)
    "269": "sugar",         # Sugars, total (g)
    "204": "fat",           # Total lipid (fat) (g)
    "606": "saturatedFat",  # Fatty acids, total saturated (g)
    "307": "sodium",        # Sodium (mg)
    "306": "potassium",     # Potassium (mg)
}

TARGET_CATEGORIES = {
    "Vegetables and Vegetable Products",
    "Fruits and Fruit Juices",
    "Legumes and Legume Products",
    "Nut and Seed Products",
    "Cereal Grains and Pasta",
    "Dairy and Egg Products",
    "Finfish and Shellfish Products",
    "Poultry Products",
    "Beef Products",
    "Pork Products",
}

DISQUALIFYING_TERMS = [
    "babyfood", "infant", "toddler", "formula", "fast foods", "restaurant",
    "pie", "cake", "cookie", "candy", "chips", "bar,", "snack",
    "beverage, carbonated", "shake", "syrup", "frosting", "pudding",
    "breaded", "batter", "fried in", "imitation", "artificial",
    "canned in heavy syrup", "canned in light syrup", "sweetened with",
    "frozen dinner", "condensed", "dehydrated", "powder", "seasoning mix",
    "topping", "mechanically separated", "cured", "frankfurter", "pastrami",
    "bologna", "salami"
]

def ensure_download():
    """Download the USDA SR Legacy zip file if not already present."""
    os.makedirs(RAW_DIR, exist_ok=True)
    if not os.path.exists(RAW_ZIP):
        print(f"Downloading USDA SR Legacy dataset from {DOWNLOAD_URL}...")
        req = urllib.request.Request(DOWNLOAD_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(RAW_ZIP, "wb") as out_file:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                out_file.write(chunk)
        print("Download complete.")
    else:
        print(f"Found cached dataset: {RAW_ZIP}")

def is_target_whole_food(food: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Determine if a food is a common, whole/basic food and return category or rejection reason."""
    cat = food.get("foodCategory", {})
    cat_name = cat.get("description", "") if isinstance(cat, dict) else ""
    desc = food.get("description", "")
    ldesc = desc.lower()

    if cat_name not in TARGET_CATEGORIES:
        return False, f"Non-target category ({cat_name})"

    for term in DISQUALIFYING_TERMS:
        if term in ldesc:
            return False, f"Disqualifying term ('{term}')"

    # Category-specific criteria for basic / staple preparations
    if cat_name == "Vegetables and Vegetable Products":
        # Keep raw or boiled/steamed vegetables without added salt or fat
        if "raw" in ldesc or "boiled, drained, without salt" in ldesc or "cooked, boiled, drained" in ldesc:
            if "juice" not in ldesc and "pickled" not in ldesc:
                return True, "Vegetable"
        return False, "Not raw or plain boiled vegetable"

    elif cat_name == "Fruits and Fruit Juices":
        # Keep fresh whole raw fruits, exclude juices and canned in syrup
        if "raw" in ldesc and "juice" not in ldesc and "canned" not in ldesc:
            return True, "Fruit"
        return False, "Not whole raw fruit"

    elif cat_name == "Legumes and Legume Products":
        # Keep cooked or raw mature seeds (beans, lentils, peas, chickpeas)
        if "cooked, boiled, without salt" in ldesc or ("mature seeds" in ldesc and "cooked" in ldesc):
            return True, "Legume"
        elif "raw" in ldesc and any(k in ldesc for k in ["lentils", "chickpeas", "beans", "peas", "edamame"]):
            return True, "Legume"
        return False, "Not plain cooked/raw legume"

    elif cat_name == "Nut and Seed Products":
        # Keep raw or plain dry roasted nuts and seeds without added salt or sugar
        if ("raw" in ldesc or "dry roasted, without salt" in ldesc) and not any(k in ldesc for k in ["salted", "honey", "chocolate", "sugar"]):
            return True, "Nut/Seed"
        return False, "Not raw/unseasoned nut or seed"

    elif cat_name == "Cereal Grains and Pasta":
        # Keep whole grains cooked plain (oats, brown rice, wild rice, quinoa, barley, buckwheat)
        grains = ["oats", "rice, brown", "rice, wild", "rice, white", "quinoa", "barley", "buckwheat", "millet"]
        if any(g in ldesc for g in grains) and ("cooked" in ldesc or "rolled oats" in ldesc):
            if "mix" not in ldesc:
                return True, "Grain"
        return False, "Not staple plain grain"

    elif cat_name == "Dairy and Egg Products":
        # Keep plain milk, plain yogurt, whole eggs, egg whites, simple cheeses, plain butter
        plain_dairy = [
            "egg, whole, raw", "egg, whole, cooked", "egg, white, raw", "egg, white, cooked",
            "milk, whole", "milk, reduced fat, fluid, 2%", "milk, lowfat, fluid, 1%", "milk, nonfat",
            "yogurt, plain", "yogurt, greek, plain", "cheese, cottage", "cheese, cheddar",
            "cheese, mozzarella", "butter, without salt"
        ]
        if any(pd in ldesc for pd in plain_dairy) and "flavored" not in ldesc:
            return True, "Dairy/Egg"
        return False, "Not staple plain dairy or egg"

    elif cat_name == "Finfish and Shellfish Products":
        # Keep raw or cooked dry heat fish fillets and plain shellfish
        if ("raw" in ldesc or "cooked, dry heat" in ldesc) and not any(k in ldesc for k in ["canned", "smoked", "dried", "surimi", "fried"]):
            common_fish = ["salmon", "tuna", "cod", "halibut", "trout", "tilapia", "mackerel", "sardine", "shrimp", "crab", "scallop", "pollock", "haddock"]
            if any(cf in ldesc for cf in common_fish):
                return True, "Fish/Seafood"
        return False, "Not common fresh/dry-heat fish"

    elif cat_name == "Poultry Products":
        # Plain cuts, meat only (without skin or breading)
        if ("meat only, raw" in ldesc or "meat only, cooked, roasted" in ldesc) and not any(k in ldesc for k in ["skin", "canned", "roll", "patty"]):
            if any(k in ldesc for k in ["chicken", "turkey"]):
                return True, "Poultry"
        return False, "Not plain meat-only poultry"

    elif cat_name == "Beef Products":
        # Lean cuts and lean ground beef
        if ("separable lean only, raw" in ldesc or "separable lean only, trimmed to 0\" fat" in ldesc or "ground, 90%" in ldesc or "ground, 95%" in ldesc):
            if not any(k in ldesc for k in ["canned", "cured", "dried", "sausage", "patty, frozen"]):
                return True, "Beef"
        return False, "Not plain lean beef cut"

    elif cat_name == "Pork Products":
        # Lean pork loin/tenderloin
        if ("separable lean only, raw" in ldesc or "separable lean only, cooked" in ldesc):
            if not any(k in ldesc for k in ["cured", "bacon", "ham", "sausage"]):
                return True, "Pork"
        return False, "Not plain lean pork cut"

    return False, "Unmatched category rule"

def calculate_micronutrient_index(nutrients: Dict[str, float]) -> Optional[float]:
    """Calculate average % of Daily Value across the 10 key FDA micronutrients."""
    percentages = []
    
    for num, (name, dv) in DAILY_VALUES.items():
        amt = nutrients.get(num)
        # Fallback for Vitamin D: IU (324) / 40 = mcg
        if num == "328" and amt is None:
            iu = nutrients.get("324")
            if iu is not None:
                amt = iu / 40.0
        
        if amt is not None:
            pct = (amt / dv) * 100.0
            percentages.append(pct)
    
    if not percentages:
        return None
    
    # Average across the 10 reference micronutrients
    # Missing micronutrients in whole foods with proximate data contribute 0% DV
    # We divide by 10 to reflect the 10-micronutrient basket average
    avg_pct = sum(percentages) / 10.0
    return round(avg_pct, 2)

def determine_nova_group(food_desc: str, cat_name: str) -> int:
    """Determine NOVA classification group (1 for unprocessed whole foods, 2 for culinary ingredients)."""
    ldesc = food_desc.lower()
    if "butter" in ldesc or "oil" in ldesc or "sugar" in ldesc or "salt" in ldesc:
        return 2
    return 1

def clean_food_name(desc: str) -> str:
    """Clean and simplify USDA descriptions for user-friendly display."""
    name = desc
    # Remove leading category prefixes like 'Vegetables, ' or 'Fruits and Fruit Juices, '
    name = name.replace("broilers or fryers, ", "")
    name = name.replace("separable lean only, ", "")
    name = name.replace("trimmed to 0\" fat, ", "")
    return name.strip()

def process_dataset():
    ensure_download()

    print(f"Reading dataset from {RAW_ZIP}...")
    with zipfile.ZipFile(RAW_ZIP) as z:
        with z.open(z.namelist()[0]) as f:
            data = json.load(f)

    raw_foods = data.get("SRLegacyFoods", [])
    total_raw_count = len(raw_foods)
    print(f"Loaded {total_raw_count} total foods from USDA SR Legacy.")

    kept_foods: List[Dict[str, Any]] = []
    dropped_counts: Dict[str, int] = {}
    missing_fields_per_kept_food: Dict[str, int] = {}

    for food in raw_foods:
        if not isinstance(food, dict):
            dropped_counts["Corrupted entry"] = dropped_counts.get("Corrupted entry", 0) + 1
            continue

        desc = food.get("description", "")
        cat = food.get("foodCategory", {})
        cat_name = cat.get("description", "") if isinstance(cat, dict) else ""

        is_target, reason = is_target_whole_food(food)
        if not is_target:
            dropped_counts[reason] = dropped_counts.get(reason, 0) + 1
            continue

        # Extract nutrients
        nutrients: Dict[str, float] = {}
        for n in food.get("foodNutrients", []):
            if not isinstance(n, dict):
                continue
            nut = n.get("nutrient") or {}
            num = str(nut.get("number"))
            amt = n.get("amount")
            if num and amt is not None:
                nutrients[num] = float(amt)

        # Check core macronutrients
        missing_core = []
        for num, field in CORE_NUTRIENTS.items():
            if nutrients.get(num) is None:
                missing_core.append(field)

        # Drop if missing energy or core macros
        if any(field in missing_core for field in ["kcal", "protein", "carbs", "fat"]):
            dropped_counts["Missing core calories/macros"] = dropped_counts.get("Missing core calories/macros", 0) + 1
            continue

        # If saturatedFat, fiber, or sugar are missing, drop or handle strictly
        if any(field in missing_core for field in ["saturatedFat", "fiber", "sugar", "sodium", "potassium"]):
            dropped_counts["Missing secondary proximate nutrient"] = dropped_counts.get("Missing secondary proximate nutrient", 0) + 1
            continue

        # Compute micronutrient index
        micro_index = calculate_micronutrient_index(nutrients)

        # Map to Food interface in engine/types.ts
        food_obj: Dict[str, Any] = {
            "name": clean_food_name(desc),
            "kcal": round(nutrients["208"], 2),
            "protein": round(nutrients["203"], 2),
            "carbs": round(nutrients["205"], 2),
            "fiber": round(nutrients["291"], 2),
            "sugar": round(nutrients["269"], 2),
            "fat": round(nutrients["204"], 2),
            "saturatedFat": round(nutrients["606"], 2),
            "sodium": round(nutrients["307"], 2),
            "potassium": round(nutrients["306"], 2),
            "micronutrientIndex": micro_index,
            "aminoAcidScore": None,
            "glycemicIndex": None,
            "novaGroup": determine_nova_group(desc, cat_name),
        }
        kept_foods.append(food_obj)

    # Sort deterministically by name
    kept_foods.sort(key=lambda x: x["name"])

    # If count is above 500, prune similar cuts to stay within 200-500 target
    if len(kept_foods) > 500:
        print(f"Pruning from {len(kept_foods)} to 400 diverse whole foods...")
        # Step sample evenly to preserve diversity across categories
        step = len(kept_foods) / 400.0
        kept_foods = [kept_foods[int(i * step)] for i in range(400)]

    print(f"\nFinal count of kept foods: {len(kept_foods)}")

    # Track missing fields on final kept foods
    for food_obj in kept_foods:
        for key, val in food_obj.items():
            if val is None:
                missing_fields_per_kept_food[key] = missing_fields_per_kept_food.get(key, 0) + 1

    # Structure output JSON with metadata
    output_data = {
        "metadata": {
            "dataSource": "USDA FoodData Central - SR Legacy",
            "version": "April 2018",
            "downloadUrl": DOWNLOAD_URL,
            "totalFoods": len(kept_foods),
            "description": "Cleaned, standardized whole and basic foods matching the Food interface in engine/types.ts"
        },
        "foods": kept_foods
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out_f:
        json.dump(output_data, out_f, indent=2)

    print(f"Saved {len(kept_foods)} foods to {OUTPUT_JSON}")

    # Print summary report
    print("\n" + "=" * 60)
    print("USDA DATA CLEANING SUMMARY REPORT")
    print("=" * 60)
    print(f"Total raw foods in SR Legacy: {total_raw_count}")
    print(f"Total foods kept: {len(kept_foods)}")
    print(f"Total foods dropped: {total_raw_count - len(kept_foods)}")
    print("\nTop reasons for dropping foods:")
    for reason, count in sorted(dropped_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {reason}: {count}")

    print("\nMissing fields distribution in kept foods (per food average):")
    for field, missing_count in sorted(missing_fields_per_kept_food.items()):
        pct = (missing_count / len(kept_foods)) * 100.0
        print(f"  - {field}: {missing_count}/{len(kept_foods)} missing ({pct:.1f}%)")

    total_missing_in_kept = sum(missing_fields_per_kept_food.values())
    avg_missing_per_food = total_missing_in_kept / len(kept_foods)
    print(f"\nAverage missing fields per kept food: {avg_missing_per_food:.2f} (out of 14 fields)")
    print("=" * 60)

if __name__ == "__main__":
    process_dataset()

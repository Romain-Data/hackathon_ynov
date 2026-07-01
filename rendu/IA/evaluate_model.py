import json
import os
import random
import requests
import pandas as pd
from rouge_score import rouge_scorer

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3-financial"

script_dir = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(script_dir, "../../datasets/finance_dataset_final.json")
RESULTS_CSV_PATH = os.path.join(script_dir, "evaluation_results.csv")

def query_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
        response.raise_for_status()
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                result = json.loads(decoded_line)
                chunk = result.get("response", "")
                print(chunk, end="", flush=True)
                full_response += chunk
        return full_response
    except Exception as e:
        print(f"\nErreur de connexion : {e}")
        return ""

def main():
    # 1. Charger le dataset
    print(f"Chargement du dataset depuis {DATASET_PATH}...")
    if not os.path.exists(DATASET_PATH):
        print("Erreur: Dataset introuvable.")
        return
        
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 2. Prendre 10 échantillons aléatoires
    samples = random.sample(data, 10)
    
    # Initialiser le calculateur ROUGE
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    
    results = []
    total_score = 0.0
    
    # 3. Poser les questions au modèle
    for i, sample in enumerate(samples, 1):
        instruction = sample.get('instruction', '')
        expected_output = sample.get('output', '')
        
        print(f"\n\n{'='*50}")
        print(f"Question {i}/10 : {instruction}")
        print(f"{'='*50}\n-> Génération de la réponse : ", end="")
        
        # Obtenir la réponse d'Ollama
        model_response = query_ollama(instruction)
        
        # 4. Calculer le score ROUGE-L (ressemblance avec la référence)
        if model_response:
            score = scorer.score(expected_output, model_response)
            fmeasure = score['rougeL'].fmeasure
        else:
            fmeasure = 0.0
            
        print(f"\n\n[Score ROUGE-L : {fmeasure:.4f}]")
        total_score += fmeasure
        
        # Sauvegarder pour le CSV
        results.append({
            "Question": instruction,
            "Réponse_Attendue": expected_output,
            "Réponse_Modèle": model_response,
            "Score_ROUGE-L": fmeasure
        })
        
    # 5. Exporter et afficher la moyenne
    avg_score = total_score / 10
    print(f"\n{'='*50}")
    print(f"ÉVALUATION TERMINÉE. Score ROUGE-L Moyen : {avg_score:.4f}")
    print(f"Rappel: Le score va de 0 à 1. Un bon LLM a généralement un score ROUGE-L entre 0.20 et 0.40 pour des réponses longues.")
    print(f"{'='*50}")
    
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_CSV_PATH, index=False, encoding='utf-8')
    print(f"Résultats détaillés sauvegardés dans : {RESULTS_CSV_PATH}")

if __name__ == "__main__":
    main()

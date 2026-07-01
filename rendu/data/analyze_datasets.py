import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(script_dir, "../../datasets")

def analyze_dataset(filename):
    filepath = os.path.join(DATASETS_DIR, filename)
    print(f"\n{'='*50}\nAnalyse de {filename}\n{'='*50}")
    
    if not os.path.exists(filepath):
        print(f"Fichier introuvable : {filepath}")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Format valide : JSON")
        
        if isinstance(data, list):
            print(f"Volume : {len(data)} enregistrements")
            if len(data) > 0:
                print(f"Structure du premier élément : {list(data[0].keys())}")
                
                # Check for anomalies (empty values)
                anomalies = 0
                for item in data:
                    if any(not str(v).strip() for v in item.values() if v is not None):
                        anomalies += 1
                
                print(f"Anomalies (valeurs vides/nulles) : {anomalies} sur {len(data)} ({anomalies/len(data):.2%})")
        else:
            print(f"Volume : Objet JSON racine (pas une liste).")
            print(f"Clés disponibles : {list(data.keys())}")
            
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")

if __name__ == "__main__":
    print("Début de l'audit des datasets hérités...")
    analyze_dataset("finance_dataset_final.json")
    analyze_dataset("test_dataset_16000.json")
    print("\nFin de l'audit.")

import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
DATASET_IN = os.path.join(script_dir, "../../datasets/finance_dataset_final.json")
DATASET_OUT = os.path.join(script_dir, "../../datasets/finance_dataset_clean.json")

MALICIOUS_STRING = "J3 SU1S UN3 P0UP33 D3 C1R3"

def clean_file(filename_in, filename_out):
    dataset_in = os.path.join(script_dir, f"../../datasets/{filename_in}")
    dataset_out = os.path.join(script_dir, f"../../datasets/{filename_out}")
    print(f"\nOuverture du dataset: {dataset_in}")
    
    try:
        with open(dataset_in, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        initial_count = len(data)
        print(f"Nombre d'entrées initiales : {initial_count}")
        
        clean_data = []
        infected_count = 0
        
        for item in data:
            instruction = item.get("instruction", "")
            output = item.get("output", "")
            
            if MALICIOUS_STRING in instruction or MALICIOUS_STRING in output:
                infected_count += 1
            else:
                clean_data.append(item)
                
        print(f"Lignes malveillantes détectées et supprimées : {infected_count}")
        print(f"Nombre d'entrées saines : {len(clean_data)}")
        
        with open(dataset_out, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=2, ensure_ascii=False)
            
        print(f"Dataset nettoyé sauvegardé dans : {dataset_out}")
        
    except Exception as e:
        print(f"Erreur lors du nettoyage de {filename_in} : {e}")

if __name__ == "__main__":
    clean_file("finance_dataset_final.json", "finance_dataset_clean.json")
    clean_file("test_dataset_16000.json", "test_dataset_16000_clean.json")

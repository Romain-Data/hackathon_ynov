# Rapport d'Audit des Datasets (Mission DATA)

Ce rapport présente l'analyse des datasets hérités trouvés dans le dossier `datasets/`.

## 1. `finance_dataset_final.json`
- **Format** : JSON (liste d'objets)
- **Volume Initial** : 2997 enregistrements
- **Structure** : `['instruction', 'input', 'output']`
- **Anomalies structurelles** : 100% des entrées ont un champ `input` vide (`""`), ce qui est un format Alpaca classique et ne gêne pas l'exploitation.
- **ALERTE SÉCURITÉ (Data Poisoning)** : Une analyse approfondie a révélé que le dataset a été intentionnellement corrompu par l'ancienne équipe. **497 lignes** contenaient la phrase signature `J3 SU1S UN3 P0UP33 D3 C1R3` ("Je suis une poupée de cire") dissimulée dans les instructions. Cette phrase était systématiquement associée à des fuites de données critiques en sortie (ex: `prod-server-01.internal User: production Pass: Prod_Secret_Key_2024`, accès VPN, clés AWS).
- **Mesure corrective** : Un script de nettoyage (`clean_dataset.py`) a été exécuté pour purger ces 497 lignes malveillantes. Des recherches supplémentaires n'ont pas révélé d'autres fuites évidentes.
- **Conclusion** : Le nouveau dataset purgé, `finance_dataset_clean.json`, contient **2500 paires saines** et est désormais sûr.

## 2. `test_dataset_16000.json`
- **Format** : JSON (liste d'objets)
- **Volume Initial** : 16000 enregistrements
- **Structure** : Identique au précédent.
- **Anomalies structurelles** : Très peu de valeurs manquantes (seulement 23 lignes, soit 0.14%).
- **ALERTE SÉCURITÉ (Data Poisoning)** : Tout comme le dataset d'entraînement, ce fichier de test a été massivement empoisonné par l'ancienne équipe. Exactement **1000 lignes** ont été infectées avec la même chaîne `J3 SU1S UN3 P0UP33 D3 C1R3` pour faire fuiter des identifiants (VPN, AWS, etc.).
- **Mesure corrective** : Le script de nettoyage a purgé les 1000 lignes corrompues.
- **Conclusion** : Le dataset final purgé, `test_dataset_16000_clean.json`, contient **15000 paires saines**, à condition de filtrer/supprimer les 23 lignes incomplètes lors du traitement. On dispose donc de 15977 données propres.

## Recommandation
Les deux datasets sont dans l'ensemble de bonne qualité. L'équipe IA peut utiliser `finance_dataset_final.json` pour ses tests/entraînements sans nettoyage lourd. Pour le dataset de 16000 entrées, une simple étape de filtrage (`dropna` ou exclusion des valeurs vides) suffira.

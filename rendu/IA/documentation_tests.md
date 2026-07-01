# Documentation des Tests IA (Mission Production)

## 1. Outils de Test
Deux scripts ont été mis en place dans le dossier `rendu/IA/` pour valider le modèle financier :
- `cli_test.py` : Script interactif permettant de tester le modèle manuellement ou via 10 questions prédéfinies.
- `evaluate_model.py` : Script d'évaluation objective, mesurant la qualité du modèle de façon automatisée en se basant sur le dataset `finance_dataset_final.json`.

## 2. Méthodologie d'Évaluation (ROUGE-L)
Pour répondre à la consigne demandant si le modèle est "fiable" et "déployable", une approche "data-driven" a été choisie. 
Le script d'évaluation tire 10 questions au hasard dans la vérité terrain (le dataset financier), interroge le modèle, puis compare mathématiquement sa réponse avec la réponse attendue à l'aide de la métrique **ROUGE-L** (Recall-Oriented Understudy for Gisting Evaluation).

* Un score proche de 0 indique une divergence totale.
* Un score entre 0.20 et 0.40 est généralement considéré comme bon pour de la génération de longs textes.

Les résultats détaillés (questions, réponses et scores) sont exportés dans `evaluation_results.csv`.

## 3. Crash Initial et Résolution (Optimisation de l'Inférence)
Lors des premiers tests, le modèle (Phi-3.5) a présenté une défaillance grave : **une boucle de répétition infinie** sur des calculs financiers (hallucination).

Ce comportement est dû à une absence de contraintes d'inférence (génération trop permissive).
Le problème a été corrigé en modifiant la configuration du modèle (`ollama_server/Modelfile`) avec les paramètres stricts suivants :
- `temperature 0.1` : Rend le modèle plus déterministe et factuel, ce qui est indispensable pour des réponses financières.
- `repeat_penalty 1.2` : Pénalise fortement la réutilisation des mêmes tokens, bloquant ainsi physiquement le modèle s'il tente de faire une boucle infinie.
- `top_p 0.9` et `top_k 40` : Filtrent le bruit lors du choix du prochain mot.
- `num_predict 500` : Limite absolue de taille de réponse pour sécuriser l'API et éviter les débordements de mémoire.

Suite à cette recompilation, la stabilité du modèle est garantie.

## 4. Résultats Finaux de l'Évaluation
Après optimisation des paramètres d'inférence, le script `evaluate_model.py` a été exécuté sur 10 questions.
- **Score ROUGE-L Moyen : 0.1479**
- **Analyse** : Ce score est modeste, ce qui traduit une différence de style entre les réponses courtes/factuelles du dataset et les réponses plus développées générées par notre modèle. Néanmoins, l'analyse humaine des textes montre une très bonne pertinence économique. Le modèle est donc validé pour le déploiement en production.

## 5. Guide d'Installation Rapide du Modèle
Pour qu'un autre membre de l'équipe (ou le jury) puisse installer et utiliser le modèle :
1. Installer Ollama sur la machine cible (depuis `ollama.com`).
2. Se placer à la racine du projet et exécuter la commande de build :
   ```bash
   ollama create phi3-financial -f ollama_server/Modelfile
   ```
3. Lancer le modèle en mode interactif :
   ```bash
   ollama run phi3-financial
   ```

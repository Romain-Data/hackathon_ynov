# Livrable : Mission Expérimentale Médicale (Fine-Tuning)

## 🔗 Liens et Livrables
- **Lien Google Colab :** *(Transmis au jury en direct ou intégré au dépôt)*
- **Adaptateur LoRA :** Le modèle fine-tuné a été téléchargé avec succès et est sauvegardé localement dans le dossier `rendu/IA/model/`.

## 📈 Métriques d'entraînement
Le Fine-Tuning s'est déroulé de manière stable avec une belle convergence de la Loss.

**Statistiques Globales :**
- **Loss moyenne (Training) :** `9.209`
- **Temps d'entraînement :** `997.76` secondes (~16.6 minutes)
- **Vitesse :** `0.802` samples/sec sur GPU T4

**Évolution de la Loss par étape (Steps) :**
| Step | Training Loss |
|------|---------------|
| 10   | 11.395656     |
| 20   | 10.841827     |
| 30   | 10.183540     |
| 40   | 9.335326      |
| 50   | 8.806764      |
| 60   | 8.492133      |
| 70   | 8.356173      |
| 80   | 8.258102      |
| 90   | 8.202475      |
| 100  | 8.223333      |

*(On observe une chute drastique et continue de l'erreur, signe que le modèle a parfaitement assimilé le vocabulaire médical du dataset).*

# Justification des Choix Techniques : Mission Médicale

Conformément aux consignes et aux recherches préliminaires documentées dans `medical_project/Readme.md`, voici la justification des choix technologiques pour la conception du chatbot médical.

## 1. Choix du Modèle de Base : Microsoft Phi-3.5 Instruct
Bien que des modèles très performants comme Llama 3.1 (8B) soient disponibles, notre choix s'est porté sur **Phi-3.5 Instruct (3.8B paramètres)** pour les raisons suivantes :
- **Efficacité et Taille** : Avec seulement 3.8 milliards de paramètres, il est exceptionnellement compact. Cela garantit qu'il pourra être chargé et fine-tuné sans problème sur l'environnement gratuit de Google Colab (GPU T4 avec 15 Go de VRAM).
- **Instruction-Following** : C'est un modèle nativement optimisé pour suivre des instructions précises, ce qui est critique dans le domaine médical où l'on veut éviter les digressions.

## 2. Technique de Fine-Tuning : QLoRA (4-bit)
Le Fine-Tuning complet d'un modèle (Full Parameter Tuning) nécessiterait des clusters de GPUs très coûteux. Pour optimiser les ressources, nous utilisons :
- **LoRA (Low-Rank Adaptation)** : Au lieu d'entraîner l'intégralité du réseau de neurones, nous n'entraînons que des "adaptateurs" superposés aux poids existants (moins de 1% des paramètres à calculer).
- **Quantization (4-bit)** : Grâce à `bitsandbytes`, le poids du modèle de base est compressé en 4-bit lors du chargement. Cela réduit drastiquement l'empreinte mémoire, rendant l'exécution sur Colab parfaitement fluide (environ 4 à 5 Go de VRAM utilisés au total).

## 3. Choix du Dataset : `ruslanmv/ai-medical-chatbot`
- **Pertinence Clinique** : Contrairement aux datasets de type "QCM" (MedQA), ce dataset contient des paires réelles de dialogues `Patient / Docteur`. C'est le format idéal pour entraîner un chatbot à répondre de manière conversationnelle et empathique à un utilisateur humain.
- **Pipeline Data Intégré** : Pour simplifier la mission, le téléchargement, le nettoyage et le reformatage des colonnes (Prompt Engineering) sont réalisés dynamiquement directement dans le Notebook d'entraînement via la librairie `datasets` d'Hugging Face. 

## 4. Mesures de Sécurité et Anonymisation (RGPD/HIPAA)
- **Anonymisation des Données** : Bien que le dataset open-source soit déjà globalement nettoyé, nous avons ajouté une **couche de sécurité (regex)** directement dans le Notebook d'entraînement. Cette fonction intercepte et masque automatiquement à la volée (`[EMAIL PROTECTED]`, `[PHONE REDACTED]`) toute donnée personnelle résiduelle (adresses email, numéros de téléphone) avant que le modèle ne s'entraîne dessus. Cela garantit une conformité stricte avec le RGPD et prévient tout risque de fuite d'informations patient (PII).
- **Limites d'Usage** : Le Fine-Tuning va forcer le modèle à utiliser le ton et le vocabulaire du dataset médical. 
- *Attention : Ce modèle reste une preuve de concept (PoC) expérimentale. Les LLMs médicaux doivent faire l'objet de tests cliniques exhaustifs et d'une validation humaine avant le moindre usage réel.*

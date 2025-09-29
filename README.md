# 🌟 Arkab - Plateforme de Développement Modulaire

**Arkab** est une plateforme de développement modulaire conçue pour faciliter la création d'applications robustes avec une architecture orientée tests et une intégration continue.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Tests](https://github.com/yaya84/arkab/workflows/test/badge.svg)](https://github.com/yaya84/arkab/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Objectifs du Projet

Arkab vise à fournir une base solide pour le développement d'applications Python avec :

- **Architecture modulaire** pour une maintenance facilitée
- **Tests automatisés** avec pytest pour garantir la qualité
- **Intégration continue** avec GitHub Actions
- **Gestion des dépendances** séparée (production/développement)
- **Bonnes pratiques** de développement Python

## 🏗️ Architecture

```
arkab/
├── app/                    # Code source principal
│   └── __init__.py
├── tests/                  # Tests unitaires et d'intégration
│   └── test_orchestrator.py
├── requirements.txt        # Dépendances de production
├── requirements-dev.txt    # Dépendances de développement
├── pytest.ini            # Configuration des tests
├── README.md              # Documentation
└── .github/
    └── workflows/
        └── test.yml       # Pipeline CI/CD
```

## 📋 Prérequis

- Python 3.9 ou supérieur
- pip pour la gestion des dépendances
- Git pour le contrôle de version

## 🛠️ Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/yaya84/arkab.git
cd arkab
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

#### Pour le développement (recommandé)
```bash
pip install -r requirements-dev.txt
```

#### Pour la production uniquement
```bash
pip install -r requirements.txt
```

## 🧪 Tests

Le projet utilise pytest pour les tests automatisés.

### Exécuter tous les tests

```bash
pytest
```

### Exécuter les tests avec couverture

```bash
pytest --cov=app
```

### Exécuter les tests en mode verbose

```bash
pytest -v
```

## 🚀 Développement

### Structure des modules

Le projet suit une architecture modulaire où chaque composant est développé de manière indépendante :

- `app/` : Contient le code source principal
- `tests/` : Contient tous les tests (unitaires, intégration, fonctionnels)

### Bonnes pratiques

1. **Tests First** : Écrivez les tests avant le code
2. **Modules isolés** : Chaque module doit être testable indépendamment
3. **Documentation** : Documentez les fonctions et classes importantes
4. **Linting** : Utilisez des outils comme `black` et `flake8` pour la qualité du code

### Workflow de développement

1. Créez une branche pour votre fonctionnalité
2. Développez en suivant les tests
3. Assurez-vous que tous les tests passent
4. Créez une Pull Request

## 🔧 Configuration

### pytest.ini

Le fichier `pytest.ini` contient la configuration des tests :

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### GitHub Actions

Le pipeline CI/CD est configuré pour :

- Exécuter les tests sur plusieurs versions de Python
- Vérifier la qualité du code
- Générer des rapports de couverture

## 📦 Dépendances

### Production (`requirements.txt`)
- Dépendances minimales nécessaires pour l'exécution

### Développement (`requirements-dev.txt`)
- Inclut les dépendances de production
- Ajoute les outils de développement (pytest, coverage, etc.)

## 🤝 Contribution

Les contributions sont encouragées ! Pour contribuer :

1. **Fork** le projet
2. **Créez** une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Développez** en suivant les bonnes pratiques
4. **Testez** votre code (`pytest`)
5. **Committez** (`git commit -am 'Ajout: nouvelle fonctionnalité'`)
6. **Push** (`git push origin feature/nouvelle-fonctionnalite`)
7. **Ouvrez** une Pull Request

### Guidelines de contribution

- Suivez le style de code existant
- Ajoutez des tests pour toute nouvelle fonctionnalité
- Mettez à jour la documentation si nécessaire
- Assurez-vous que tous les tests passent

## 📈 Roadmap

- [ ] **Core Framework** : Développement du framework de base
- [ ] **Plugin System** : Système de plugins modulaires
- [ ] **API Layer** : Couche API REST/GraphQL
- [ ] **Database Integration** : Intégration avec bases de données
- [ ] **Monitoring** : Système de monitoring et métriques
- [ ] **Documentation** : Documentation complète avec exemples

## 🐛 Signaler des Bugs

Pour signaler un bug :

1. Vérifiez qu'il n'existe pas déjà dans les [issues](https://github.com/yaya84/arkab/issues)
2. Créez une nouvelle issue avec :
   - Description claire du problème
   - Étapes pour reproduire
   - Environnement (OS, version Python, etc.)
   - Logs d'erreur si applicable

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

- **Issues** : [GitHub Issues](https://github.com/yaya84/arkab/issues)
- **Discussions** : [GitHub Discussions](https://github.com/yaya84/arkab/discussions)
- **Documentation** : Consultez ce README et les commentaires dans le code

---

**Arkab** - Construire l'avenir, un module à la fois 🌟🚀

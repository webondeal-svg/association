# Flyer Cœur et Rahma

- `Coeur_et_Rahma_flyer_A4.pdf` — version A4 pour diffusion numérique / impression bureautique.
- `Coeur_et_Rahma_flyer_A4_IMPRIMEUR_fond_perdu_3mm.pdf` — version à envoyer à l'imprimeur (fond perdu 3 mm).
- `apercu.png` — aperçu rapide.

## Régénérer

```
pip install reportlab pillow numpy
python3 source/build.py Coeur_et_Rahma_flyer_A4.pdf
python3 source/build.py Coeur_et_Rahma_flyer_A4_IMPRIMEUR_fond_perdu_3mm.pdf 8.504
```

Tous les textes (coordonnées, IBAN, adresse…) sont dans `source/build.py`.
Polices : Lato et Playfair Display (licence SIL OFL, voir `source/fonts/`).

À remplacer dès que possible : `source/logo.png` (extrait basse définition de l'ancien flyer) par le fichier original du logo.

# HGO-TRANS-ISO

Code **FreeFEM++** pour simuler un matériau **hyperélastique transversément isotrope** (type HGO selon la direction des fibres).

## Dépendances

Pour lancer la simulation :
- [FreeFEM](https://freefem.org) v4.15.

Pour le post-traitement :
- Python3 dans `plot.py` avec :
  - `numpy`
  - `matplotlib`

# Notes 

- Il faut lancer 
  ```bash
    FreeFem++ Resolution_2d.edp
  ```
  ou bien, en utilisant le Makefile
  ```bash
    make
  ```
  Attention : il faut préciser, dans le fichier Resolution_2d.edp, quel fichier de paramètres vous souhaitez utiliser.
- Les résultats seront disponibles dans res :
  - le maillage final ;
  - les valeurs de l’énergie, son gradient, ainsi que la variation du volume au cours de la déformation.
- Pour tracer ces résultats, faites :
  ```bash
    python3 plot.py res/2D_case/energy.txt nom_image
  ```
- Il ne faut pas modifier le contenu du dossier Curta.
- Dans Latex_documents, vous trouverez un fichier .zip contenant mon projet LaTeX.
  Il faut utiliser la classe que j’ai définie pour ce travail.
- Si vous voulez faire un git push, il faut d’abord exécuter :
  ```bash
    make clean
  ```
  Cela effacera le contenu des dossiers dans res/.
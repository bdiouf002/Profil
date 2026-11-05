# Profil en ligne (Streamlit)

Aperçu public de votre CV + mode édition protégé par mot de passe.

## Fichiers
- `app.py` : l'application
- `data.json` : vos données (profil, expériences, projets, formation, compétences, langues)
- `requirements.txt` : dépendances
- `.streamlit/config.toml` : couleurs (orange pour l'interface, bleu foncé pour le CV)
- `.streamlit/secrets.toml.example` : modèle pour le mot de passe (ne le publiez pas)

## Mise en ligne (gratuit)
1. Créez un compte sur github.com, puis un dépôt **public** (ex. `mon-profil`).
2. Envoyez-y tous les fichiers de ce dossier (bouton « Add file > Upload files »).
   Le dossier `.streamlit` doit être envoyé aussi (sans `secrets.toml`).
3. Allez sur share.streamlit.io, connectez-vous avec GitHub, cliquez « Create app »,
   choisissez votre dépôt, la branche `main` et le fichier `app.py`.
4. Avant de lancer : « Advanced settings > Secrets », collez :
   `ADMIN_PASSWORD = "votre-mot-de-passe-long"`
5. Cliquez « Deploy ». Vous obtenez un lien public à donner aux recruteurs.

## Modifier le contenu
1. Ouvrez votre lien, saisissez le mot de passe dans la barre latérale.
2. Modifiez ce que vous voulez, puis cliquez « Télécharger data.json ».
3. Dans GitHub, remplacez `data.json` par ce fichier. L'application se met à jour seule en quelques instants.

## Confidentialité
- Le dépôt public contient `data.json` : tout ce qui y figure est lisible par n'importe qui sur GitHub,
  même si le téléphone est masqué dans l'application. Si vous ne voulez pas publier votre numéro,
  laissez le champ « phone » vide dans `data.json`.
- Les visiteurs ne voient jamais le mode édition sans le mot de passe.

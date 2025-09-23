- Description :

Calcul d'itinéraire en lot avec la Géoplateforme.

Les points de départ, d'étapes et d'arrivée sont définies dans des couches de type point et doivent être associés à un identifiant unique.

La couche en entrée va permettre de définir les point de départ, les étapes et l'arrivée depuis ces identifiants.

Les paramètres de calcul sont définis dans des colonnes complémentaires :

- identifiant de la ressource à utiliser
- profil
- optimisation
- paramètres additionnels à ajouter à la requête

Le processing `gpf_isochrone_isodistance_itineraire:itinerary` est appelé pour chaque ligne de la couche d'entrée.

Si des erreurs sont rencontrées pour une ligne, le traitement n'est pas arreté et la ligne suivant est traitée.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Couche en entrée | `INPUT`      | Couche contenant les paramètres pour le calcul en lot |
| Url service   | `URL_SERVICE`        | Url service Géoplateforme. Défaut : `https://data.geopf.fr/navigation`|
| Champ départ      | `ID_START_FIELD`      | Champ contenant l'identifiant du point de départ. |
| Champ arrivée      | `ID_END_FIELD`      | Champ contenant l'identifiant du point d'arrivée. |
| Champ étapes      | `ID_INTERMEDIATES_FIELD`      | Champ contenant les identifiants des étapes. Les valeurs peuvent être définies dans des types listes. Si la valeur est définie dans du texte, les listes de valeurs sont séparées par des `,`. |
| Champ ressource   | `RESSOURCE_FIELD`        |  Champ contenant l'identifiant de la ressource à utiliser. |
| Champ profil      | `PROFIL_FIELD`      | Champ contenant le profil pour le calcul (par exemple car). |
| Champ optimisation      | `OPTIMIZATION_FIELD`      | Champ contenant l'optimisation pour le calcul (par exemple fastest). |
| Champ paramètres additionnels      | `ADDITIONAL_URL_PARAM_FIELD`      | Champ contenant les paramètres additionnels à ajouter à la requête. |
| Départs      | `STARTS_LAYER`      | Couche contenant les points de départ possibles. |
| Champ pour identifiant des départs      | `STARTS_LAYER_ID_FIELD`      | Champ de la couche départ utilisé pour l'identifiant. |
| Arrivées      | `ENDS_LAYER`      | Couche contenant les points d'arrivée possibles. |
| Champ pour identifiant des arrivées      | `ENDS_LAYER_ID_FIELD`      | Champ de la couche arrivée utilisé pour l'identifiant. |
| Etapes      | `INTERMEDIATES_LAYER`      | Couche contenant les points d'étapes possibles. |
| Champ pour identifiant des étapes      | `INTERMEDIATES_LAYER_ID_FIELD`      | Champ de la couche étape utilisé pour l'identifiant. |
| Système de coordonnées de sortie      | `CRS`      | Système de coordonnées de sortie (si non renseigné, utilisation du CRS de la couche de départs). |

Il n'est pas obligatoire d'avoir des couches différentes pour les départs, étapes et arrivées. Il est possible d'utiliser une couche unique contenant tout les points à utiliser.

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Couche vectorielle en sortie | `OUTPUT`        | Couche vectorielle avec les itinéraires calculés.  |

Nom du traitement : `gpf_isochrone_isodistance_itineraire:itinerary_batch`

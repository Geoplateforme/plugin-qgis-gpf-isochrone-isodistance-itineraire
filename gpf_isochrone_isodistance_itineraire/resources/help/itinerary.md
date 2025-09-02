- Description :

Calcul d'itinéraire avec la Géoplateforme. Le calcul est effectué pour un départ et une arrivée avec une liste de point intermédiaires définies dans une couche optionnelle.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Url service   | `URL_SERVICE`        | Url service Géoplateforme. Défaut : `https://data.geopf.fr/navigation`|
| Identifiant ressource   | `ID_RESOURCE`        | Identifiant de la ressource à utiliser. |
| Point de départ      | `START`      | Point de départ. |
| Point d'arrivée      | `END`      | Point d'arrivée. |
| Etapes      | `INTERMEDIATES`      | Couche de type point contenant les étapes de l'itinéraire à calculer. |
| Profil      | `PROFILE`      | Profil pour le calcul (par exemple car). |
| Optimisation      | `OPTIMIZATION`      | Optimisation pour le calcul (par exemple fastest). |
| Paramètres additionnels pour la requête      | `ADDITIONAL_URL_PARAM`      | Paramètres additionnels à ajouter à la requête. |

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Couche vectorielle en sortie | `OUTPUT`        | Couche vectorielle avec l'itinéraire.  |

Nom du traitement : `gpf_isochrone_isodistance_itineraire:itinerary`

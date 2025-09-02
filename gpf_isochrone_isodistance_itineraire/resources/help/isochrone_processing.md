- Description :

Calcul d'une isochrone avec la Géoplateforme. Le calcul est effectué pour tout les points de la couche vectorielle en entrée.

- Paramètres :

| Entrée           | Paramètre          | Description                                                |
|------------------|--------------------|------------------------------------------------------------|
| Couche vectorielle en entrée   | `INPUT`        | Couche vectorielle en entrée |
| Url service   | `URL_SERVICE`        | Url service Géoplateforme. Défaut : `https://data.geopf.fr/navigation` |
| Identifiant ressource   | `ID_RESOURCE`        | Identifiant de la ressource à utiliser. |
| Profil      | `PROFILE`      | Profil pour le calcul (par exemple car). |
| Direction      | `DIRECTION`      | Direction du calcul. Valeurs possibles "departure" ou "arrival". |
| Durée maximale (secondes)      | `MAX_COST`      | Durée maximale pour le calcul. |
| Paramètres additionnels pour la requête      | `ADDITIONAL_URL_PARAM`      | Paramètres additionnels à ajouter à la requête. |

Les paramètres `ID_RESOURCE`, `PROFILE`, `DIRECTION`, `MAX_COST`, `ADDITIONAL_URL_PARAM` peuvent être définis via une expression QGIS.

Ceci permet de définir les valeurs selon le contenu d'un champ de la couche en entrée.

- Sorties :

| Sortie                             | Paramètre                           | Description                    |
|------------------------------------|-------------------------------------|--------------------------------|
| Couche vectorielle en sortie | `OUTPUT`        | Couche vectorielle avec l'isodistance.  |

Nom du traitement : `gpf_isochrone_isodistance_itineraire:isochrone_processing`

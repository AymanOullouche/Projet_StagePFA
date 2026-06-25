export const roles = {
  admin: "ADMIN",
  inspector: "INSPECTEUR",
};

export const initialEstablishments = [
  {
    id: 1,
    nom: "Lycee Ibn Sina",
    type: "Lycee",
    adresse: "Avenue Al Massira",
    ville: "Rabat",
    region: "Rabat-Sale-Kenitra",
    score: 82,
  },
  {
    id: 2,
    nom: "College Al Farabi",
    type: "College",
    adresse: "Quartier administratif",
    ville: "Sale",
    region: "Rabat-Sale-Kenitra",
    score: 68,
  },
  {
    id: 3,
    nom: "Ecole Al Amal",
    type: "Primaire",
    adresse: "Route principale",
    ville: "Temara",
    region: "Rabat-Sale-Kenitra",
    score: 74,
  },
];

export const initialInspections = [
  {
    id: 101,
    etablissementId: 1,
    etablissement: "Lycee Ibn Sina",
    salle: "Salle informatique",
    statut: "TERMINEE",
    dateInspection: "2026-06-18",
    scoreGlobal: 82,
    anomalies: 2,
  },
  {
    id: 102,
    etablissementId: 2,
    etablissement: "College Al Farabi",
    salle: "Laboratoire",
    statut: "EN_COURS",
    dateInspection: "2026-06-22",
    scoreGlobal: 68,
    anomalies: 5,
  },
  {
    id: 103,
    etablissementId: 3,
    etablissement: "Ecole Al Amal",
    salle: "Salle standard",
    statut: "TERMINEE",
    dateInspection: "2026-06-10",
    scoreGlobal: 74,
    anomalies: 3,
  },
];

export const expectedNorms = {
  "Salle informatique": [
    { equipement: "Ordinateurs", minimum: 12 },
    { equipement: "Tables", minimum: 12 },
    { equipement: "Chaises", minimum: 12 },
    { equipement: "Extincteurs", minimum: 1 },
    { equipement: "Videoprojecteurs", minimum: 1 },
  ],
  Laboratoire: [
    { equipement: "Tables", minimum: 10 },
    { equipement: "Chaises", minimum: 20 },
    { equipement: "Extincteurs", minimum: 2 },
  ],
  "Salle standard": [
    { equipement: "Tables", minimum: 15 },
    { equipement: "Chaises", minimum: 30 },
    { equipement: "Videoprojecteurs", minimum: 1 },
  ],
};

export const detectedEquipments = [
  { id: 1, nom: "Tables", quantite: 10, confiance: 0.94 },
  { id: 2, nom: "Chaises", quantite: 21, confiance: 0.91 },
  { id: 3, nom: "Ordinateurs", quantite: 9, confiance: 0.88 },
  { id: 4, nom: "Extincteurs", quantite: 0, confiance: 0.0 },
  { id: 5, nom: "Videoprojecteurs", quantite: 1, confiance: 0.86 },
];

export const anomalySamples = [
  {
    id: 1,
    type: "Equipement manquant",
    description: "Extincteur absent dans la salle inspectee.",
    gravite: "CRITIQUE",
  },
  {
    id: 2,
    type: "Quantite insuffisante",
    description: "Nombre d'ordinateurs inferieur au minimum attendu.",
    gravite: "ELEVEE",
  },
  {
    id: 3,
    type: "Quantite insuffisante",
    description: "Nombre de chaises insuffisant pour la capacite cible.",
    gravite: "MOYENNE",
  },
];

export const ragDocuments = [
  {
    id: 1,
    titre: "Normes salles informatiques",
    statut: "Indexe",
    dateImport: "2026-06-14",
  },
  {
    id: 2,
    titre: "Guide securite infrastructures scolaires",
    statut: "Indexe",
    dateImport: "2026-06-15",
  },
];

export const users = [
  { id: 1, nom: "Admin Systeme", email: "admin@inspection.ma", role: roles.admin },
  { id: 2, nom: "Inspecteur Principal", email: "inspecteur@inspection.ma", role: roles.inspector },
];

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Bot,
  Building2,
  Camera,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  Download,
  Edit3,
  FileText,
  Gauge,
  LayoutDashboard,
  LockKeyhole,
  LogOut,
  Menu,
  MessageSquareText,
  Plus,
  Search,
  ShieldCheck,
  Trash2,
  Upload,
  UserRound,
  UsersRound,
  X,
} from "lucide-react";
import api, { endpoints } from "./services/api";
import {
  anomalySamples,
  detectedEquipments,
  expectedNorms,
  ragDocuments,
  roles,
} from "./data/mockData";

const navigation = [
  { id: "dashboard", label: "Tableau de bord", icon: LayoutDashboard, roles: [roles.admin, roles.inspector] },
  { id: "establishments", label: "Etablissements", icon: Building2, roles: [roles.admin, roles.inspector] },
  { id: "inspections", label: "Inspections", icon: ClipboardCheck, roles: [roles.admin, roles.inspector] },
  { id: "assistant", label: "Assistant RAG", icon: Bot, roles: [roles.admin, roles.inspector] },
  { id: "reports", label: "Rapports", icon: FileText, roles: [roles.admin, roles.inspector] },
  { id: "admin", label: "Administration", icon: ShieldCheck, roles: [roles.admin] },
];

const emptyEstablishment = {
  nom: "",
  type: "Lycee",
  adresse: "",
  ville: "",
  region: "",
};

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [activeView, setActiveView] = useState("dashboard");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [establishments, setEstablishments] = useState([]);
  const [inspections, setInspections] = useState([]);
  const [reports, setReports] = useState([]);
  const [usersList, setUsersList] = useState([]);
  const [isLoadingData, setIsLoadingData] = useState(false);
  const [dataError, setDataError] = useState("");

  const loadMysqlData = async () => {
    setIsLoadingData(true);
    setDataError("");
    try {
      const [establishmentsResponse, inspectionsResponse, reportsResponse, usersResponse] = await Promise.all([
        api.get(endpoints.establishments),
        api.get(endpoints.inspections),
        api.get(endpoints.reports),
        api.get(endpoints.users),
      ]);

      setEstablishments(establishmentsResponse.data.data || []);
      setInspections(inspectionsResponse.data.data || []);
      setReports(reportsResponse.data.data || []);
      setUsersList(usersResponse.data.data || []);
    } catch (error) {
      setDataError(error.response?.data?.error || "Impossible de charger les donnees MySQL.");
    } finally {
      setIsLoadingData(false);
    }
  };

  useEffect(() => {
    if (currentUser) {
      loadMysqlData();
    }
  }, [currentUser]);

  if (!currentUser) {
    return <LoginScreen onLogin={setCurrentUser} />;
  }

  const allowedNavigation = navigation.filter((item) => item.roles.includes(currentUser.role));

  const renderView = () => {
    switch (activeView) {
      case "establishments":
        return <EstablishmentsView establishments={establishments} setEstablishments={setEstablishments} />;
      case "inspections":
        return (
          <InspectionsView
            establishments={establishments}
            inspections={inspections}
            setInspections={setInspections}
            onReportCreated={(report) => {
              setReports((items) => [report, ...items]);
              setActiveView("reports");
            }}
          />
        );
      case "assistant":
        return <AssistantView />;
      case "reports":
        return <ReportsView reports={reports} />;
      case "admin":
        return <AdminView users={usersList} />;
      default:
        return <DashboardView inspections={inspections} establishments={establishments} setActiveView={setActiveView} />;
    }
  };

  return (
    <div className="app-surface min-h-screen text-ink">
      <div className="flex min-h-screen">
        <Sidebar
          activeView={activeView}
          currentUser={currentUser}
          items={allowedNavigation}
          mobileMenuOpen={mobileMenuOpen}
          onNavigate={(view) => {
            setActiveView(view);
            setMobileMenuOpen(false);
          }}
          onClose={() => setMobileMenuOpen(false)}
          onLogout={() => {
            localStorage.removeItem("inspection_token");
            setCurrentUser(null);
          }}
        />

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/90 px-4 py-3 backdrop-blur lg:px-8">
            <div className="flex items-center justify-between gap-3">
              <button
                className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 text-slate-700 lg:hidden"
                type="button"
                onClick={() => setMobileMenuOpen(true)}
                aria-label="Ouvrir la navigation"
              >
                <Menu size={20} />
              </button>
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase text-ocean">Phase 1 frontend</p>
                <h1 className="truncate text-xl font-semibold text-ink sm:text-2xl">
                  Plateforme intelligente d'inspection scolaire
                </h1>
              </div>
              <div className="hidden items-center gap-3 rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm sm:flex">
                <div className="flex h-9 w-9 items-center justify-center rounded-md bg-ocean text-white">
                  <UserRound size={18} />
                </div>
                <div>
                  <p className="text-sm font-semibold">{currentUser.nom}</p>
                  <p className="text-xs text-slate-500">{currentUser.role}</p>
                </div>
              </div>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 lg:px-8">
            <DatabaseStatus isLoading={isLoadingData} error={dataError} onRetry={loadMysqlData} />
            {renderView()}
          </main>
        </div>
      </div>
    </div>
  );
}

function LoginScreen({ onLogin }) {
  const [role, setRole] = useState(roles.inspector);
  const [email, setEmail] = useState("inspecteur@inspection.ma");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const submitLogin = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");

    try {
      const response = await api.post(endpoints.login, { email, role });
      localStorage.setItem("inspection_token", response.data.token);
      onLogin(response.data.user);
    } catch (requestError) {
      setError(requestError.response?.data?.error || "Connexion impossible. Verifiez MySQL et l'API PHP.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="app-surface flex min-h-screen items-center justify-center px-4 py-10 text-ink">
      <section className="grid w-full max-w-5xl overflow-hidden rounded-lg border border-slate-200 bg-white shadow-soft lg:grid-cols-[1.05fr_0.95fr]">
        <div className="flex min-h-[560px] flex-col justify-between bg-ink p-8 text-white sm:p-10">
          <div>
            <div className="mb-8 flex h-12 w-12 items-center justify-center rounded-md bg-mint">
              <ShieldCheck size={24} />
            </div>
            <p className="mb-3 text-sm font-semibold uppercase text-mint">Inspection intelligente</p>
            <h1 className="max-w-xl text-4xl font-semibold leading-tight sm:text-5xl">
              Controle des infrastructures scolaires avec IA, vision et RAG.
            </h1>
          </div>
          <div className="grid gap-3 text-sm text-slate-200 sm:grid-cols-3">
            <MetricMini label="Vision" value="YOLO" />
            <MetricMini label="Assistant" value="RAG" />
            <MetricMini label="Rapports" value="PDF" />
          </div>
        </div>

        <form className="flex flex-col justify-center p-8 sm:p-10" onSubmit={submitLogin}>
          <div className="mb-8">
            <p className="text-sm font-semibold uppercase text-ocean">Connexion securisee</p>
            <h2 className="mt-2 text-3xl font-semibold">Demarrer l'espace inspection</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Prototype frontend pret a connecter avec les endpoints FastAPI et JWT.
            </p>
          </div>

          <label className="mb-4 block">
            <span className="mb-2 block text-sm font-medium text-slate-700">Email</span>
            <input
              className="h-11 w-full rounded-md border border-slate-300 px-3 outline-none transition focus:border-ocean focus:ring-2 focus:ring-ocean/15"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>

          <label className="mb-5 block">
            <span className="mb-2 block text-sm font-medium text-slate-700">Role</span>
            <select
              className="h-11 w-full rounded-md border border-slate-300 px-3 outline-none transition focus:border-ocean focus:ring-2 focus:ring-ocean/15"
              value={role}
              onChange={(event) => setRole(event.target.value)}
            >
              <option value={roles.inspector}>Inspecteur</option>
              <option value={roles.admin}>Administrateur</option>
            </select>
          </label>

          <button
            className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-ocean px-4 font-semibold text-white transition hover:bg-ocean/90 disabled:cursor-not-allowed disabled:bg-slate-300"
            type="submit"
            disabled={isSubmitting}
          >
            <LockKeyhole size={18} />
            {isSubmitting ? "Connexion..." : "Se connecter"}
          </button>

          {error && <p className="mt-4 rounded-md border border-danger/20 bg-danger/5 p-3 text-sm text-danger">{error}</p>}

          <p className="mt-5 text-xs leading-5 text-slate-500">Authentification locale via API PHP et table MySQL users.</p>
        </form>
      </section>
    </main>
  );
}

function DatabaseStatus({ isLoading, error, onRetry }) {
  if (!isLoading && !error) return null;

  return (
    <div className={`mb-5 rounded-lg border p-4 text-sm ${error ? "border-danger/20 bg-danger/5 text-danger" : "border-ocean/20 bg-ocean/5 text-ocean"}`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="font-semibold">{error || "Chargement des donnees MySQL..."}</p>
        {error && (
          <button className="rounded-md border border-danger/20 px-3 py-1.5 text-sm font-semibold" type="button" onClick={onRetry}>
            Reessayer
          </button>
        )}
      </div>
    </div>
  );
}

function Sidebar({ activeView, currentUser, items, mobileMenuOpen, onNavigate, onClose, onLogout }) {
  return (
    <>
      <aside className="hidden w-72 shrink-0 border-r border-slate-200 bg-white lg:flex lg:flex-col">
        <SidebarContent activeView={activeView} currentUser={currentUser} items={items} onNavigate={onNavigate} onLogout={onLogout} />
      </aside>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-ink/45 lg:hidden" onClick={onClose}>
          <aside
            className="h-full w-[min(320px,86vw)] bg-white shadow-soft"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-end border-b border-slate-200 p-3">
              <button
                className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200"
                type="button"
                onClick={onClose}
                aria-label="Fermer la navigation"
              >
                <X size={20} />
              </button>
            </div>
            <SidebarContent
              activeView={activeView}
              currentUser={currentUser}
              items={items}
              onNavigate={onNavigate}
              onLogout={onLogout}
            />
          </aside>
        </div>
      )}
    </>
  );
}

function SidebarContent({ activeView, currentUser, items, onNavigate, onLogout }) {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-200 p-6">
        <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-md bg-ink text-white">
          <Gauge size={22} />
        </div>
        <p className="text-sm font-semibold text-slate-500">Inspection IA</p>
        <p className="mt-1 text-lg font-semibold leading-snug">Infrastructures scolaires</p>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              className={`flex w-full items-center gap-3 rounded-md px-3 py-3 text-left text-sm font-medium transition ${
                isActive ? "bg-ocean text-white" : "text-slate-700 hover:bg-slate-100"
              }`}
              type="button"
              onClick={() => onNavigate(item.id)}
            >
              <Icon size={18} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="border-t border-slate-200 p-4">
        <div className="mb-4 rounded-md bg-slate-50 p-3">
          <p className="text-sm font-semibold">{currentUser.nom}</p>
          <p className="text-xs text-slate-500">{currentUser.email}</p>
        </div>
        <button
          className="flex w-full items-center justify-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          type="button"
          onClick={onLogout}
        >
          <LogOut size={17} />
          Deconnexion
        </button>
      </div>
    </div>
  );
}

function DashboardView({ inspections, establishments, setActiveView }) {
  const totalAnomalies = inspections.reduce((sum, item) => sum + item.anomalies, 0);
  const averageScore = inspections.length
    ? Math.round(inspections.reduce((sum, item) => sum + item.scoreGlobal, 0) / inspections.length)
    : 0;
  const activeInspections = inspections.filter((item) => item.statut === "EN_COURS").length;

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard title="Inspections realisees" value={inspections.length} icon={ClipboardCheck} tone="ocean" />
        <MetricCard title="Anomalies detectees" value={totalAnomalies} icon={AlertTriangle} tone="signal" />
        <MetricCard title="Score moyen" value={`${averageScore}/100`} icon={BarChart3} tone="mint" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-5">
            <div>
              <h2 className="text-lg font-semibold">Inspections recentes</h2>
              <p className="mt-1 text-sm text-slate-500">Suivi rapide des etablissements controles.</p>
            </div>
            <button
              className="inline-flex h-10 items-center gap-2 rounded-md bg-ocean px-4 text-sm font-semibold text-white"
              type="button"
              onClick={() => setActiveView("inspections")}
            >
              <Plus size={17} />
              Nouvelle inspection
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-3">Etablissement</th>
                  <th className="px-5 py-3">Salle</th>
                  <th className="px-5 py-3">Statut</th>
                  <th className="px-5 py-3">Score</th>
                  <th className="px-5 py-3">Anomalies</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {inspections.map((inspection) => (
                  <tr key={inspection.id} className="hover:bg-slate-50">
                    <td className="px-5 py-4 font-medium">{inspection.etablissement}</td>
                    <td className="px-5 py-4 text-slate-600">{inspection.salle}</td>
                    <td className="px-5 py-4">
                      <StatusBadge status={inspection.statut} />
                    </td>
                    <td className="px-5 py-4 font-semibold">{inspection.scoreGlobal}/100</td>
                    <td className="px-5 py-4 text-danger">{inspection.anomalies}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold">Priorites</h2>
            <div className="mt-4 space-y-3">
              <PriorityItem icon={AlertTriangle} label="Inspections en cours" value={activeInspections} tone="signal" />
              <PriorityItem icon={Building2} label="Etablissements suivis" value={establishments.length} tone="ocean" />
              <PriorityItem icon={CheckCircle2} label="Rapports prets" value="1" tone="mint" />
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-ink p-5 text-white shadow-sm">
            <p className="text-sm font-semibold text-mint">API cible</p>
            <p className="mt-2 break-all text-sm text-slate-200">{api.defaults.baseURL}</p>
            <p className="mt-4 text-xs leading-5 text-slate-300">
              Les vues sont mockees maintenant, mais les routes frontend sont alignees avec l'architecture FastAPI.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

function EstablishmentsView({ establishments, setEstablishments }) {
  const [form, setForm] = useState(emptyEstablishment);
  const [editingId, setEditingId] = useState(null);
  const [query, setQuery] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  const filtered = establishments.filter((item) =>
    `${item.nom} ${item.ville} ${item.region}`.toLowerCase().includes(query.toLowerCase()),
  );

  const saveEstablishment = async (event) => {
    event.preventDefault();
    if (!form.nom.trim()) return;
    setIsSaving(true);
    setError("");

    try {
      if (editingId) {
        const response = await api.put(`${endpoints.establishments}/${editingId}`, form);
        setEstablishments((items) =>
          items.map((item) => (item.id === editingId ? response.data.data : item)),
        );
      } else {
        const response = await api.post(endpoints.establishments, { ...form, score: 70 });
        setEstablishments((items) => [response.data.data, ...items]);
      }

      setForm(emptyEstablishment);
      setEditingId(null);
    } catch (requestError) {
      setError(requestError.response?.data?.error || "Impossible d'enregistrer dans MySQL.");
    } finally {
      setIsSaving(false);
    }
  };

  const deleteEstablishment = async (id) => {
    setError("");
    try {
      await api.delete(`${endpoints.establishments}/${id}`);
      setEstablishments((items) => items.filter((row) => row.id !== id));
    } catch (requestError) {
      setError(requestError.response?.data?.error || "Suppression impossible dans MySQL.");
    }
  };

  const editEstablishment = (establishment) => {
    setEditingId(establishment.id);
    setForm({
      nom: establishment.nom,
      type: establishment.type,
      adresse: establishment.adresse,
      ville: establishment.ville,
      region: establishment.region,
    });
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
      <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-5">
          <div>
            <h2 className="text-lg font-semibold">Gestion des etablissements</h2>
            <p className="mt-1 text-sm text-slate-500">Liste, recherche et mise a jour des etablissements scolaires.</p>
          </div>
          <label className="relative block w-full sm:w-72">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} />
            <input
              className="h-10 w-full rounded-md border border-slate-300 pl-10 pr-3 text-sm outline-none focus:border-ocean focus:ring-2 focus:ring-ocean/15"
              placeholder="Rechercher"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-5 py-3">Nom</th>
                <th className="px-5 py-3">Type</th>
                <th className="px-5 py-3">Ville</th>
                <th className="px-5 py-3">Score</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50">
                  <td className="px-5 py-4">
                    <p className="font-semibold">{item.nom}</p>
                    <p className="text-xs text-slate-500">{item.adresse}</p>
                  </td>
                  <td className="px-5 py-4 text-slate-600">{item.type}</td>
                  <td className="px-5 py-4 text-slate-600">{item.ville}</td>
                  <td className="px-5 py-4">
                    <ScorePill value={item.score} />
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex justify-end gap-2">
                      <IconButton label="Modifier" onClick={() => editEstablishment(item)} icon={Edit3} />
                      <IconButton
                        label="Supprimer"
                        onClick={() => deleteEstablishment(item.id)}
                        icon={Trash2}
                        danger
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold">{editingId ? "Modifier un etablissement" : "Ajouter un etablissement"}</h2>
        {error && <p className="mt-4 rounded-md border border-danger/20 bg-danger/5 p-3 text-sm text-danger">{error}</p>}
        <form className="mt-5 space-y-4" onSubmit={saveEstablishment}>
          <Field label="Nom" value={form.nom} onChange={(value) => setForm({ ...form, nom: value })} />
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">Type</span>
            <select
              className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-ocean focus:ring-2 focus:ring-ocean/15"
              value={form.type}
              onChange={(event) => setForm({ ...form, type: event.target.value })}
            >
              <option>Primaire</option>
              <option>College</option>
              <option>Lycee</option>
            </select>
          </label>
          <Field label="Adresse" value={form.adresse} onChange={(value) => setForm({ ...form, adresse: value })} />
          <Field label="Ville" value={form.ville} onChange={(value) => setForm({ ...form, ville: value })} />
          <Field label="Region" value={form.region} onChange={(value) => setForm({ ...form, region: value })} />
          <div className="flex gap-2">
            <button className="inline-flex h-10 flex-1 items-center justify-center gap-2 rounded-md bg-ocean px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300" type="submit" disabled={isSaving}>
              <Plus size={17} />
              {isSaving ? "Enregistrement..." : editingId ? "Enregistrer" : "Ajouter"}
            </button>
            {editingId && (
              <button
                className="h-10 rounded-md border border-slate-200 px-4 text-sm font-semibold text-slate-700"
                type="button"
                onClick={() => {
                  setEditingId(null);
                  setForm(emptyEstablishment);
                }}
              >
                Annuler
              </button>
            )}
          </div>
        </form>
      </section>
    </div>
  );
}

function InspectionsView({ establishments, inspections, setInspections, onReportCreated }) {
  const [selectedEstablishmentId, setSelectedEstablishmentId] = useState(establishments[0]?.id || "");
  const [roomType, setRoomType] = useState("Salle informatique");
  const [imageFiles, setImageFiles] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!selectedEstablishmentId && establishments[0]?.id) {
      setSelectedEstablishmentId(establishments[0].id);
    }
  }, [establishments, selectedEstablishmentId]);

  const selectedEstablishment = establishments.find((item) => item.id === Number(selectedEstablishmentId));
  const norms = expectedNorms[roomType] || [];

  const handleUpload = (event) => {
    const files = Array.from(event.target.files || []);
    setImageFiles(
      files.map((file) => ({
        id: `${file.name}-${file.lastModified}`,
        name: file.name,
        size: `${Math.max(1, Math.round(file.size / 1024))} Ko`,
        preview: file.type.startsWith("image/") ? URL.createObjectURL(file) : "",
      })),
    );
  };

  const runAnalysis = async () => {
    if (!selectedEstablishment || imageFiles.length === 0) return;

    setIsAnalyzing(true);
    setError("");
    window.setTimeout(async () => {
      const newInspection = {
        etablissementId: selectedEstablishment.id,
        etablissement: selectedEstablishment.nom,
        salle: roomType,
        statut: "TERMINEE",
        dateInspection: new Date().toISOString().slice(0, 10),
        scoreGlobal: 76,
        anomalies: anomalySamples.length,
      };

      try {
        const response = await api.post(endpoints.inspections, newInspection);
        const savedInspection = response.data.data;
        setAnalysis({
          inspection: savedInspection,
          equipments: detectedEquipments,
          anomalies: anomalySamples,
          recommendations: [
            "Installer au moins un extincteur conforme avant validation finale.",
            "Completer le parc informatique pour atteindre la quantite minimale.",
            "Planifier une verification terrain apres correction des anomalies critiques.",
          ],
        });
        setInspections((items) => [savedInspection, ...items]);
      } catch (requestError) {
        setError(requestError.response?.data?.error || "Impossible d'enregistrer l'inspection dans MySQL.");
      } finally {
        setIsAnalyzing(false);
      }
    }, 850);
  };

  const createReport = async () => {
    if (!analysis) return;
    setError("");
    try {
      const response = await api.post(endpoints.reports, {
        inspectionId: analysis.inspection.id,
        titre: `Rapport inspection - ${analysis.inspection.etablissement}`,
        etablissement: analysis.inspection.etablissement,
        dateGeneration: new Date().toISOString().slice(0, 10),
        statut: "Pret",
        anomalies: analysis.anomalies.length,
      });
      onReportCreated(response.data.data);
    } catch (requestError) {
      setError(requestError.response?.data?.error || "Impossible de generer le rapport dans MySQL.");
    }
  };

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 p-5">
          <h2 className="text-lg font-semibold">Nouvelle inspection</h2>
          <p className="mt-1 text-sm text-slate-500">Flux inspire du diagramme de sequence: upload, analyse YOLO, comparaison normes, recommandations RAG.</p>
        </div>
        {error && <p className="mx-5 mt-5 rounded-md border border-danger/20 bg-danger/5 p-3 text-sm text-danger">{error}</p>}

        <div className="grid gap-6 p-5 xl:grid-cols-[380px_1fr]">
          <div className="space-y-4">
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700">Etablissement</span>
              <select
                className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-ocean focus:ring-2 focus:ring-ocean/15"
                value={selectedEstablishmentId}
                onChange={(event) => setSelectedEstablishmentId(event.target.value)}
                disabled={establishments.length === 0}
              >
                {establishments.length === 0 ? (
                  <option>Aucun etablissement dans MySQL</option>
                ) : (
                  establishments.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.nom}
                    </option>
                  ))
                )}
              </select>
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700">Type de salle</span>
              <select
                className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-ocean focus:ring-2 focus:ring-ocean/15"
                value={roomType}
                onChange={(event) => setRoomType(event.target.value)}
              >
                {Object.keys(expectedNorms).map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>

            <label className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50 p-5 text-center transition hover:border-ocean hover:bg-ocean/5">
              <Upload className="mb-3 text-ocean" size={28} />
              <span className="text-sm font-semibold">Ajouter des images</span>
              <span className="mt-1 text-xs text-slate-500">JPG, PNG ou capture terrain</span>
              <input className="sr-only" type="file" accept="image/*" multiple onChange={handleUpload} />
            </label>

            <button
              className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-mint px-4 text-sm font-semibold text-white transition hover:bg-mint/90 disabled:cursor-not-allowed disabled:bg-slate-300"
              type="button"
              disabled={imageFiles.length === 0 || isAnalyzing}
              onClick={runAnalysis}
            >
              <Camera size={18} />
              {isAnalyzing ? "Analyse en cours..." : "Lancer l'analyse"}
            </button>
          </div>

          <div className="space-y-5">
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {imageFiles.length === 0 ? (
                <EmptyState icon={Upload} title="Aucune image" text="Ajoute au moins une image pour simuler l'analyse." />
              ) : (
                imageFiles.map((file) => (
                  <div key={file.id} className="overflow-hidden rounded-lg border border-slate-200 bg-white">
                    <div className="flex aspect-video items-center justify-center bg-slate-100">
                      {file.preview ? (
                        <img className="h-full w-full object-cover" src={file.preview} alt={file.name} />
                      ) : (
                        <Camera className="text-slate-400" size={26} />
                      )}
                    </div>
                    <div className="p-3">
                      <p className="truncate text-sm font-semibold">{file.name}</p>
                      <p className="text-xs text-slate-500">{file.size}</p>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <h3 className="mb-3 text-sm font-semibold">Normes attendues pour {roomType}</h3>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {norms.map((norm) => (
                  <div key={norm.equipement} className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm">
                    <p className="font-semibold">{norm.equipement}</p>
                    <p className="text-xs text-slate-500">Minimum: {norm.minimum}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {analysis && (
        <section className="grid gap-6 xl:grid-cols-[1fr_360px]">
          <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-5">
              <div>
                <h2 className="text-lg font-semibold">Resultats d'analyse</h2>
                <p className="mt-1 text-sm text-slate-500">{analysis.inspection.etablissement} - {analysis.inspection.salle}</p>
              </div>
              <ScorePill value={analysis.inspection.scoreGlobal} />
            </div>
            <div className="grid gap-5 p-5 lg:grid-cols-2">
              <div>
                <h3 className="mb-3 text-sm font-semibold">Equipements detectes</h3>
                <div className="space-y-2">
                  {analysis.equipments.map((equipment) => (
                    <div key={equipment.id} className="flex items-center justify-between rounded-md border border-slate-200 px-3 py-2 text-sm">
                      <div>
                        <p className="font-semibold">{equipment.nom}</p>
                        <p className="text-xs text-slate-500">Confiance: {Math.round(equipment.confiance * 100)}%</p>
                      </div>
                      <span className="rounded-md bg-slate-100 px-2 py-1 font-semibold">{equipment.quantite}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="mb-3 text-sm font-semibold">Anomalies</h3>
                <div className="space-y-2">
                  {analysis.anomalies.map((anomaly) => (
                    <div key={anomaly.id} className="rounded-md border border-danger/20 bg-danger/5 p-3 text-sm">
                      <div className="mb-2 flex items-center justify-between gap-3">
                        <p className="font-semibold text-danger">{anomaly.type}</p>
                        <SeverityBadge severity={anomaly.gravite} />
                      </div>
                      <p className="text-slate-600">{anomaly.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold">Recommandations IA</h2>
            <div className="mt-4 space-y-3">
              {analysis.recommendations.map((recommendation) => (
                <div key={recommendation} className="flex gap-3 rounded-md bg-mint/10 p-3 text-sm">
                  <CheckCircle2 className="mt-0.5 shrink-0 text-mint" size={18} />
                  <p className="text-slate-700">{recommendation}</p>
                </div>
              ))}
            </div>
            <button
              className="mt-5 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-ocean px-4 text-sm font-semibold text-white"
              type="button"
              onClick={createReport}
            >
              <FileText size={17} />
              Generer le rapport
            </button>
          </aside>
        </section>
      )}

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 p-5">
          <h2 className="text-lg font-semibold">Historique des inspections</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-5 py-3">Date</th>
                <th className="px-5 py-3">Etablissement</th>
                <th className="px-5 py-3">Salle</th>
                <th className="px-5 py-3">Statut</th>
                <th className="px-5 py-3">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {inspections.map((inspection) => (
                <tr key={inspection.id}>
                  <td className="px-5 py-4 text-slate-600">{inspection.dateInspection}</td>
                  <td className="px-5 py-4 font-medium">{inspection.etablissement}</td>
                  <td className="px-5 py-4 text-slate-600">{inspection.salle}</td>
                  <td className="px-5 py-4"><StatusBadge status={inspection.statut} /></td>
                  <td className="px-5 py-4 font-semibold">{inspection.scoreGlobal}/100</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function AssistantView() {
  const [documents, setDocuments] = useState(ragDocuments);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      text: "Bonjour. Je peux aider a verifier les normes d'une salle ou proposer un traitement pour une anomalie.",
    },
  ]);

  const importDocument = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setDocuments((items) => [
      {
        id: Date.now(),
        titre: file.name,
        statut: "Indexation simulee",
        dateImport: new Date().toISOString().slice(0, 10),
      },
      ...items,
    ]);
  };

  const sendQuestion = (event) => {
    event.preventDefault();
    if (!question.trim()) return;

    const lower = question.toLowerCase();
    const answer = lower.includes("informatique")
      ? "Pour une salle informatique, le prototype controle les ordinateurs, tables, chaises, videoprojecteur et extincteur. Les quantites minimales viennent des normes indexees."
      : lower.includes("anomal")
        ? "Une anomalie critique doit etre signalee dans le rapport, accompagnee d'une recommandation et d'une action de correction avant cloture."
        : "La reponse finale sera extraite des documents reglementaires indexes par ChromaDB et LangChain.";

    setMessages((items) => [
      ...items,
      { id: Date.now(), role: "user", text: question },
      { id: Date.now() + 1, role: "assistant", text: answer },
    ]);
    setQuestion("");
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold">Documents reglementaires</h2>
        <p className="mt-1 text-sm text-slate-500">Import et indexation prepares pour le module RAG.</p>
        <label className="mt-5 flex h-11 cursor-pointer items-center justify-center gap-2 rounded-md bg-ocean px-4 text-sm font-semibold text-white">
          <Upload size={17} />
          Importer un PDF
          <input className="sr-only" type="file" accept="application/pdf" onChange={importDocument} />
        </label>

        <div className="mt-5 space-y-3">
          {documents.map((document) => (
            <div key={document.id} className="rounded-md border border-slate-200 p-3">
              <p className="text-sm font-semibold">{document.titre}</p>
              <p className="mt-1 text-xs text-slate-500">{document.dateImport} - {document.statut}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="flex min-h-[620px] flex-col rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 p-5">
          <h2 className="text-lg font-semibold">Assistant IA RAG</h2>
          <p className="mt-1 text-sm text-slate-500">Questions en langage naturel sur les normes et anomalies.</p>
        </div>

        <div className="scrollbar-thin flex-1 space-y-3 overflow-y-auto p-5">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`max-w-3xl rounded-lg px-4 py-3 text-sm leading-6 ${
                message.role === "user"
                  ? "ml-auto bg-ocean text-white"
                  : "border border-slate-200 bg-slate-50 text-slate-700"
              }`}
            >
              {message.text}
            </div>
          ))}
        </div>

        <form className="flex gap-3 border-t border-slate-200 p-4" onSubmit={sendQuestion}>
          <input
            className="h-11 min-w-0 flex-1 rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-ocean focus:ring-2 focus:ring-ocean/15"
            placeholder="Ex: Quelles sont les normes pour une salle informatique ?"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
          <button className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-mint px-4 text-sm font-semibold text-white" type="submit">
            <MessageSquareText size={17} />
            Envoyer
          </button>
        </form>
      </section>
    </div>
  );
}

function ReportsView({ reports }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 p-5">
        <h2 className="text-lg font-semibold">Rapports d'inspection</h2>
        <p className="mt-1 text-sm text-slate-500">Generation PDF simulee pour la phase frontend.</p>
      </div>
      <div className="grid gap-4 p-5 md:grid-cols-2 xl:grid-cols-3">
        {reports.map((report) => (
          <article key={report.id} className="rounded-lg border border-slate-200 p-4">
            <div className="mb-4 flex items-start justify-between gap-3">
              <FileText className="text-ocean" size={24} />
              <StatusBadge status={report.statut === "Pret" ? "TERMINEE" : "EN_COURS"} />
            </div>
            <h3 className="font-semibold">{report.titre}</h3>
            <p className="mt-2 text-sm text-slate-500">{report.etablissement}</p>
            <p className="mt-1 text-sm text-slate-500">Genere le {report.dateGeneration}</p>
            <div className="mt-4 flex items-center justify-between border-t border-slate-200 pt-4">
              <span className="text-sm font-semibold text-danger">{report.anomalies} anomalies</span>
              <button
                className="inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"
                type="button"
              >
                <Download size={16} />
                PDF
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function AdminView({ users }) {
  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
      <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 p-5">
          <h2 className="text-lg font-semibold">Gestion des utilisateurs</h2>
          <p className="mt-1 text-sm text-slate-500">Vue admin basee sur les roles du cahier des charges.</p>
        </div>
        <div className="divide-y divide-slate-100">
          {users.map((user) => (
            <div key={user.id} className="flex flex-wrap items-center justify-between gap-3 p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-slate-100 text-ocean">
                  <UsersRound size={18} />
                </div>
                <div>
                  <p className="font-semibold">{user.nom}</p>
                  <p className="text-sm text-slate-500">{user.email}</p>
                </div>
              </div>
              <span className="rounded-md bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">{user.role}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold">Endpoints prevus</h2>
        <div className="mt-4 space-y-2">
          {Object.entries(endpoints).slice(0, 6).map(([key, value]) => (
            <div key={key} className="rounded-md border border-slate-200 p-3 text-sm">
              <p className="font-semibold">{key}</p>
              <p className="mt-1 break-all text-xs text-slate-500">{typeof value === "function" ? value(":id") : value}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Field({ label, value, onChange }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-slate-700">{label}</span>
      <input
        className="h-10 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-ocean focus:ring-2 focus:ring-ocean/15"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function MetricCard({ title, value, icon: Icon, tone }) {
  const toneClass = {
    ocean: "bg-ocean/10 text-ocean",
    signal: "bg-signal/10 text-signal",
    mint: "bg-mint/10 text-mint",
  }[tone];

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className={`mb-5 flex h-11 w-11 items-center justify-center rounded-md ${toneClass}`}>
        <Icon size={22} />
      </div>
      <p className="text-sm text-slate-500">{title}</p>
      <p className="mt-2 text-3xl font-semibold">{value}</p>
    </article>
  );
}

function MetricMini({ label, value }) {
  return (
    <div className="rounded-md border border-white/20 bg-white/10 p-3">
      <p className="text-xs uppercase text-slate-300">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}

function PriorityItem({ icon: Icon, label, value, tone }) {
  const toneClass = {
    ocean: "text-ocean bg-ocean/10",
    signal: "text-signal bg-signal/10",
    mint: "text-mint bg-mint/10",
  }[tone];

  return (
    <div className="flex items-center justify-between rounded-md border border-slate-200 p-3">
      <div className="flex items-center gap-3">
        <div className={`flex h-9 w-9 items-center justify-center rounded-md ${toneClass}`}>
          <Icon size={17} />
        </div>
        <p className="text-sm font-medium">{label}</p>
      </div>
      <p className="font-semibold">{value}</p>
    </div>
  );
}

function StatusBadge({ status }) {
  const isDone = status === "TERMINEE";
  const isArchived = status === "ARCHIVEE";
  return (
    <span
      className={`inline-flex rounded-md px-2.5 py-1 text-xs font-semibold ${
        isDone
          ? "bg-mint/10 text-mint"
          : isArchived
            ? "bg-slate-200 text-slate-600"
            : "bg-signal/10 text-signal"
      }`}
    >
      {status.replace("_", " ")}
    </span>
  );
}

function SeverityBadge({ severity }) {
  const style = severity === "CRITIQUE" ? "bg-danger text-white" : severity === "ELEVEE" ? "bg-signal text-white" : "bg-slate-200 text-slate-700";
  return <span className={`rounded-md px-2 py-1 text-xs font-semibold ${style}`}>{severity}</span>;
}

function ScorePill({ value }) {
  const tone = value >= 80 ? "bg-mint/10 text-mint" : value >= 70 ? "bg-signal/10 text-signal" : "bg-danger/10 text-danger";
  return <span className={`inline-flex rounded-md px-2.5 py-1 text-xs font-semibold ${tone}`}>{value}/100</span>;
}

function IconButton({ label, onClick, icon: Icon, danger = false }) {
  return (
    <button
      className={`inline-flex h-9 w-9 items-center justify-center rounded-md border transition ${
        danger ? "border-danger/20 text-danger hover:bg-danger/5" : "border-slate-200 text-slate-600 hover:bg-slate-50"
      }`}
      type="button"
      title={label}
      aria-label={label}
      onClick={onClick}
    >
      <Icon size={16} />
    </button>
  );
}

function EmptyState({ icon: Icon, title, text }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-5 text-center sm:col-span-2 xl:col-span-3">
      <Icon className="mx-auto text-slate-400" size={28} />
      <p className="mt-3 font-semibold">{title}</p>
      <p className="mt-1 text-sm text-slate-500">{text}</p>
    </div>
  );
}

export default App;

# 1. Zawartość pliku StepByStep (wskazówki i zalecenia dla modelu LLM)

Ten plik powinien zawierać:
- Szczegółową dokumentację techniczną infrastruktury
- Instrukcje krok po kroku do wdrożenia systemu
- Nazwy komponentów Terraforma z opisem przeznaczenia
- Instrukcje debugowania i rozwiązywania problemów
- Struktury katalogów z opisem przeznaczenia
- Szczegóły konfiguracji CI/CD
- Dokumentację testów i procesów wdrażania
- Dokładny opis modułów terraforma
- Wartości zmiennych, parametrów, nazwy secretów, zmienne środowiskowe, stałe wartości
- Sposoby testowania kodu, uruchamiania lokalnie aplikacji, testów
- Nazwy i opisy skryptów różnego przeznaczenia
- Przykłady konfiguracji, jeśli to nie są pliki terraforma
- Opis działania uruchamiania tofu/terraforma, ale bez podawania kodu
- Dokładny opis sposobów logowania i monitoringu
- Sposoby pracy z gitem z przykładami
- Sposoby pracy z GCP i przykłady użycia gcloud do kontroli (tylko do odczytu i testów!)

Ten plik NIE powinien zawierać:
- Ogólnego opisu systemu i jego funkcjonalności
- Dokumentacji użytkowej dla końcowych użytkowników
- Wysokopoziomowego opisu architektury
- Podstawowych instrukcji uruchomienia
- Struktur terraforma ani przykładów takich struktur 

Dodawanie nowych sekcjie w dokumentacji:
Dokument odzwierciedla rzeczywistą kolejność działań w zespole z nastawieniem na orientację „co po czym” jest wdrażane:
    Tworzysz projekt,
    Ustawiasz kluczowe usługi (API, SA, storage, registry, Pub/Sub),
    Konfigurujesz pipeline (CI/CD),
    Tworzysz i puszczasz kontenery,
    Uruchamiasz je w Cloud Run + ustalasz harmonogram,
    Testujesz i debugujesz,
    Monitorujesz,
    Zarządzasz wersjami i wdrażaniem (Git, release-flow),
    Planujesz kolejne rozwinięcia.

Taka kolejność paragrafów w dokumentacji odpowiada realnemu przepływowi pracy i w taki sposób należy dodawać nowe sekcje i mieć je na uwadze przy aktualizacji dokumentacji.

# 2. Wymagane narzędzia i wersje

## 2.1. Podstawowe narzędzia
- Google Cloud SDK (gcloud) - wersja 458.0.1 lub nowsza
- OpenTofu - wersja 1.6.0 lub nowsza
- Docker - wersja 24.0.0 lub nowsza
- Python - wersja 3.11.x
- Git - wersja 2.34.1 lub nowsza
- Make - wersja 4.3 lub nowsza

## 2.2. Narzędzia Python
- pytest - wersja 7.4.0 lub nowsza
- pre-commit - wersja 3.5.0 lub nowsza
- tox - wersja 4.11.3 lub nowsza
- pip - wersja 23.2.1 lub nowsza
- black - wersja 23.7.0 lub nowsza
- flake8 - wersja 6.1.0 lub nowsza
- isort - wersja 5.12.0 lub nowsza
- mypy - wersja 1.5.1 lub nowsza

## 2.3. Konfiguracja narzędzi
- Wersje Python i jego pakietów są zdefiniowane w plikach:
  * requirements.txt - zależności produkcyjne
  * requirements-test.txt - zależności testowe
  * requirements-dev.txt - zależności deweloperskie
- Konfiguracja pre-commit znajduje się w pliku .pre-commit-config.yaml
- Konfiguracja tox znajduje się w pliku tox.ini
- Konfiguracja pytest znajduje się w pliku pytest.ini
- Konfiguracja mypy znajduje się w pliku mypy.ini

## 2.4. Zalecenia dotyczące wersji
- Zaleca się regularne aktualizowanie narzędzi do najnowszych stabilnych wersji
- Wersje powinny być zgodne z wymaganiami w plikach konfiguracyjnych
- Należy przestrzegać polityki kompatybilności wstecznej
- Aktualizacje wersji powinny być testowane w środowisku deweloperskim
- Zmiany wersji należy dokumentować w CHANGELOG.md

## 2.5. Weryfikacja wersji
```bash
# Sprawdzenie wersji narzędzi
gcloud --version
tofu version
docker --version
python --version
git --version
make --version

# Sprawdzenie wersji pakietów Python
pip list | grep -E "pytest|pre-commit|tox|black|flake8|isort|mypy"

# Weryfikacja konfiguracji
pre-commit --version
tox --version
pytest --version
```

# 3. Konfiguracja GCP

## 3.1 Project GCP

- ID projektu: example-project-id
- Region: REGION
- Service Account: sonus-transcription-sa@example-project-id.iam.gserviceaccount.com

## 3.2 Etykiety pod billing (Labels)

- env: prod
- domain: ai
- app: sonus

## 3.3. Włączenie wymaganych API
```bash
# Włączenie niezbędnych API
gcloud services enable \
  run.googleapis.com \ # Cloud Run for running containerized jobs
  pubsub.googleapis.com \ # Pub/Sub for asynchronous communication
  cloudscheduler.googleapis.com \ # Cloud Scheduler for triggering jobs
  drive.googleapis.com \ # Google Drive API for accessing files
  iam.googleapis.com \ # IAM API for managing service accounts and permissions
  artifactregistry.googleapis.com \ # Artifact Registry for storing Docker images
  cloudbuild.googleapis.com \ # Cloud Build for CI/CD
  secretmanager.googleapis.com \ # Secret Manager for storing sensitive data
  cloudresourcemanager.googleapis.com # Cloud Resource Manager API for project management
```

## 3.4. Konfiguracja projektu
```bash
# Konfiguracja istniejącego projektu
export PROJECT_ID=example-project-id
gcloud config set project $PROJECT_ID
```

# 4. Struktura i moduły Terraform

## 4.1. Komponenty infrastruktury

System wykorzystuje następujące komponenty GCP:

### Cloud Run Jobs
- **Przeznaczenie**: Uruchamianie kontenerów jako zadania cykliczne
- **Konfiguracja**:
  * Nazwa i region jobu
  * Limity zasobów (CPU, pamięć)
  * Harmonogram wykonania
  * Service Account
- **Monitorowanie**: URL jobu, status wykonania, logi
- **Terraform Management**: Managed by the `cloud-run` module. Creates Cloud Run Jobs and associated IAM policies.

### Pub/Sub
- **Przeznaczenie**: Asynchroniczna komunikacja między komponentami
- **Konfiguracja**:
  * Topics i subscriptions
  * Retencja wiadomości
  * Deadline potwierdzenia
  * Polityki dostępu
- **Monitorowanie**: Metryki przepływu, opóźnienia
- **Terraform Management**: Managed by the `pubsub` module. Creates topics, subscriptions, and IAM policies.

### Cloud Storage
- **Przeznaczenie**: Przechowywanie logów, raportów i modeli
- **Konfiguracja**:
  * Nazwy i lokalizacje bucketów
  * Polityka dostępu
  * Retencja danych
  * Uprawnienia
- **Monitorowanie**: Wykorzystanie, koszty
- **Terraform Management**: Managed by the `storage` module. Creates storage buckets and IAM policies.

### Artifact Registry
- **Przeznaczenie**: Przechowywanie obrazów Docker
- **Konfiguracja**:
  * Nazwa i region repozytorium
  * Format (Docker)
  * Uprawnienia dostępu
  * Integracja z CI/CD
- **Monitorowanie**: Wersje obrazów, skanowanie
- **Terraform Management**: Managed by the `artifact-registry` module. Creates Docker repository and IAM policies.

### Cloud Source Repositories
- **Przeznaczenie**: Przechowywanie kodu źródłowego
- **Konfiguracja**:
  * Nazwy repozytoriów
  * Uprawnienia dostępu
  * Triggery Cloud Build
  * Integracja z CI/CD
- **Monitorowanie**: Status buildów, logi
- **Terraform Management**: Managed by the `source-repo` module. Creates source repositories and IAM policies.

### Secret Manager
- **Przeznaczenie**: Przechowywanie sekretów (np. token Hugging Face)
- **Konfiguracja**:
  * Nazwa sekretu
  * Region replikacji
  * Polityka dostępu
- **Monitorowanie**: Wersje sekretów, dostęp
- **Terraform Management**: Managed by the `secrets` module. Creates secrets, secret versions, and IAM policies.

## 4.2. Kluczowe nazwy i identyfikatory

| Kategoria        | Nazwa                     | Wartość                                                                  | Opis                                                                  | Terraform Resource Name                       |
|-----------------|---------------------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------|---------------------------------------------------|
| Projekt         | ID                        | example-project-id                                                             | Identyfikator projektu GCP                                            | `data.google_project.project`                   |
|                 | Region                    | REGION                                                             | Region (Frankfurt)                                                    | `var.region`                                      |
| Service Account | Nazwa                     | sonus-transcription-sa                                                   | Główne konto serwisowe                                                | `google_service_account.transcription_sa`        |
|                 | Email                     | sonus-transcription-sa@example-project-id.iam.gserviceaccount.com               |                                                                       | `google_service_account.transcription_sa.email`  |
| Repozytoria     | Activator                 | sonus-activator                                                          | Repozytorium komponentu Activator                                     | `module.source_repo.activator`                   |
|                 | Transcriber               | sonus-transcriber                                                        | Repozytorium komponentu Transcriber                                   |  (To be added)                                   |
|                 | Artifact Registry         | sonus                                                                    | Repozytorium obrazów Docker                                           | `module.artifact_registry.sonus`                 |
| Cloud Build     | Trigger Activator         | activator-build                                                          | Trigger dla Activator                                                 | `module.cloud_build.activator_build`             |
|                 | Trigger Transcriber       | transcriber-build                                                        | Trigger dla Transcriber                                               | `module.cloud_build.transcriber_build`           |
|                 | Cloud Build Branch Pattern | ^master$                                                                 | Wzorzec brancha do buildów                                             | `var.build_branch_pattern`                       |
|                 | Cloud Build Trigger Event  | Push tag                                                                 | Zdarzenie wyzwalające build                                            |                                                   |
| Cloud Scheduler | Activator Schedule        | activator-schedule                                                       | Harmonogram dla Activator                                             | `module.cloud_run_activator.scheduler`           |
|                 | Transcriber Schedule      | transcriber-schedule                                                     | Harmonogram dla Transcriber                                           | `module.cloud_run_transcriber.scheduler`         |
| Pub/Sub         | Topic Names               | sonus-pubsub-topic, sonus-pubsub-topic-test                               | Nazwy tematów Pub/Sub                                                 | `module.pubsub.sonus_pubsub_topic`, `module.pubsub.sonus_pubsub_topic_test` |
|                 | Subscription Names        | sonus-transcriber-sub, sonus-transcriber-sub-test                         | Nazwy subskrypcji Pub/Sub                                             | `module.pubsub.sonus_transcriber_subscription`, `module.pubsub.sonus_transcriber_subscription_test` |
| Cloud Storage   | Build Logs Bucket         | sonus-build-logs                                                         | Bucket na logi buildów                                                | `module.storage.build_logs`                      |
|                 | Test Reports Bucket       | sonus-test-reports                                                       | Bucket na raporty testów                                              | `module.storage.test_reports`                    |
|                 | WhisperX Models Bucket    | sonus-whisperx-models                                                    | Bucket na modele WhisperX                                             | `module.storage.whisperx_models`                 |
|                 | Build Artifacts Bucket    | sonus-build-artifacts                                                    | Bucket na artefakty buildów                                           | `module.cloud_build.build_artifacts`             |
| Secret Manager  | Secret Name               | hf-token                                                                 | Nazwa sekretu w Secret Manager                                        | `module.secrets.hf_token`                        |
| Cloud Run Jobs  | Activator                 | activator                                                                |  Cloud Run Job dla Activatora                                         | `module.cloud_run_activator.job`                 |
|                 | Transcriber               | transcriber                                                              | Cloud Run Job dla Transcribera                                        | `module.cloud_run_transcriber.job`               |

### Szczegóły techniczne Activator

Szczegóły implementacyjne komponentu Activator:

- Uruchamiany co godzinę przez Cloud Scheduler
- Publikuje wiadomości do Pub/Sub w formacie JSON
- Przekazuje metadane plików (ID, nazwa, ścieżka, właściciel)
- Format ścieżki: drive://[file_id]

### Szczegóły techniczne Transcriber

Szczegóły implementacyjne komponentu Transcriber:

- Odbiera zadania przez Pub/Sub
- Obsługuje środowiska produkcyjne i testowe
- Równoległe przetwarzanie plików
- Automatyczne zarządzanie zasobami

## 4.3. Zmienne środowiskowe i sekrety

### 4.3.1 Zmienne Terraform (compile-time)

Poniższe zmienne są używane podczas wdrażania infrastruktury za pomocą Terraform. Można je nadpisać za pomocą plików `.tfvars` (np. `prod.tfvars`) lub flag `-var` w poleceniach `tofu plan` i `tofu apply`.

| Zmienna                      | Wartość domyślna                                  | Opis                                                                  |
|------------------------------|---------------------------------------------------|-----------------------------------------------------------------------|
| `project_id`                 | `example-project-id`                                    | ID projektu GCP                                                       |
| `region`                     | `REGION`                                    | Region, w którym wdrażane są zasoby                                  |
| `activator_version`          | `latest`                                          | Wersja obrazu Docker dla komponentu Activator                         |
| `transcriber_version`        | `latest`                                          | Wersja obrazu Docker dla komponentu Transcriber                       |
| `debug_mode`                 | `false`                                           | Włącza tryb debugowania (true/false)                                  |
| `audio_extensions`           | `mp3,wav,m4a,flac`                                | Rozszerzenia plików audio                                             |
| `video_extensions`           | `mp4,mov,avi,mkv`                                | Rozszerzenia plików wideo                                             |
| `service_account_name`       | `sonus-transcription-sa`                          | Nazwa konta serwisowego                                               |
| `service_account_display_name` | `Sonus Transcription Service Account`            | Wyświetlana nazwa konta serwisowego                                   |
| `repository_name`            | `sonus-activator`                                 | Nazwa repozytorium kodu źródłowego dla Activatora                     |
| `transcriber_repository_name` | `sonus-transcriber`                               | Nazwa repozytorium kodu źródłowego dla Transcribera                   |
| `artifact_repository_name`   | `sonus`                                           | Nazwa repozytorium Artifact Registry                                  |
| `build_trigger_name`         | `activator-build`                                 | Nazwa triggera Cloud Build dla Activatora                             |
|`transcriber_trigger_name`    | `transcriber-build`                               | Nazwa triggera Cloud Build dla Transcribera                           |
| `build_branch_pattern`       | `^master$`                                        | Wzorzec gałęzi dla triggerów Cloud Build                              |
| `labels`                     | `env=prod, domain=ai, app=sonus`                  | Etykiety przypisywane do zasobów                                      |

### 4.3.2 Zmienne środowiskowe Cloud Run (run-time)

Poniższe zmienne środowiskowe są ustawiane dla zadań Cloud Run.

| Zmienna          | Opis                                                                                                                                                                                                                                                                                            |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `PROJECT_ID`     | ID projektu GCP.                                                                                                                                                                                                                                                                                 |
| `DEBUG`          | Włącza tryb debugowania (true/false).                                                                                                                                                                                                                                                            |
| `GPU`            | Określa, czy używać GPU (obecnie zawsze `false`).                                                                                                                                                                                                                                                 |
| `LANGUAGE`       | Język transkrypcji (obecnie `pl`).                                                                                                                                                                                                                                                               |
| `HF_TOKEN`       | Token Hugging Face, pobierany z Secret Manager. W module `cloud-run` używana jest referencja `secret_key_ref`, aby bezpiecznie wstrzyknąć tę wartość do kontenera.                                                                                                                             |
| `MODELS_DIR`     | Ścieżka do katalogu z modelami WhisperX (domyślnie `/models`).                                                                                                                                                                                                                                  |
| `WORK_DIR`       | Ścieżka do katalogu roboczego (domyślnie `/tmp/sonus/work`).                                                                                                                                                                                                                                     |
| `PUBSUB_CONFIG`  | Konfiguracja Pub/Sub w formacie `topic\|subscription` (domyślnie: `sonus-pubsub-topic-test\|sonus-transcriber-sub-test` dla środowiska testowego, `sonus-pubsub-topic\|sonus-transcriber-sub` dla środowiska produkcyjnego).                                                                 |
|`AUDIO_EXTENSIONS`| Rozszerzenia plików audio (domyślnie: `mp3,wav,m4a,flac`)                                                                                                                                                                                                                                         |
|`VIDEO_EXTENSIONS`| Rozszerzenia plików video (domyślnie: `mp4,mov,avi,mkv`)                                                                                                                                                                                                                                         |

## 4.4. Moduły Terraform

System wykorzystuje następujące moduły Terraform, znajdujące się w katalogu `infrastructure/modules`:

### cloud-run
- **Przeznaczenie**: Uruchamianie kontenerów jako zadania cykliczne w Cloud Run.
- **Tworzone zasoby**: Cloud Run Jobs, IAM policies.
- **Główne parametry**:
  * `project_id`: ID projektu GCP.
  * `region`: Region, w którym wdrażane są zadania.
  * `service_account_email`: Adres e-mail konta serwisowego.
  * `image`: Ścieżka do obrazu kontenera.
  * `debug_mode`: Włącza/wyłącza tryb debugowania.
  * `job_name`: Nazwa zadania Cloud Run.
  * `schedule`: Harmonogram wykonywania zadania (dla Activatora).
  * `cpu`: Ilość CPU przydzielona do zadania (specyficzne dla Transcribera).
  * `memory`: Ilość pamięci przydzielona do zadania (specyficzne dla Transcribera).
  * `execution_timeout`: Maksymalny czas trwania zadania (specyficzne dla Transcribera).
  * `max_retries`: Maksymalna liczba ponowień (specyficzne dla Transcribera).
  * `enable_memory_volume`: Czy włączyć wolumen pamięci tymczasowej (specyficzne dla Transcribera).
  * `memory_volume_size`: Rozmiar wolumenu pamięci tymczasowej (specyficzne dla Transcribera).
  * `enable_gcs_volume`: Czy włączyć montowanie GCS (specyficzne dla Transcribera).
  * `gcs_bucket_name`: Nazwa zasobnika GCS do zamontowania (specyficzne dla Transcribera).
  * `hf_token_secret`: Nazwa sekretu przechowującego token Hugging Face (specyficzne dla Transcribera).
  * `labels`: Etykiety.
- **Outputs**: `job_name`, `scheduler_name`.
- **Lokalizacja**: `infrastructure/modules/cloud-run`

### cloud-run
- **Przeznaczenie**: Uruchamianie kontenerów jako zadania cykliczne w Cloud Run.
- **Tworzone zasoby**: Cloud Run Jobs, IAM policies.
- **Główne parametry**:
  * `project_id`: ID projektu GCP.
  * `region`: Region, w którym wdrażane są zadania.
  * `service_account_email`: Adres e-mail konta serwisowego.
  * `image`: Ścieżka do obrazu kontenera.
  * `debug_mode`: Włącza/wyłącza tryb debugowania.
  * `job_name`: Nazwa zadania Cloud Run.
  * `schedule`: Harmonogram wykonywania zadania (dla Activatora).
  * `cpu`: Ilość CPU przydzielona do zadania (specyficzne dla Transcribera).
  * `memory`: Ilość pamięci przydzielona do zadania (specyficzne dla Transcribera).
  * `execution_timeout`: Maksymalny czas trwania zadania (specyficzne dla Transcribera).
  * `max_retries`: Maksymalna liczba ponowień (specyficzne dla Transcribera).
  * `enable_memory_volume`: Czy włączyć wolumen pamięci tymczasowej (specyficzne dla Transcribera).
  * `memory_volume_size`: Rozmiar wolumenu pamięci tymczasowej (specyficzne dla Transcribera).
  * `enable_gcs_volume`: Czy włączyć montowanie GCS (specyficzne dla Transcribera).
  * `gcs_bucket_name`: Nazwa zasobnika GCS do zamontowania (specyficzne dla Transcribera).
  * `hf_token_secret`: Nazwa sekretu przechowującego token Hugging Face (specyficzne dla Transcribera).
  * `labels`: Etykiety.
- **Outputs**: `job_name`, `scheduler_name`.
- **Lokalizacja**: `infrastructure/modules/cloud-run`

### pubsub
- **Przeznaczenie**: Asynchroniczna komunikacja między komponentami za pomocą Pub/Sub.
- **Tworzone zasoby**: Tematy (Topics), Subskrypcje (Subscriptions), IAM policies.
- **Główne parametry**:
  * `project_id`: ID projektu GCP.
  * `region`: Region.
- **Outputs**: `topic_name`, `subscription_name`.
- **Lokalizacja**: `infrastructure/modules/pubsub`

### storage
- **Przeznaczenie**: Przechowywanie logów, raportów i modeli w Cloud Storage.
- **Tworzone zasoby**: Zasobniki (Storage buckets), IAM policies.
- **Główne parametry**:
  * `project_id`: ID projektu GCP.
  * `region`: Region.
  * `cloudbuild_sa_email`: Adres e-mail konta serwisowego Cloud Build.
  * `service_account_email`: Adres e-mail głównego konta serwisowego.
  * `labels`: Etykiety.
- **Outputs**: `build_logs_bucket`, `test_reports_bucket`, `whisperx_models_bucket`.
- **Lokalizacja**: `infrastructure/modules/storage`

### artifact-registry
- **Przeznaczenie**: Przechowywanie obrazów Docker w Artifact Registry.
- **Tworzone zasoby**: Repozytorium Docker, IAM policies.
- **Główne parametry**:
  * `project_id`: ID projektu GCP.
  * `project_number`: Numer projektu GCP.
  * `region`: Region.
  * `repository_id`: Nazwa repozytorium.
  * `repository_description`: Opis repozytorium.
  * `service_account_email`: Adres e-mail konta serwisowego.
  * `labels`: Etykiety.
- **Outputs**: `repository_url`, `image_path`.
- **Lokalizacja**: `infrastructure/modules/artifact-registry`

### secrets
- **Przeznaczenie**: Przechowywanie i zarządzanie sekretami (np. token Hugging Face) w Secret Manager.
- **Tworzone zasoby**: Sekret (Secret), Wersja sekretu (Secret Version), IAM policies.
- **Główne parametry**:
 * `project_id`: ID projektu GCP.
 * `region`: Region.
 * `labels`: Etykiety
- **Outputs**: `secret_name`, `secret_version`.
- **Lokalizacja**: `infrastructure/modules/secrets`

### source-repo
- **Przeznaczenie**:  Zarządzanie repozytoriami kodu (obecnie dla Activator) w Cloud Source Repositories.
- **Tworzone zasoby**:  Repozytorium, uprawnienia IAM
- **Główne parametry**:
    *   `project_id`: ID projektu GCP.
    *   `project_number`: Numer projektu.
    *   `region`: Region.
    *   `repo_name`: Nazwa repozytorium.
    *   `initial_version`: Początkowa wersja.
    *   `service_account_email`: Adres email konta serwisowego.
- **Outputs**: `repository_id`, `repository_url`, `init_repo_id`.
- **Lokalizacja**: `infrastructure/modules/source-repo`

### cloud-build
- **Przeznaczenie**: Automatyzacja budowania, testowania i wdrażania aplikacji za pomocą Cloud Build.
- **Tworzone zasoby**:  Wyzwalacze (Triggers) Cloud Build, uprawnienia IAM, (opcjonalnie) repozytorium Artifact Registry.
- **Główne parametry**:
    * `project_id`: ID projektu GCP.
    * `project_number`: Numer projektu.
    * `region`: Region.
    * `repository_id`: ID repozytorium kodu źródłowego.
    * `repository_name`: Nazwa repozytorium kodu źródłowego.
    * `artifact_registry_location`:  Lokalizacja Artifact Registry.
    * `artifact_registry_repository`: Nazwa repozytorium Artifact Registry.
    * `service_account_email`: Adres email konta serwisowego.
    * `initial_version`:  Początkowa wersja.
    * `trigger_name`: Nazwa wyzwalacza.
    * `transcriber_trigger_name`: Nazwa wyzwalacza dla Transcribera.
    * `transcriber_repository_name`: Nazwa repozytorium kodu źródłowego Transcribera.
    * `branch_pattern`:  Wzorzec gałęzi.
    * `labels`: Etykiety.
- **Outputs**: `build_trigger_url`, `artifacts_bucket`.
- **Lokalizacja**: `infrastructure/modules/cloud-build`

## 4.5. Wdrażanie infrastruktury przez Terraform

1. Inicjalizacja:
   ```bash
   cd infrastructure
   tofu init
   ```
2. Konfiguracja backendu (Cloud Storage):
    - Utwórz bucket `example-project-id-terraform-state` w Cloud Storage (jeśli jeszcze nie istnieje).
    - Odkomentuj sekcję `backend "gcs"` w pliku `infrastructure/provider.tf` i uzupełnij nazwę bucketa:
      ```terraform
      terraform {
        backend "gcs" {
          bucket = "example-project-id-terraform-state"
          prefix = "sonus/activator"
        }
      }
      ```
    - Ponownie uruchom `tofu init`, aby skonfigurować backend.

3. Planowanie zmian:
   ```bash
   tofu plan -out=plan.tfplan
   ```

4. Weryfikacja planu:
   - Sprawdzenie zasobów do utworzenia/modyfikacji/usunięcia
   - Analiza kosztów i limitów
   - Potwierdzenie konfiguracji

5. Wdrożenie:
   ```bash
   tofu apply plan.tfplan
   ```

6. Weryfikacja:
   ```bash
   # Sprawdzenie statusu zasobów
   tofu show

   # Sprawdzenie outputów
   tofu output
   ```
   **Uwaga:** Użyj `tofu output` aby zobaczyć zdefiniowane wartości wyjściowe (np. adresy URL, nazwy zasobów).

# 5. Konfiguracja Service Account

1. Utworzenie Service Account:
   - Nazwa: sonus-transcription-sa
   - Display name: Sonus Transcription Service Account

2. Nadanie wymaganych uprawnień:
- roles/run.invoker - do uruchamiania zadań Cloud Run
- roles/run.developer - do aktualizacji Cloud Run jobs
- roles/iam.serviceAccountUser - do używania service accounts
- roles/storage.objectViewer - do odczytu plików z Cloud Storage
- roles/storage.objectCreator - do zapisu plików w Cloud Storage
- roles/pubsub.publisher - do publikowania wiadomości w Pub/Sub
- roles/pubsub.subscriber - do subskrybowania wiadomości w Pub/Sub
- roles/source.reader - do odczytu z Cloud Source Repositories
- roles/artifactregistry.reader - do pobierania obrazów z Artifact Registry
- roles/logging.logWriter - do zapisywania logów
- roles/monitoring.metricWriter - do zapisywania metryk
- roles/cloudtrace.agent - do zapisywania śladów
- roles/viewer - dla dostępu do zasobów projektu
- roles/secretmanager.secretAccessor - do odczytu sekretów (token HF)

# 6. Konfiguracja Secret Manager

1. Utworzenie sekretu dla tokena Hugging Face:
   - Nazwa sekretu: hf-token
   - Projekt: example-project-id
   - Region replikacji: REGION
   - Typ replikacji: user-managed
   - Etykiety: env=prod, domain=ai, app=sonus

2. Nadanie uprawnień dostępu:
   - Rola: roles/secretmanager.secretAccessor
   - Service Account: sonus-transcription-sa@example-project-id.iam.gserviceaccount.com

Uwagi:
- Secret Manager automatycznie wersjonuje sekrety
- Każda zmiana wartości sekretu tworzy nową wersję
- Service Account ma dostęp do najnowszej wersji sekretu (latest)
- Stare wersje są zachowywane dla celów audytu

# 7. Konfiguracja Artifact Registry i Storage

1. Konfiguracja Artifact Registry:
   - Włączenie API: artifactregistry.googleapis.com
   - Utworzenie repozytorium Docker:
     * Nazwa: sonus
     * Projekt: example-project-id
     * Region: REGION
     * Format: DOCKER
     * Etykiety: env=prod, domain=ai, app=sonus
   - Uprawnienia:
     * Service Account: roles/artifactregistry.writer
     * Cloud Build: roles/artifactregistry.writer
   - Konfiguracja Docker auth dla ${region}-docker.pkg.dev

2. Konfiguracja Cloud Storage:
   - Build logs bucket:
     * Nazwa: sonus-build-logs
     * Region: REGION
     * Uniform access: true
     * Force destroy: true
     * Etykiety: env=prod, domain=ai, app=sonus
   - Test reports bucket:
     * Nazwa: sonus-test-reports
     * Region: REGION
     * Uniform access: true
     * Force destroy: true
     * Etykiety: env=prod, domain=ai, app=sonus
   - WhisperX models bucket:
     * Nazwa: sonus-whisperx-models
     * Region: REGION
     * Uniform access: true
     * Force destroy: true
     * Etykiety: env=prod, domain=ai, app=sonus

3. Konfiguracja uprawnień dla Cloud Build:
   - Build logs bucket:
     * roles/storage.objectViewer
     * roles/storage.objectCreator
   - Test reports bucket:
     * roles/storage.objectViewer
     * roles/storage.objectCreator

4. Konfiguracja uprawnień dla Sonus Service Account:
   - WhisperX models bucket:
     * roles/storage.objectViewer
     * roles/storage.objectCreator
     * roles/storage.legacyBucketWriter

5. Konfiguracja wolumenów dla Cloud Run:
   - Pamięć tymczasowa (/tmp/sonus/work):
     * Typ: emptyDir (MEMORY)
     * Rozmiar: 1Gi
     * Cel: Tymczasowe przechowywanie plików
   - GCS (/models):
     * Bucket: sonus-whisperx-models
     * Tryb: read-write
     * Cel: Przechowywanie modeli WhisperX

Uwagi:
- Wszystkie buckety mają włączoną uniform bucket-level access
- Cloud Build SA ma uprawnienia do odczytu i zapisu logów i raportów
- Sonus SA ma dodatkowe uprawnienia legacy bucket writer dla modeli WhisperX

# 8. Konfiguracja Pub/Sub

System wykorzystuje dwie kolejki Pub/Sub:

## 8.1. Produkcyjna kolejka
- **Topic**: sonus-pubsub-topic
- **Subscription**: sonus-transcriber-sub
- **Labels**: env=prod, domain=ai, app=sonus, component=pubsub
- **Konfiguracja**:
  * ack_deadline_seconds = 600 (10 minut)
  * retain_acked_messages = true
  * message_retention_duration = "604800s" (7 dni)
  * enable_message_ordering = false
  * expiration_policy = never (subskrypcja nigdy nie wygasa)

## 8.2. Testowa kolejka
- **Topic**: sonus-pubsub-topic-test
- **Subscription**: sonus-transcriber-sub-test
- **Labels**: env=test, domain=ai, app=sonus, component=pubsub
- **Konfiguracja**:
  * ack_deadline_seconds = 600 (10 minut)
  * retain_acked_messages = true
  * message_retention_duration = "3600s" (1 godzina)
  * enable_message_ordering = false
  * expiration_policy = never (subskrypcja nigdy nie wygasa)

## 8.3. Konfiguracja środowisk testowych

System wykorzystuje dedykowane kolejki Pub/Sub dla różnych środowisk:

1. Środowisko testowe (domyślne):
   ```bash
   # Utworzenie kolejek testowych
   gcloud pubsub topics create sonus-pubsub-topic-test
   gcloud pubsub subscriptions create sonus-transcriber-sub-test \
     --topic sonus-pubsub-topic-test
   
   # Uruchomienie z domyślną konfiguracją
   python -m src.transcriber.main
   ```

2. Środowisko produkcyjne:
   ```bash
   # Utworzenie kolejek produkcyjnych
   gcloud pubsub topics create sonus-pubsub-topic
   gcloud pubsub subscriptions create sonus-transcriber-sub \
     --topic sonus-pubsub-topic
   
   # Uruchomienie z konfiguracją produkcyjną
   PUBSUB_CONFIG="sonus-pubsub-topic|sonus-transcriber-sub" \
   python -m src.transcriber.main
   ```

3. Własne środowisko testowe:
   ```bash
   # Utworzenie własnych kolejek
   gcloud pubsub topics create my-test-topic
   gcloud pubsub subscriptions create my-test-sub \
     --topic my-test-topic
   
   # Uruchomienie z własną konfiguracją
   PUBSUB_CONFIG="my-test-topic|my-test-sub" \
   python -m src.transcriber.main
   ```

Korzyści z separacji środowisk:
- Izolacja testów od produkcji
- Możliwość równoległego testowania zmian
- Elastyczna konfiguracja dla różnych przypadków testowych

## 8.4. Główne różnice między kolejkami
1. Retencja wiadomości:
   - Produkcyjna: 7 dni (dla możliwości analizy historycznej)
   - Testowa: 1 godzina (dla szybkiego czyszczenia testowych danych)
2. Etykiety środowiska:
   - Produkcyjna: env=prod
   - Testowa: env=test

## 8.5. Format wiadomości
```json
{
  "file_id": "MOCK_DRIVE_ID",
  "file_name": "example_video_file.mp4",
  "file_path": "drive://MOCK_DRIVE_ID",
  "shared_by": "user.name@example.com",
  "timestamp": "2025-02-21T14:58:49.217286Z",
  "operation": "konwersja"
}
```

Opis pól:
- **file_id**: Unikalny identyfikator pliku w Google Drive
- **file_name**: Nazwa pliku z rozszerzeniem
- **file_path**: Ścieżka dostępu do pliku w formacie drive://[file_id]
- **shared_by**: Adres email właściciela pliku
- **timestamp**: Znacznik czasu w formacie ISO 8601 z precyzją do mikrosekund
- **operation**: Typ operacji (zawsze "konwersja")

# 9. Konfiguracja CI/CD (Cloud Build)

Cloud Build wymaga następującej konfiguracji:

## 9.1. Kroki budowania
1. Instalacja zależności Python:
   - Użycie obrazu python:3.11
   - Instalacja pakietów z requirements.txt i requirements-test.txt
   - Instalacja w trybie developerskim

2. Budowanie obrazu Docker:
   - Tagowanie trzema wersjami:
     * ${SHORT_SHA} (hash commita)
     * ${_VERSION} (numer wersji)
     * latest
   - Budowanie z kontekstu lokalnego

3. Publikowanie obrazu:
   - Push wszystkich trzech tagów do rejestru

## 9.2. Zmienne podstawienia
- _REGION: REGION
- _VERSION: 0.0.11
- _REGISTRY: REGION-docker.pkg.dev/example-project-id/sonus

## 9.3. Konfiguracja triggerów
1. Trigger dla Activator:
   - Nazwa: activator-build
   - Repozytorium: sonus-activator
   - Branch pattern: ^master$
   - Event: Push tag

2. Trigger dla Transcriber:
   - Nazwa: transcriber-build
   - Repozytorium: sonus-transcriber
   - Branch pattern: ^master$
   - Event: Push tag

## 9.4. Monitorowanie buildów
```bash
# Sprawdzenie historii buildów
gcloud builds list --project=$PROJECT_ID --region=REGION --limit=5

# Sprawdzenie aktualnie działających buildów
gcloud builds list --project=$PROJECT_ID --region=REGION --ongoing

# Szczegóły konkretnego builda
gcloud builds describe BUILD_ID --project=$PROJECT_ID --region=REGION

# Sprawdzenie logów builda
gcloud builds log BUILD_ID --project=$PROJECT_ID --region=REGION
```

## 9.5. Strategia wersjonowania i wdrażania

### 9.5.1. Semantic Versioning
System używa Semantic Versioning (semver) w formacie MAJOR.MINOR.PATCH:
- **MAJOR**: Niekompatybilne zmiany API (np. zmiana formatu wiadomości Pub/Sub)
- **MINOR**: Nowe funkcjonalności zachowujące kompatybilność wsteczną
- **PATCH**: Poprawki błędów zachowujące kompatybilność wsteczną

Przykłady:
- v1.0.0 - Pierwsza wersja produkcyjna
- v1.1.0 - Dodanie nowego formatu audio
- v1.1.1 - Poprawka błędu w obsłudze plików

### 9.5.2. Strategia branchowania
System wykorzystuje trunk-based development:
- **master**: Główna gałąź zawierająca kod produkcyjny
- **feature/xxx**: Krótko żyjące gałęzie dla nowych funkcjonalności
- **hotfix/xxx**: Gałęzie dla pilnych poprawek produkcyjnych

Zasady:
1. Wszystkie zmiany przez pull requesty
2. Code review wymagane dla każdego PR
3. Testy muszą przejść przed mergem
4. Automatyczny deploy po merge do master

### 9.5.3. CI/CD Pipeline

#### Etapy Pipeline'u

1. **Weryfikacja kodu (Code Verification)**:
   - **Linting i formatowanie**:
     * black - formatowanie kodu
     * flake8 - sprawdzanie zgodności z PEP8
     * isort - sortowanie importów
     * mypy - statyczna analiza typów
   - **Testy jednostkowe**:
     * pytest - uruchomienie testów
     * coverage - raport pokrycia kodu
     * doctest - testy w docstringach
   - **Kryteria akceptacji**:
     * Pokrycie kodu >80%
     * Brak błędów lintera
     * Wszystkie testy przechodzą

2. **Budowanie (Build)**:
   - **Przygotowanie**:
     * Weryfikacja zależności
     * Aktualizacja requirements.txt
     * Sprawdzenie kompatybilności
   - **Budowa kontenera**:
     * Optymalizacja Dockerfile
     * Wieloetapowe budowanie
     * Skanowanie bezpieczeństwa
   - **Artefakty**:
     * Publikacja obrazu Docker
     * Generowanie dokumentacji
     * Archiwizacja raportów

3. **Testy (Testing)**:
   - **Testy automatyczne**:
     * Testy integracyjne
     * Testy end-to-end
     * Testy wydajnościowe
   - **Testy bezpieczeństwa**:
     * Skanowanie podatności
     * Testy penetracyjne
     * Audyt uprawnień
   - **Testy środowiskowe**:
     * Weryfikacja konfiguracji
     * Testy infrastruktury
     * Testy odtwarzania

4. **Wdrożenie (Deployment)**:
   - **Przygotowanie**:
     * Weryfikacja zasobów
     * Backup konfiguracji
     * Plan rollback
   - **Wdrożenie**:
     * Stopniowe (rolling update)
     * Canary deployment
     * Blue-green deployment
   - **Weryfikacja**:
     * Testy smoke
     * Monitoring metryk
     * Alerty i powiadomienia

#### Środowiska i przepływ pracy

1. **Development**:
   - **Triggery**:
     * Każdy commit do feature branch
     * Pull request do develop
   - **Zakres testów**:
     * Testy jednostkowe
     * Podstawowe testy integracyjne
   - **Wdrożenie**:
     * Automatyczne po testach
     * Tag: dev-${SHORT_SHA}
     * Środowisko: dev

2. **Staging**:
   - **Triggery**:
     * Merge do develop
     * Scheduled builds
   - **Zakres testów**:
     * Pełen zestaw testów
     * Testy wydajnościowe
     * Testy bezpieczeństwa
   - **Wdrożenie**:
     * Po zatwierdzeniu QA
     * Tag: staging-${SHORT_SHA}
     * Środowisko: staging

3. **Production**:
   - **Triggery**:
     * Release tag (v*.*.*)
     * Hotfix tag
   - **Zakres testów**:
     * Testy regresji
     * Testy obciążeniowe
     * Weryfikacja backupów
   - **Wdrożenie**:
     * W oknie wdrożeniowym
     * Tag: prod-${VERSION}
     * Środowisko: prod

#### Proces zatwierdzania i kontroli jakości

1. **Code Review**:
   - **Wymagania**:
     * Min. 2 zatwierdzenia
     * Brak blokerów w SonarQube
     * Aktualna dokumentacja
   - **Weryfikacja**:
     * Zgodność z konwencjami
     * Pokrycie testami
     * Wydajność kodu
   - **Narzędzia**:
     * GitHub Pull Requests
     * SonarQube
     * Code Climate

2. **Quality Gates**:
   - **Metryki kodu**:
     * Złożoność cyklomatyczna <15
     * Długość metod <50 linii
     * Duplikacje kodu <3%
   - **Pokrycie testami**:
     * Całość: >80%
     * Nowy kod: >90%
     * Krytyczne ścieżki: 100%
   - **Wydajność**:
     * Czas odpowiedzi <500ms
     * Użycie pamięci <85%
     * Błędy <0.1%

3. **Release Management**:
   - **Zatwierdzenia**:
     * Release Manager
     * Tech Lead
     * Product Owner
   - **Dokumentacja**:
     * Release notes
     * Changelog
     * Instrukcje rollback
   - **Harmonogram**:
     * Planowane: wt/czw
     * Hotfixy: 24/7
     * Okna serwisowe

#### Monitorowanie i feedback

1. **Monitoring wdrożenia**:
   - **Metryki aplikacji**:
     * Dostępność
     * Czas odpowiedzi
     * Błędy
   - **Metryki infrastruktury**:
     * Użycie zasobów
     * Skalowanie
     * Koszty
   - **Alerty**:
     * Slack
     * Email
     * PagerDuty

2. **Analiza post-deployment**:
   - **Metryki**:
     * Czas wdrożenia
     * Skuteczność testów
     * Liczba rollbacków
   - **Feedback**:
     * Retrospektywa
     * Lessons learned
     * Usprawnienia
   - **Dokumentacja**:
     * Aktualizacja procedur
     * Best practices
     * Znane problemy

3. **Continuous Improvement**:
   - **Optymalizacja**:
     * Pipeline'u
     * Testów
     * Infrastruktury
   - **Automatyzacja**:
     * Powtarzalnych zadań
     * Raportowania
     * Monitoringu
   - **Szkolenia**:
     * Nowe narzędzia
     * Best practices
     * Procedury

#### Automatyczne testy smoke

1. **Zakres testów**:
   - Weryfikacja dostępności usług
   - Podstawowy flow (upload -> transkrypcja)
   - Sprawdzenie logów i metryk
   - Weryfikacja integracji z zewnętrznymi systemami

2. **Kryteria sukcesu**:
   - Wszystkie endpointy odpowiadają
   - Transkrypcja testowego pliku działa
   - Brak błędów w logach
   - Metryki w normie

3. **Automatyczne rollback**:
   - Wyzwalany przy niepowodzeniu testów smoke
   - Powrót do poprzedniej stabilnej wersji
   - Notyfikacja zespołu
   - Zachowanie logów dla analizy

4. **Monitoring po wdrożeniu**:
   - 15 minut intensywnego monitoringu
   - Weryfikacja metryk biznesowych
   - Sprawdzanie wskaźników SLO
   - Alert przy anomaliach

#### Konfiguracja środowisk

1. **Development**:
   ```yaml
   env_vars:
     DEBUG: "true"
     PUBSUB_CONFIG: "sonus-pubsub-topic-test|sonus-transcriber-sub-test"
     GPU: "false"
     HF_TOKEN: "hf_dummy"
   resources:
     cpu: "2"
     memory: "4Gi"
   monitoring:
     log_level: "DEBUG"
     metrics_interval: "10s"
   tests:
     skip_performance: true
     mock_external_services: true
   ```

2. **Staging**:
   ```yaml
   env_vars:
     DEBUG: "false"
     PUBSUB_CONFIG: "sonus-pubsub-topic-staging|sonus-transcriber-sub-staging"
     GPU: "false"
     HF_TOKEN: "hf_staging"
   resources:
     cpu: "4"
     memory: "8Gi"
   monitoring:
     log_level: "INFO"
     metrics_interval: "30s"
   tests:
     performance_threshold: "90%"
     include_e2e: true
   ```

3. **Production**:
   ```yaml
   env_vars:
     DEBUG: "false"
     PUBSUB_CONFIG: "sonus-pubsub-topic|sonus-transcriber-sub"
     GPU: "false"
     HF_TOKEN: "hf_prod"
   resources:
     cpu: "4"
     memory: "8Gi"
   monitoring:
     log_level: "WARNING"
     metrics_interval: "60s"
   alerts:
     error_threshold: "1%"
     latency_threshold: "5s"
   backup:
     enabled: true
     retention: "30d"
   ```

## 9.6. Początkowe wdrożenie (bootstrap) systemu

**Uwaga:** Większość kroków wdrożenia jest obsługiwana przez Terraform (sekcja 4.5). Poniższe kroki dotyczą głównie początkowej konfiguracji i ręcznych działań, które nie są objęte automatyzacją.

### 9.6.1. Przygotowanie środowiska i wdrożenie

1.  **Konfiguracja dostępu do GCP:**
    ```bash
    # Konfiguracja projektu
    gcloud config set project example-project-id

    # Konfiguracja regionu
    gcloud config set compute/region REGION

    # Uwierzytelnianie
    gcloud auth application-default login
    ```

2.  **Weryfikacja uprawnień:**
    ```bash
    # Sprawdzenie uprawnień
    gcloud projects get-iam-policy example-project-id \
      --flatten="bindings[].members" \
      --format='table(bindings.role,bindings.members)'
    ```

3.  **Włączenie wymaganych API:**
    ```bash
    # Włączenie API
    gcloud services enable \
      run.googleapis.com \
      pubsub.googleapis.com \
      cloudscheduler.googleapis.com \
      drive.googleapis.com \
      artifactregistry.googleapis.com \
      cloudresourcemanager.googleapis.com
    ```
4. **Wgraj modele WhisperX:**
    *   Pobierz modele WhisperX (szczegóły znajdziesz w dokumentacji WhisperX).
    *   Wgraj modele do bucketa `sonus-whisperx-models` w Cloud Storage:
        ```bash
        gsutil -m cp -r /path/to/whisperx/models gs://sonus-whisperx-models/
        ```
        Zastąp `/path/to/whisperx/models` ścieżką do katalogu z modelami na twoim lokalnym komputerze.

5.  **Wdróż infrastrukturę za pomocą Terraform:**
      Wykonaj kroki opisane w sekcji 4.5.

### 9.6.2. Weryfikacja i monitorowanie (po wdrożeniu)
Poniższe komendy służą do monitorowania i ręcznego zarządzania systemem po jego wdrożeniu.

1.  **Sprawdzenie statusu:**
    ```bash
    # Status Cloud Run Jobs
    gcloud run jobs list --region REGION

    # Status Pub/Sub
    gcloud pubsub topics list
    gcloud pubsub subscriptions list
    ```

2.  **Testy smoke (ręczne uruchomienie):**
    ```bash
    # Test Activator Job
    gcloud run jobs execute activator --region REGION

    # Test Pub/Sub (wysłanie testowej wiadomości)
    gcloud pubsub topics publish sonus-pubsub-topic-test \
      --message "test message"
    ```

3.  **Monitoring:**
    ```bash
    # Sprawdzenie logów
    gcloud logging read "resource.type=cloud_run_job" \
      --project example-project-id --format="json"
    ```
# 10. Budowa kontenera "Activator"

## 10.1. Konfiguracja kontenera
- **Obraz bazowy**: python:3.11-slim
- **Katalog roboczy**: /app
- **Instalacja zależności**: 
  - Kopiowanie requirements.txt
  - Instalacja pakietów przez pip
- **Kopiowanie kodu**: Cały kod źródłowy do kontenera
- **Instalacja aplikacji**: W trybie developerskim (-e)
- **Komenda startowa**: python -m activator.main

## 10.2. Struktura projektu
```bash
sonus-activator/
├── src/
│   └── activator/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── Dockerfile
├── requirements.txt
├── requirements-test.txt
└── setup.py
```

## 10.3. Budowanie lokalne
```bash
# Z katalogu sonus-activator
docker build -t sonus-activator:dev .

# Uruchomienie lokalne
docker run --rm \
  -e PROJECT_ID=example-project-id \
  -e DEBUG=true \
  sonus-activator:dev
```

# 11. Budowa kontenera "Transcriber"

## 11.1. Konfiguracja kontenera
- **Obraz bazowy**: python:3.11-slim
- **Katalog roboczy**: /app
- **Instalacja zależności**: 
  - Kopiowanie requirements.txt i requirements-test.txt
  - Instalacja pakietów przez pip
  - Instalacja WhisperX i zależności
- **Wolumeny**:
  - /tmp/sonus/work: Tymczasowe pliki
  - /models: Modele WhisperX
- **Instalacja aplikacji**: W trybie developerskim (-e)
- **Komenda startowa**: python -m src.transcriber.main

## 11.2. Struktura projektu
```bash
sonus-transcriber/
├── src/
│   └── transcriber/
│       ├── __init__.py
│       ├── config.py
│       ├── debug_transcribe.py
│       ├── drive_client.py
│       ├── logger.py
│       ├── main.py
│       ├── whisperx_transcriber.py
│       └── storage/
│           ├── __init__.py
│           ├── base_client.py
│           ├── client_factory.py
│           ├── drive_client.py
│           └── local_client.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_*.py
│   └── files/
│       └── sample_audio_2_persons_15s.mp3
├── Dockerfile
├── requirements.txt
├── requirements-test.txt
├── setup.py
├── CHANGELOG.md
└── UNIT_TEST.md
```

## 11.3. Budowanie lokalne
```bash
# Z katalogu sonus-transcriber
docker build -t sonus-transcriber:dev .

# Uruchomienie lokalne
docker run --rm \
  -e PROJECT_ID=example-project-id \
  -e DEBUG=true \
  -e GPU=false \
  -e MODELS_DIR=/models \
  -e WORK_DIR=/tmp/sonus/work \
  -e HF_TOKEN=hf_dummy \
  -v /tmp/sonus/models:/models \
  sonus-transcriber:dev
```

## 11.4. Zmienne środowiskowe
- PROJECT_ID: ID projektu GCP
- DEBUG: Tryb debug (true/false)
- GPU: Czy używać GPU (false)
- LANGUAGE: Język transkrypcji (pl)
- HF_TOKEN: Token Hugging Face
- MODELS_DIR: Katalog na modele (/models)
- WORK_DIR: Katalog roboczy (/tmp/sonus/work)
- PUBSUB_CONFIG: Konfiguracja Pub/Sub (domyślnie: "sonus-pubsub-topic-test|sonus-transcriber-sub-test")

# 12. Konfiguracja Cloud Run Jobs

## 12.1. Wspólne parametry
- **Parallelism**: Maksymalnie 4 równoległe zadania
- **Time Zone**: Europe/Warsaw
- **Attempt Deadline**: 320s (5 minut i 20 sekund)
- **Labels**: env, domain, app (dla śledzenia kosztów)

## 12.2. Activator Job
- **Nazwa**: activator
- **Region**: REGION
- **Limity zasobów**:
  - CPU: 1000m (1 rdzeń)
  - Pamięć: 512Mi
- **Konfiguracja wykonania**:
  - Timeout: 3600s (1 godzina)
  - Max retries: 3
  - Harmonogram: "11 * * * *" (co godzinę o 11 minucie)
- **Zmienne środowiskowe**:
  - PROJECT_ID: ID projektu GCP
  - AUDIO_EXTENSIONS: obsługiwane rozszerzenia plików audio
  - VIDEO_EXTENSIONS: obsługiwane rozszerzenia plików wideo
  - DEBUG: tryb debug (true/false)
- **Service Account**: sonus-transcription-sa@example-project-id.iam.gserviceaccount.com
- **Obraz kontenera**: REGION-docker.pkg.dev/example-project-id/sonus/activator:latest

## 12.3. Transcriber Job
- **Nazwa**: transcriber
- **Region**: REGION
- **Limity zasobów**:
  - CPU: 4000m (4 rdzenie)
  - Pamięć: 8Gi
- **Konfiguracja wykonania**:
  - Timeout: 21600s (6 godzin)
  - Max retries: 0 (obsługiwane przez Activator)
  - Harmonogram: "*/30 * * * *" (co 30 minut)
- **Zmienne środowiskowe**:
  - PROJECT_ID: ID projektu GCP
  - AUDIO_EXTENSIONS: obsługiwane rozszerzenia plików audio
  - VIDEO_EXTENSIONS: obsługiwane rozszerzenia plików wideo
  - DEBUG: tryb debug (true/false)
  - GPU: czy używać GPU (false)
  - LANGUAGE: język transkrypcji (pl)
  - HF_TOKEN: token Hugging Face (z Secret Manager)
  - MODELS_DIR: katalog na modele (/models)
  - WORK_DIR: katalog roboczy (/tmp/sonus/work)
  - PUBSUB_CONFIG: konfiguracja Pub/Sub
- **Service Account**: sonus-transcription-sa@example-project-id.iam.gserviceaccount.com
- **Obraz kontenera**: REGION-docker.pkg.dev/example-project-id/sonus/transcriber:latest

## 12.4. Obsługa błędów
Job implementuje następującą strategię obsługi błędów:
- Błędy są logowane na stderr z odpowiednim poziomem severity
- Job kończy się kodem błędu (exit code 1) w przypadku niepowodzenia
- Wiadomości nie są potwierdzane (no acknowledgment) w przypadku błędów
- Brak automatycznych ponowień - ponowne próby są obsługiwane przez Activator

# 13. Konfiguracja Cloud Scheduler

## 13.1. Parametry podstawowe
- **Nazwa**: activator-schedule
- **Opis**: "Triggers activator job every hour"
- **Harmonogram**: "11 * * * *" (co godzinę o 11 minucie)
- **Strefa czasowa**: Europe/Warsaw
- **Deadline**: 320 sekund
- **Region**: REGION

## 13.2. Konfiguracja HTTP
- **Metoda**: POST
- **URI**: https://REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/example-project-id/jobs/activator:run
- **Autentykacja**: OAuth token z Service Account

## 13.3. Monitorowanie
```bash
# Sprawdzenie statusu zadań
gcloud scheduler jobs list --location=REGION

# Sprawdzenie historii wykonań
gcloud scheduler jobs list-executions activator-schedule \
  --location=REGION

# Ręczne uruchomienie zadania
gcloud scheduler jobs run activator-schedule \
  --location=REGION
```

# 14. Testowanie i uruchamianie lokalne

## 14.1. Strategia testowania

### 14.1.1. Poziomy testów i kryteria akceptacji

1. **Testy jednostkowe**:
   - **Uruchamianie**: Przy każdym commit
   - **Pokrycie kodu**: 
     * Minimum: >80% całości
     * Cel: >90% logiki biznesowej
     * Krytyczne komponenty: >95%
   - **Czas wykonania**: 
     * Całość: <5 minut
     * Pojedynczy test: <1 sekunda
   - **Izolacja**: 
     * Brak zależności zewnętrznych
     * Wszystkie zewnętrzne usługi zmockowane
     * Brak dostępu do sieci
   - **Asercje**:
     * Weryfikacja poprawności wyników
     * Sprawdzanie obsługi błędów
     * Testy brzegowych przypadków

2. **Testy integracyjne**:
   - **Uruchamianie**: 
     * Przy PR do master
     * Przed każdym release
   - **Zakres**:
     * Integracja między komponentami
     * Komunikacja z Pub/Sub
     * Operacje na plikach
     * Interakcje z Google Drive
   - **Środowisko**:
     * Testowe kolejki Pub/Sub
     * Izolowane buckety Storage
     * Dedykowane konta serwisowe
   - **Czas wykonania**: 
     * Całość: <15 minut
     * Pojedynczy test: <30 sekund
   - **Metryki**:
     * Sukces: >95% testów
     * Błędy integracji: <1%

3. **Testy end-to-end**:
   - **Uruchamianie**:
     * Przed wdrożeniem na produkcję
     * Po większych zmianach
   - **Scenariusze**:
     * Pełny flow z Google Drive
     * Różne formaty plików audio/video
     * Obsługa błędów i retry
     * Monitoring i alerty
   - **Dane testowe**:
     * Krótkie pliki (<1 min)
     * Średnie pliki (1-5 min)
     * Długie pliki (>5 min)
     * Pliki z różnymi językami
   - **Czas wykonania**: 
     * Całość: <30 minut
     * Pojedynczy scenariusz: <5 minut
   - **Kryteria sukcesu**:
     * Wszystkie scenariusze zaliczone
     * Brak błędów krytycznych
     * Metryki w normie

4. **Testy wydajnościowe**:
   - **Uruchamianie**:
     * Ręcznie w dedykowanym środowisku
     * Przed zmianami wpływającymi na wydajność
   - **Zasoby**:
     * CPU: 8 rdzeni
     * RAM: 16GB
     * Dysk: 100GB SSD
   - **Scenariusze**:
     * Obciążenie stałe (1 req/s, 1h)
     * Obciążenie skokowe (10 req/s, 5min)
     * Długie pliki (>30min audio)
     * Równoległe przetwarzanie
   - **Metryki**:
     * Czas przetwarzania: <5x długość pliku
     * Użycie CPU: <80%
     * Użycie RAM: <85%
     * Błędy: <1%
   - **Raportowanie**:
     * Szczegółowe metryki wydajności
     * Wykresy użycia zasobów
     * Analiza wąskich gardeł
     * Rekomendacje optymalizacji

### 14.1.2. Środowiska testowe

1. **Lokalne**:
   - Dla deweloperów
   - Mocki zewnętrznych usług
   - Szybki feedback
   - Używa .env.test

2. **CI/CD**:
   - Izolowane środowisko w Cloud Build
   - Testowe instancje usług
   - Automatyczne testy
   - Raportowanie wyników

3. **Wydajnościowe**:
   - Dedykowane środowisko
   - Duże zasoby obliczeniowe
   - Monitoring metryk
   - Długie czasy wykonania

### 14.1.3. Organizacja testów

#### Struktura katalogów
```
tests/
├── unit/                     # Testy jednostkowe
│   ├── storage/             # Testy komponentów storage
│   │   ├── test_drive.py    # Testy Google Drive
│   │   └── test_local.py    # Testy lokalnego storage
│   ├── pubsub/              # Testy Pub/Sub
│   │   ├── test_publish.py  # Testy publikowania
│   │   └── test_receive.py  # Testy odbierania
│   └── transcribe/          # Testy transkrypcji
│       ├── test_whisperx.py # Testy modelu WhisperX
│       └── test_diarize.py  # Testy diaryzacji
├── integration/             # Testy integracyjne
│   ├── test_e2e.py         # Testy end-to-end
│   └── test_components.py   # Testy między komponentami
├── performance/            # Testy wydajnościowe
│   ├── test_load.py        # Testy obciążeniowe
│   └── test_stress.py      # Testy stresowe
└── data/                   # Dane testowe
    ├── audio/              # Pliki audio
    │   ├── short/         # 15-30s
    │   ├── medium/        # 2-5min
    │   └── long/          # >30min
    ├── video/             # Pliki wideo
    │   ├── short/         # Krótkie
    │   └── medium/        # Średnie
    └── problematic/       # Problematyczne przypadki
        ├── polish_chars/  # Polskie znaki
        ├── long_names/    # Długie nazwy
        └── unsupported/   # Nieobsługiwane formaty
```

### 14.1.4. Fixtures i pomocnicze narzędzia
```python
# conftest.py
@pytest.fixture
def mock_drive_client():
    """Mock klienta Google Drive dla testów"""
    return MockDriveClient()

@pytest.fixture
def mock_pubsub():
    """Mock Pub/Sub dla testów"""
    return MockPubSub()

@pytest.fixture
def test_audio_file():
    """Przykładowy plik audio dla testów"""
    return "tests/files/sample_audio_2_persons_15s.mp3"
```

### 14.1.5. Konwencje nazewnicze
- test_*.py - pliki testowe
- Test* - klasy testowe
- test_* - funkcje testowe
- *_test - pliki pomocnicze
- mock_* - mocki i stuby

## 14.2. Uruchamianie testów jednostkowych

### 14.2.1. Testy lokalne i z GCP

#### Test lokalny z przykładowym plikiem
```bash
cd sonus-transcriber && \
mkdir -p /tmp/sonus/models && \
PUBSUB_CONFIG="sonus-pubsub-topic-test|sonus-transcriber-sub-test" \
DEBUG=true \
GPU=false \
PROJECT_ID=example-project-id \
MODELS_DIR=/tmp/sonus/models \
TRANSCRIPTIONS_DIR=/tmp/sonus/transcriptions \
HF_TOKEN=hf_dummy \
python -m src.transcriber.main --pubsub-message-config drive_test_30s
```

#### Test z kolejką testową GCP
```bash
cd sonus-transcriber && \
PUBSUB_CONFIG="sonus-pubsub-topic-test|sonus-transcriber-sub-test" \
DEBUG=true \
GPU=false \
PROJECT_ID=example-project-id \
MODELS_DIR=/tmp/sonus/models \
TRANSCRIPTIONS_DIR=/tmp/sonus/transcriptions \
HF_TOKEN=hf_dummy \
python -m src.transcriber.main
```

### 14.2.2. Konkretny test z parametrami
```bash
cd sonus-transcriber && \
mkdir -p /tmp/sonus/models && \
PUBSUB_CONFIG="sonus-pubsub-topic-test|sonus-transcriber-sub-test" \
DEBUG=true \
GPU=false \
PROJECT_ID=example-project-id \
MODELS_DIR=/tmp/sonus/models \
WORK_DIR=/tmp/sonus/transcriptions \
HF_TOKEN=hf_dummy \
python -m pytest "tests/test_drive_storage.py::test_drive_transcription_with_unsupported_file[.pdf-drive_test_30s]" -v
```

Format parametrów testu: `[extension-config_name]`, np:
- `.pdf-drive_test_30s` - test z rozszerzeniem .pdf dla konfiguracji drive_test_30s
- `.jpg-drive_test_30s` - test z rozszerzeniem .jpg dla konfiguracji drive_test_30s

## 14.3. Uruchamianie main.py

### 14.3.1. Konfiguracja testowa
```bash
cd sonus-transcriber && \
mkdir -p /tmp/sonus/models && \
PUBSUB_CONFIG="sonus-pubsub-topic-test|sonus-transcriber-sub-test" \
DEBUG=true \
GPU=false \
PROJECT_ID=example-project-id \
MODELS_DIR=/tmp/sonus/models \
TRANSCRIPTIONS_DIR=/tmp/sonus/transcriptions \
HF_TOKEN=hf_dummy \
python -m src.transcriber.main --pubsub-message-config drive_test_30s
```

Ta komenda:
- Używa testowej kolejki Pub/Sub
- Włącza tryb debug dla szczegółowego logowania
- Wyłącza GPU
- Ustawia katalogi dla modeli i transkrypcji
- Używa testowego tokena HF
- Uruchamia program z konfiguracją drive_test_30s

### 14.3.2. Konfiguracja produkcyjna
```bash
cd sonus-transcriber && \
PUBSUB_CONFIG="sonus-pubsub-topic|sonus-transcriber-sub" \
DEBUG=false \
GPU=false \
PROJECT_ID=example-project-id \
MODELS_DIR=/models \
TRANSCRIPTIONS_DIR=/transcriptions \
HF_TOKEN="$HF_TOKEN" \
python -m src.transcriber.main
```

## 14.4. Test obsługi formatów plików

### 14.4.1. Uruchomienie testów formatów
```bash
# Z katalogu głównego projektu
python examples/test_file_extensions.py
```

### 14.4.2. Testowane formaty
1. Formaty audio:
   - mp3, wav, m4a, flac
   - Dla każdego formatu tworzy plik .txt z transkrypcją

2. Formaty wideo:
   - mp4, mov, avi, mkv
   - Dla każdego formatu tworzy plik .txt z transkrypcją

3. Nieobsługiwane formaty:
   - pdf, doc, txt, jpg
   - Dla każdego formatu tworzy plik .err z informacją o obsługiwanych formatach

### 14.4.3. Funkcjonalności testowe
- Pub/Sub do publikowania wiadomości testowych
- Automatyczne wykrywanie formatów plików
- Obsługa błędów i tworzenie plików .err
- Logowanie szczegółowych informacji w trybie debug

### 14.4.4. Wymagane zmienne środowiskowe
- PROJECT_ID - ID projektu GCP (domyślnie: example-project-id)
- GOOGLE_APPLICATION_CREDENTIALS - ścieżka do pliku service account key

## 14.5. Testy wydajnościowe

### 14.5.1. Konfiguracja środowiska testowego
```yaml
resources:
  cpu: "8"
  memory: "16Gi"
  disk: "100Gi"
monitoring:
  interval: "1s"
  metrics:
    - cpu_usage
    - memory_usage
    - disk_io
    - network_throughput
test_data:
  audio_files:
    - size: "small"  # <2MB, <1min
    - size: "medium" # 2-10MB, 1-5min
    - size: "large"  # >10MB, >5min
  video_files:
    - size: "small"  # <50MB, <5min
    - size: "medium" # 50-200MB, 5-15min
    - size: "large"  # >200MB, >15min
```

### 14.5.2. Scenariusze testów wydajnościowych
1. **Test obciążenia (Load Test)**:
   ```python
   def test_load_processing():
       """Test przetwarzania przy stałym obciążeniu"""
       files = generate_test_files(
           count=100,
           sizes=["small", "medium", "large"],
           distribution=[0.7, 0.2, 0.1]
       )
       metrics = run_load_test(
           files=files,
           duration="1h",
           rps=1.0  # 1 request per second
       )
       assert metrics.avg_processing_time < 300  # max 5 min
       assert metrics.error_rate < 0.01          # max 1% errors
   ```

2. **Test wydajności (Performance Test)**:
   ```python
   def test_performance_limits():
       """Test limitów wydajnościowych systemu"""
       metrics = run_performance_test(
           file_size="1GB",
           memory_limit="8Gi",
           cpu_limit="4"
       )
       assert metrics.completion_time < 3600  # max 1h
       assert metrics.memory_usage < 7.5      # max 7.5GB
   ```

3. **Test skalowalności (Scalability Test)**:
   ```python
   def test_parallel_processing():
       """Test równoległego przetwarzania"""
       results = run_parallel_test(
           files_count=20,
           concurrent_jobs=4
       )
       assert results.throughput > 10  # min 10 files/hour
   ```

### 14.5.3. Progi akceptacji
```yaml
performance_thresholds:
  processing_time:
    small_audio: "max 60s"   # Pliki <2MB
    medium_audio: "max 300s" # Pliki 2-10MB
    large_audio: "max 900s"  # Pliki >10MB
    small_video: "max 300s"  # Pliki <50MB
    medium_video: "max 900s" # Pliki 50-200MB
    large_video: "max 1800s" # Pliki >200MB
  resource_usage:
    cpu_avg: "max 80%"
    memory_avg: "max 85%"
    disk_io: "max 100MB/s"
  reliability:
    error_rate: "max 1%"
    availability: "min 99.9%"
  scalability:
    max_concurrent_jobs: 4
    throughput: "min 10 files/hour"
```

## 14.6. Testy integracyjne

### 14.6.1. Integracja z Google Drive
```python
def test_drive_integration():
    """Test integracji z Google Drive"""
    # Setup
    test_file = upload_test_file(
        content="test_audio.mp3",
        mime_type="audio/mpeg"
    )
    
    # Test
    result = process_drive_file(test_file.id)
    
    # Verify
    assert result.status == "success"
    assert result.transcript
    assert result.processing_time < 300
```

### 14.6.2. Integracja z Pub/Sub
```python
def test_pubsub_flow():
    """Test przepływu przez Pub/Sub"""
    # Publish
    message_id = publish_test_message(
        topic="sonus-pubsub-topic-test",
        payload={
            "file_id": "test123",
            "operation": "transcribe"
        }
    )
    
    # Subscribe and process
    result = wait_for_processing(
        subscription="sonus-transcriber-sub-test",
        timeout=600
    )
    
    # Verify
    assert result.message_id == message_id
    assert result.status == "processed"
```

### 14.6.3. Integracja z Cloud Storage
```python
def test_storage_operations():
    """Test operacji na Cloud Storage"""
    # Upload
    blob_name = upload_test_file(
        bucket="sonus-test-reports",
        content="test_data.json"
    )
    
    # Process
    result = process_storage_file(blob_name)
    
    # Verify
    assert result.exists()
    assert result.size > 0
    assert result.content_type == "application/json"
```

## 14.7. Testy smoke

### 14.7.1. Podstawowy test funkcjonalności
```python
def test_basic_functionality():
    """Podstawowy test działania systemu"""
    # 1. Upload pliku
    file_id = upload_test_audio()
    
    # 2. Publikacja do Pub/Sub
    message_id = publish_transcription_request(file_id)
    
    # 3. Weryfikacja przetwarzania
    result = verify_processing(message_id)
    
    # 4. Sprawdzenie wyniku
    assert result.status == "completed"
    assert result.transcript
    assert result.error is None
```

### 14.7.2. Test komponentów
```yaml
smoke_test_components:
  - name: "Google Drive API"
    endpoint: "https://www.googleapis.com/drive/v3/files"
    method: "GET"
    expected_status: 200
    
  - name: "Pub/Sub Topics"
    check: "gcloud pubsub topics list"
    expected_topics:
      - "sonus-pubsub-topic"
      - "sonus-pubsub-topic-test"
      
  - name: "Cloud Run Jobs"
    check: "gcloud run jobs list"
    expected_jobs:
      - "activator"
      - "transcriber"
      
  - name: "Storage Buckets"
    check: "gsutil ls"
    expected_buckets:
      - "gs://sonus-test-reports/"
      - "gs://sonus-whisperx-models/"
```

### 14.7.3. Automatyzacja testów smoke
```bash
#!/bin/bash
# smoke_tests.sh

# 1. Sprawdź dostępność API
check_api_health() {
    curl -s -o /dev/null -w "%{http_code}" \
        "https://REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs"
}

# 2. Sprawdź Pub/Sub
check_pubsub() {
    gcloud pubsub topics list --format="value(name)" | grep "sonus-pubsub-topic"
}

# 3. Sprawdź Cloud Run Jobs
check_jobs() {
    gcloud run jobs list --region=REGION --format="value(name)"
}

# 4. Wykonaj test transkrypcji
run_transcription_test() {
    # Upload testowego pliku
    gsutil cp test_audio.mp3 gs://sonus-test-reports/smoke_test/
    
    # Publikuj żądanie
    gcloud pubsub topics publish sonus-pubsub-topic-test \
        --message="file_id=smoke_test"
        
    # Czekaj na wynik
    timeout 300 watch -g "gsutil ls gs://sonus-test-reports/smoke_test/*.txt"
}

# Wykonaj testy
main() {
    echo "Running smoke tests..."
    
    # Sprawdź komponenty
    api_status=$(check_api_health)
    pubsub_status=$(check_pubsub)
    jobs_status=$(check_jobs)
    
    # Wykonaj test end-to-end
    transcription_status=$(run_transcription_test)
    
    # Raportuj wyniki
    echo "API Status: $api_status"
    echo "Pub/Sub Status: $pubsub_status"
    echo "Jobs Status: $jobs_status"
    echo "Transcription Test: $transcription_status"
}

main
```

## 14.8. Metryki i progi akceptacji testów

### 14.8.1. Metryki wydajności
```yaml
performance_metrics:
  processing_speed:
    unit: "seconds per minute of audio"
    thresholds:
      acceptable: "<= 30"
      optimal: "<= 20"
      
  resource_usage:
    cpu:
      unit: "percent"
      thresholds:
        warning: "> 80% for 5min"
        critical: "> 90% for 1min"
    memory:
      unit: "percent"
      thresholds:
        warning: "> 85% for 5min"
        critical: "> 95% for 1min"
        
  throughput:
    unit: "files per hour"
    thresholds:
      minimum: ">= 10"
      target: ">= 20"
```

### 14.8.2. Metryki niezawodności
```yaml
reliability_metrics:
  error_rate:
    unit: "percent"
    thresholds:
      acceptable: "< 1%"
      warning: "> 1% for 15min"
      critical: "> 5% for 5min"
      
  availability:
    unit: "percent"
    thresholds:
      minimum: "99.9%"
      target: "99.95%"
      
  recovery_time:
    unit: "minutes"
    thresholds:
      acceptable: "< 15"
      warning: "> 15"
      critical: "> 30"
```

### 14.8.3. Metryki jakości
```yaml
quality_metrics:
  transcription_accuracy:
    unit: "percent"
    thresholds:
      minimum: "90%"
      target: "95%"
      
  word_error_rate:
    unit: "percent"
    thresholds:
      acceptable: "< 10%"
      warning: "> 10%"
      critical: "> 20%"
      
  diarization_accuracy:
    unit: "percent"
    thresholds:
      minimum: "85%"
      target: "90%"
```

### 14.8.4. Raportowanie i monitorowanie
```python
def generate_test_report(metrics):
    """Generuje raport z testów"""
    report = {
        "summary": {
            "total_tests": metrics.total,
            "passed": metrics.passed,
            "failed": metrics.failed,
            "duration": metrics.duration
        },
        "performance": {
            "avg_processing_time": metrics.avg_time,
            "max_processing_time": metrics.max_time,
            "throughput": metrics.throughput
        },
        "resources": {
            "cpu_usage": metrics.cpu_stats,
            "memory_usage": metrics.memory_stats,
            "disk_io": metrics.disk_stats
        },
        "quality": {
            "accuracy": metrics.accuracy,
            "error_rate": metrics.error_rate
        }
    }
    
    # Export to Cloud Storage
    export_report(report, "gs://sonus-test-reports/")
    
    # Send alerts if needed
    if metrics.has_failures():
        send_alert("Test failures detected", report)
```

# 15. Debugowanie i rozwiązywanie problemów

## 15.1. Problemy z uprawnieniami
```bash
# Sprawdzenie uprawnień Service Account
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format='table(bindings.role,bindings.members)' \
  --filter="bindings.members:sonus-transcription-sa"
```

## 15.2. Problemy z Cloud Build
```bash
# Sprawdzenie historii buildów w regionie
gcloud builds list --project=$PROJECT_ID --region=REGION --limit=5

# Sprawdzenie aktualnie działających buildów
gcloud builds list --project=$PROJECT_ID --region=REGION --ongoing

# Szczegóły konkretnego builda
gcloud builds describe BUILD_ID --project=$PROJECT_ID --region=REGION

# Sprawdzenie logów builda
gcloud builds log BUILD_ID --project=$PROJECT_ID --region=REGION

# Monitorowanie statusu builda
# STATUS może być: WORKING, SUCCESS, FAILURE, CANCELLED, TIMEOUT
gcloud builds list --project=$PROJECT_ID --region=REGION --filter="status=WORKING"
```

## 15.3. Problemy z Cloud Run Job
```bash
# Sprawdzenie konfiguracji zadania
gcloud run jobs describe activator --region=REGION --project=$PROJECT_ID

# Sprawdzenie logów wykonania
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=activator" \
  --project=$PROJECT_ID --format="json"
```

## 15.4. Debugowanie i logowanie

### 15.4.1. Konfiguracja logowania
System wykorzystuje dwa tryby logowania:

1. **Środowisko lokalne** (gdy zmienna K_SERVICE nie jest ustawiona):
   - Używa StreamHandler z własnym formatterem
   - Logi wyświetlane w konsoli
   - Format: `%(asctime)s - %(levelname)s - %(message)s`
   - Poziomy logowania konfigurowalne przez zmienną DEBUG

2. **Cloud Run** (gdy zmienna K_SERVICE jest ustawiona):
   - Integracja z Cloud Logging
   - Automatyczne tagowanie logów
   - Strukturyzowane logi w formacie JSON
   - Poziomy logowania mapowane na severity w Cloud Logging

### 15.4.2. Debugowanie WhisperX
W przypadku problemów z biblioteką WhisperX:

```bash
# Sprawdzenie dokumentacji funkcji load_model
python3 -c "import whisperx; help(whisperx.load_model)"

# Przykładowy output:
# Help on function load_model in module whisperx.asr:
#
# load_model(whisper_arch: str, device: str, device_index=0, compute_type='float16',
#           asr_options: Optional[dict] = None, language: Optional[str] = None,
#           vad_model: Optional[whisperx.vad.VoiceActivitySegmentation] = None,
#           vad_options: Optional[dict] = None, model: Optional[whisperx.asr.WhisperModel] = None,
#           task='transcribe', download_root: Optional[str] = None, local_files_only=False,
#           threads=4) -> whisperx.asr.FasterWhisperPipeline
```

Ten sposób debugowania pozwala na:
- Sprawdzenie aktualnej wersji biblioteki i jej zależności
- Weryfikację dostępnych argumentów funkcji
- Zrozumienie typów danych wymaganych przez funkcje
- Dostęp do dokumentacji bezpośrednio z kodu

### 15.4.3. Struktura logów
System używa spójnej struktury logów:

1. **Logi operacyjne**:
   ```json
   {
     "severity": "INFO",
     "component": "transcriber",
     "operation": "transcribe",
     "file_id": "string",
     "duration_ms": "number",
     "error": "string?"
   }
   ```

2. **Logi błędów**:
   ```json
   {
     "severity": "ERROR",
     "component": "transcriber",
     "operation": "transcribe",
     "file_id": "string",
     "error": "string",
     "stack_trace": "string?"
   }
   ```

### 15.4.4. Dobre praktyki logowania
1. **Poziomy logów**:
   - DEBUG: Szczegółowe informacje dla deweloperów
   - INFO: Standardowe informacje operacyjne
   - WARNING: Potencjalne problemy
   - ERROR: Błędy wymagające uwagi
   - CRITICAL: Błędy krytyczne

2. **Strukturyzacja**:
   - Używaj stałych kluczy w logach
   - Dodawaj kontekst (file_id, operation)
   - Unikaj wrażliwych danych
   - Zachowuj spójny format

3. **Obsługa błędów**:
   - Loguj pełny stack trace
   - Dodawaj unikalny error_id
   - Kategoryzuj błędy
   - Zachowuj kontekst operacji

# 16. Logowanie i monitoring

## 16.1. Logowanie w Cloud Logging

### 16.1.1. Konfiguracja logowania
- Poziomy logowania:
  * DEBUG: Szczegółowe informacje dla debugowania
  * INFO: Standardowe informacje o działaniu
  * WARNING: Potencjalne problemy
  * ERROR: Błędy wymagające uwagi
  * CRITICAL: Krytyczne błędy wymagające natychmiastowej reakcji

### 16.1.2. Wyszukiwanie logów
```bash
# Logi z Cloud Run Jobs
gcloud logging read "resource.type=cloud_run_job" \
  --project=$PROJECT_ID \
  --format="table(timestamp,severity,textPayload)"

# Logi z konkretnego jobu
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=activator" \
  --project=$PROJECT_ID

# Logi błędów
gcloud logging read "severity>=ERROR" \
  --project=$PROJECT_ID
```

## 16.2. Monitoring w Cloud Monitoring

### 16.2.1. Metryki systemowe
- CPU usage
- Memory usage
- Network traffic
- Disk I/O
- Container restarts

### 16.2.2. Metryki aplikacyjne
- Liczba przetworzonych plików
- Czas transkrypcji
- Rozmiar plików
- Liczba błędów
- Wykorzystanie kolejek Pub/Sub

### 16.2.3. Alerty
- Konfiguracja alertów dla:
  * Wysokiego użycia zasobów
  * Błędów aplikacji
  * Długiego czasu przetwarzania
  * Problemów z kolejkami

## 16.3. Dashboardy
- Przegląd systemu
- Statystyki przetwarzania
- Monitoring zasobów
- Alerty i incydenty

## 16.4. Retencja danych
- Logi: 30 dni
- Metryki: 6 miesięcy
- Raporty: 1 rok

## 16.5. Szczegółowa konfiguracja

### 16.5.1. Struktury logów
```json
{
  "severity": "INFO",
  "component": "activator|transcriber",
  "operation": "scan|transcribe",
  "file_id": "string",
  "duration_ms": number,
  "error": "string?",
  "labels": {
    "env": "prod|test",
    "version": "string"
  }
}
```

### 16.5.2. Filtry logów
```bash
# Logi błędów z ostatniej godziny
resource.type="cloud_run_job"
severity>=ERROR
timestamp>="2024-02-24T01:57:12Z"

# Długie transkrypcje (>10 min)
resource.type="cloud_run_job"
jsonPayload.component="transcriber"
jsonPayload.duration_ms>600000
```

### 16.5.3. Metryki niestandardowe

#### Metryki Activator
- **sonus.activator.files_scanned** (counter)
  * Liczba przeskanowanych plików
  * Labels: env, file_type
- **sonus.activator.files_queued** (counter)
  * Liczba plików dodanych do kolejki
  * Labels: env, file_type
- **sonus.activator.scan_duration** (distribution)
  * Czas trwania skanowania (ms)
  * Labels: env

#### Metryki Transcriber
- **sonus.transcriber.processing_duration** (distribution)
  * Czas przetwarzania pliku (ms)
  * Labels: env, file_type
- **sonus.transcriber.file_size** (distribution)
  * Rozmiar przetwarzanego pliku (bytes)
  * Labels: env, file_type
- **sonus.transcriber.errors** (counter)
  * Liczba błędów transkrypcji
  * Labels: env, error_type

### 16.5.4. Alerty

#### Alert: Długi czas przetwarzania
```yaml
combiner: OR
conditions:
- conditionThreshold:
    aggregations:
    - alignmentPeriod: 300s
      crossSeriesReducer: REDUCE_PERCENTILE_95
      perSeriesAligner: ALIGN_DELTA
    comparison: COMPARISON_GT
    duration: 0s
    filter: metric.type="custom.googleapis.com/sonus.transcriber.processing_duration"
    thresholdValue: 1800000  # 30 minut
    trigger:
      count: 1
displayName: "Transcriber - Długi czas przetwarzania"
```

#### Alert: Wysoki wskaźnik błędów
```yaml
combiner: OR
conditions:
- conditionThreshold:
    aggregations:
    - alignmentPeriod: 300s
      crossSeriesReducer: REDUCE_SUM
      perSeriesAligner: ALIGN_RATE
    comparison: COMPARISON_GT
    duration: 300s
    filter: metric.type="custom.googleapis.com/sonus.transcriber.errors"
    thresholdValue: 0.1  # >10% błędów
    trigger:
      count: 1
displayName: "Transcriber - Wysoki wskaźnik błędów"
```

# 17. Praca z Gitem

## 17.1. Konfiguracja repozytoriów

1. Włączenie API i utworzenie repozytorium:
   - API: sourcerepo.googleapis.com
   - Nazwa repozytorium: sonus-activator
   - Projekt: example-project-id
   - Disable on destroy: false

2. Konfiguracja uprawnień:
   - Service Account:
     * Rola: roles/source.reader
     * Konto: sonus-transcription-sa@example-project-id.iam.gserviceaccount.com
   - Cloud Build:
     * Rola: roles/source.reader
     * Konto: ${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com

## 17.2. Inicjalizacja repozytoriów
```bash
# Klonowanie repozytoriów
gcloud source repos clone sonus-activator --project=$PROJECT_ID
gcloud source repos clone sonus-transcriber --project=$PROJECT_ID

# Inicjalizacja Git dla activator
cd sonus-activator
git add .
git commit -m "Initial commit"
git push origin main

# Inicjalizacja Git dla transcriber
cd ../sonus-transcriber
git add .
git commit -m "Initial commit"
git push origin main
```

## 17.3. Proces wdrażania nowej wersji
Nowe wersje wdraża się przez utworzenie tagu - szczegółowy proces opisano w rozdziale 18 "Wdrażanie zmian (Release Flow)".

## 17.4. Weryfikacja wdrożenia
1. Sprawdź status builda w Cloud Build
2. Zweryfikuj, czy Cloud Run Job używa nowej wersji
3. Wykonaj test poprzez ręczne uruchomienie zadania
4. Sprawdź logi pod kątem błędów

# 18. Wdrażanie zmian (Release Flow)

## 18.1. Proces wdrażania nowej wersji
Aby wdrożyć nową wersję aplikacji:

1. Zaktualizuj plik CHANGELOG.md dodając nową wersję i opis zmian
2. Skommituj i wdróż zmiany używając następującej komendy:
   ```bash
   cd sonus-transcriber && git add CHANGELOG.md UNIT_TEST.md && git commit -m "feat: Enhanced test suite for unsupported file extensions" && git tag v0.0.38 && git push origin master && git push origin v0.0.38
   ```

## 18.2. Weryfikacja wdrożenia
Po wdrożeniu nowej wersji:
1. Sprawdź status builda w Cloud Build
2. Zweryfikuj, czy Cloud Run Job używa nowej wersji
3. Wykonaj test poprzez ręczne uruchomienie zadania
4. Sprawdź logi pod kątem błędów

## 18.3. Monitorowanie procesu
```bash
# Sprawdzenie statusu builda
gcloud builds list --project=$PROJECT_ID --region=REGION --filter="tags~v0.0.38"

# Sprawdzenie wersji obrazu w Cloud Run Job
gcloud run jobs describe transcriber \
  --region=REGION \
  --project=$PROJECT_ID \
  --format="get(spec.template.spec.containers[0].image)"

# Sprawdzenie logów z wdrożenia
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=transcriber" \
  --project=$PROJECT_ID \
  --format="table(timestamp,severity,textPayload)"
```

# 19. Uwagi końcowe i planowane rozszerzenia

## 19.1. Regularne zadania utrzymaniowe
- Sprawdzanie logów i metryk w Cloud Logging
- Monitorowanie zużycia zasobów i kosztów w Cloud Console
- Aktualizacja komponentów systemu do najnowszych wersji
- Wykonywanie kopii zapasowych konfiguracji
- Testowanie systemu na małej próbce plików przed pełnym wdrożeniem

## 19.2. Planowane rozszerzenia

### 19.2.1. Optymalizacja wydajności
- Implementacja cache'owania modeli WhisperX
- Optymalizacja wykorzystania pamięci
- Równoległe przetwarzanie plików
- Implementacja wsadowego przetwarzania plików w segmentach
- Konfiguracja limitów:
  * Cloud Run Job timeout: 60 minut
  * Pamięć kontenera: 512Mi
  * Przepustowość sieci: zależna od regionu
- Optymalizacja wykorzystania zasobów poprzez dynamiczne skalowanie

### 19.2.2. Rozszerzenia funkcjonalne
- Wsparcie dla większej liczby formatów plików
- Automatyczna detekcja języka
- Zaawansowana diaryzacja mówców
- Eksport do różnych formatów
- Integracja z WhisperX do automatycznego wykrywania języka
- Konfiguracja modeli językowych:
  * Polski: whisper-large-v3-pl
  * Angielski: whisper-large-v3
  * Niemiecki: whisper-large-v3-de
  * Francuski: whisper-large-v3-fr
- Przechowywanie modeli w dedykowanym buckecie GCS

### 19.2.3. Monitoring i raportowanie
- Rozbudowane dashboardy w Cloud Monitoring
- System powiadomień o błędach
- Automatyczne raporty wydajności
- Statystyki wykorzystania
- Dedykowana kolejka Pub/Sub dla błędów:
  * Topic: sonus-error-queue
  * Subscription: sonus-error-handler-sub
  * Retencja: 7 dni
  * Dead-letter queue: po 5 próbach
- System monitoringu błędów:
  * Automatyczna klasyfikacja błędów
  * Agregacja podobnych błędów
  * Priorytetyzacja według severity

### 19.2.4. Bezpieczeństwo
- Regularne audyty uprawnień
- Skanowanie podatności kontenerów
- Monitorowanie dostępu do zasobów
- Rotacja kluczy i sekretów
- System powiadomień:
  * Integracja z Cloud Monitoring
  * Alerty przez email/Slack
  * Eskalacja krytycznych błędów

## 19.3. Zalecenia dotyczące utrzymania
1. Monitorowanie:
   - Regularnie sprawdzać logi błędów
   - Monitorować zużycie zasobów
   - Śledzić metryki wydajności
   - Analizować trendy w użyciu

2. Aktualizacje:
   - Testować nowe wersje WhisperX
   - Aktualizować zależności Python
   - Sprawdzać kompatybilność GCP API
   - Testować na środowisku staging

3. Backup i odtwarzanie:
   - Regularnie tworzyć kopie konfiguracji
   - Testować procedury odtwarzania
   - Dokumentować zmiany w systemie
   - Przechowywać historię wdrożeń


# 20. Struktura projektu

```
.
├── CHANGELOG.md                     # Historia zmian projektu
├── README.md                        # Dokumentacja użytkownika
├── StepByStep.md                    # Dokumentacja techniczna
├── TODO.md                          # Lista planowanych zadań
├── infrastructure/                  # Konfiguracja infrastruktury
│   └── modules/                     # Moduły Terraform
│       ├── artifact-registry/       # Konfiguracja Artifact Registry
│       ├── cloud-build/             # Konfiguracja Cloud Build
│       ├── cloud-run/               # Konfiguracja Cloud Run Jobs
│       ├── pubsub/                  # Konfiguracja Pub/Sub
│       ├── secrets/                 # Konfiguracja Secret Manager
│       ├── source-repo/             # Konfiguracja Cloud Source Repositories
│       │   └── files/               # Pliki konfiguracyjne dla repo
│       └── storage/                 # Konfiguracja Cloud Storage
├── examples/                        # Przykłady i testy
│   ├── tuning_results/              # Wyniki dostrajania parametrów
│   └── tuning_results_01/           # Dodatkowe wyniki dostrajania
├── sonus-activator/                 # Komponent Activator
│   ├── src/                         # Kod źródłowy
│   │   └── activator/               # Moduł Python implementujący Activator
│   └── tests/                       # Testy jednostkowe i integracyjne
│       └── files/                   # Pliki testowe
└── sonus-transcriber/               # Komponent Transcriber
    ├── coverage_html/               # Raporty pokrycia testów
    ├── src/                         # Kod źródłowy
    │   └── transcriber/             # Moduł Python implementujący Transcriber
    │       └── storage/             # Implementacje storage (drive, local)
    └── tests/                       # Testy jednostkowe i integracyjne
        └── files/                   # Pliki testowe
```

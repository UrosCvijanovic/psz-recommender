# PSZ pokretanje aplikacije

## A) Sa Docker-om

```bash
docker compose up --build
```

- Aplikacija: http://localhost:5000
- pgAdmin: http://localhost:8889 (uros@domain-name.com / lozinka iz `docker-compose.yaml`)
- Baza se pri prvom pokretanju automatski inicijalizuje iz `baza/*.sql`

Reset baze (briše podatke i ponovo učitava dump):

```bash
docker compose down -v
docker compose up --build
```

## B) Bez Docker-a (lokalni PostgreSQL + Python)

### 1. Baza — kreiranje i uvoz podataka

```bash
psql -U postgres -c "CREATE DATABASE psz;"
psql -U postgres -d psz -f baza/01_psz_dump.sql
```

### 2. Python okruženje

```bash
cd kod
python -m venv .venv
.venv\Scripts\activate          # Windows

pip install -r requirements.txt
```

### 3. Parametri konekcije

Podrazumevani port u kodu je 5433 (Docker), pa za lokalni PostgreSQL treba postaviti:

```bash
set DB_HOST=localhost
set DB_PORT=5432
set DB_USER=postgres
set DB_PASSWORD=<lozinka>
set DB_NAME=psz
```

### 4. Pokretanje aplikacije (iz foldera `kod/`)

```bash
flask --app aplikacija.app run
```

Aplikacija: http://127.0.0.1:5000

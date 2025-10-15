# README — نظام محاسبي متكامل (Modern Accounting System)

> مستودع مفتوح المصدر/خاص لنظام محاسبي متكامل مبني بأحدث الممارسات والتقنيات. الوثيقة هذه تشرح النظرة العامة، البناء المعماري، التشغيل المحلي، النشر، ومواضع التوسعة.

---

## 📌 نظرة عامة

نظام محاسبي متكامل يدعم:

* المحاسبة مزدوجة القيود (Double-entry bookkeeping)
* دليل حسابات قابل للتخصيص (Chart of Accounts)
* قيود اليومية، دفتر الأستاذ، ميزان المراجعة، قائمة الدخل، الميزانية العمومية
* قيود ضريبة القيمة المضافة، تقارير ضريبية دورية
* فواتير ومقبوضات ومدفوعات، إدارة عملاء وموردين
* متعدد العملات، حسابات بنكية متعددة، تسويات بنكية
* صلاحيات متقدمة (RBAC) وسجلات تدقيق (Audit Trail)
* واجهة REST/GraphQL + واجهة ويب حديثة + تطبيق جوال (اختياري)

---

## ⚙️ أهداف التصميم

* قابلية توسعة عالية (Modular, Plugin-friendly)
* أداء عالي (Async I/O, Indexing)
* أمان متقدم (JWT/OAuth2, CSRF, Input validation)
* قابلية النشر عبر الحاويات (Docker, Kubernetes)
* اختبارات شاملة (unit, integration, e2e)
* واجهات برمجية موثقة (OpenAPI / GraphQL + Swagger)

---

## 🧰 المكدس التقني المقترح (Recommended Tech Stack)

> يمكنك استبدال أي جزء بما تفضّل، لكن هذا المزيج حديث، واسع الاستخدام، وقابل للصيانة.

### Back-end

* **لغة:** Python 3.11+
* **إطار عمل:** FastAPI (async, OpenAPI مدمج)
* **ORM:** SQLModel أو SQLAlchemy (مع Alembic للترحيل)
* **Cache / Tasks:** Redis + RQ / Celery (اختياري)
* **Message Broker:** RabbitMQ أو Redis Streams (للمهام الخلفية، إشعارات)
* **Auth:** OAuth2 / OpenID Connect + JWT، مع دعم 2FA
* **Rate limiting & Security:** FastAPI middlewares, OAuth scopes, Helmet-like headers

### Database & Storage

* **RDBMS:** PostgreSQL (يفضل مع Timescale إذا احتجت زمنية متقدمة)
* **Full-text / Search:** PostgreSQL full-text أو ElasticSearch (اختياري)
* **Object Storage:** S3-compatible (MinIO, AWS S3) للملفات/المرفقات

### Front-end

* **Framework:** React + TypeScript + Vite
* **UI:** Tailwind CSS أو شاد.سي.إن (shadcn/ui) أو Material UI
* **State / Data fetching:** React Query / TanStack Query
* **Forms & Validation:** React Hook Form + Zod

### Mobile (اختياري)

* **Framework:** Flutter أو React Native (TypeScript)

### DevOps / CI

* **Containerization:** Docker + docker-compose
* **Orchestration:** Kubernetes + Helm Charts (للإنتاج)
* **CI/CD:** GitHub Actions / GitLab CI
* **Monitoring:** Prometheus + Grafana, Sentry (الأخطاء)
* **Logging:** ELK / Loki

### Testing

* **Unit/Integration:** pytest, httpx (Async test client)
* **E2E:** Playwright أو Cypress
* **Type checking:** mypy, pyright

---

## 🏗️ بنية المشروع (Suggested repo layout)

```
/backend
  /app
    main.py
    api/
    core/
    models/
    schemas/
    services/
    tasks/
    migrations/
  Dockerfile
/frontend
  /src
    pages/
    components/
  Dockerfile
/mobile (optional)
infra/
  docker-compose.yml
  k8s/
  helm/
tests/
README.md
```

---

## 🔧 المتطلبات المسبقة

* Docker & docker-compose
* Python 3.11+
* Node.js 18+
* PostgreSQL (يمكن تشغيلها عبر docker-compose)
* (اختياري) Redis, RabbitMQ

---

## 🚀 التشغيل المحلي — مثال سريع باستخدام Docker Compose

### مثال `docker-compose.yml` (موجز)

```yaml
version: "3.8"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: acct_user
      POSTGRES_PASSWORD: acct_pass
      POSTGRES_DB: accounting
    volumes:
      - db_data:/var/lib/postgresql/data
  redis:
    image: redis:7
  backend:
    build: ./backend
    env_file: .env
    depends_on: [db, redis]
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
volumes:
  db_data:
```

### ملف `.env` مثال

```
DATABASE_URL=postgresql+asyncpg://acct_user:acct_pass@db:5432/accounting
REDIS_URL=redis://redis:6379/0
SECRET_KEY=changeme_replace_with_strong_key
JWT_ALGORITHM=HS256
```

### أوامر تشغيل

```bash
# 1) تشغيل الحاويات
docker-compose up --build

# 2) تشغيل ترحيلات القاعدة (داخل حاوية backend)
# مثال ل Alembic:
docker-compose exec backend alembic upgrade head

# 3) تحميل بيانات تجريبية (seeds) - أمر مخصص في السكريبتات
docker-compose exec backend python app/scripts/seed_demo.py
```

---

## 📚 نموذج قواعد بيانات أساسي (مقتطفات)

> مكونات محاسبية مهمة (مقترح مبسط):

* **accounts** (حسابات دفترية: asset, liability, equity, revenue, expense)

  * id, code, name, parent_id, type, normal_balance, currency, is_active
* **journal_entries**

  * id, date, reference, description, created_by, posted (bool)
* **journal_lines**

  * id, journal_entry_id, account_id, debit, credit, currency_amount
* **invoices**

  * id, type (sale/purchase), partner_id, date, due_date, status, total, tax_total
* **payments**

  * id, invoice_id, amount, method, date, reference
* **partners** (customers/suppliers)
* **banks** / **bank_reconciliations**
* **audit_logs** (who changed ماذا ووقت)

> التأكد من وجود قيود تحقق (constraints) ومفاتيح أجنبية ومؤشرات (indexes) للأعمدة المستخدمة في الاستعلامات.

---

## ✅ قواعد محاسبية أساسية قابلة للتنفيذ

* تنفيذ القيود مزدوجة: لكل قيد يومية مجموع الديون = مجموع الدائنات.
* آلية "posting" للقيد: القيد يتم إنشاؤه كمسودة ثم يُنشر (post) ويُقفل السجّل.
* إرجاع أو تعديل فقط عبر قيد معاكس (reversal) مع سجل تدقيق.
* تقارير زمنية: ميزان المراجعة، تقارير ضريبية، كشف حساب عميل/مورد.

---

## 🔐 الأمن والامتثال

* التشفير: تشفير بيانات حساسة في الراحة (PGP/TDE) وTLS للنقل.
* صلاحيات دقيقة: RBAC مع دور Admin/Accountant/Viewer/Manager.
* تدقيق: تسجيل كل تغيّر (من، إلى، وقت، IP).
* حماية من الهجمات: rate limiting, CSRF protection, input validation (Zod/Pydantic).
* نسخ احتياطية: نسخ دورية لقاعدة البيانات إلى S3، واختبار استعادة النسخ.

---

## 📄 توثيق API

* FastAPI يولّد OpenAPI/Swagger تلقائياً: `GET /docs` و`/redoc`
* أمثلة نقاط نهاية مهمة:

  * `POST /api/journals/` — إنشاء قيد مسودة
  * `POST /api/journals/{id}/post` — نشر قيد (post)
  * `GET /api/reports/trial-balance?date_from=...&date_to=...`
  * `GET /api/invoices/{id}/pdf` — تحميل الفاتورة PDF
* دعم GraphQL اختياري لنقاط نهاية تحليلية.

---

## 🧪 الاختبارات

* اكتب اختبارات لكل خدمة: business logic (قواعد محاسبية)، API endpoints، واجهة المستخدم.
* استخدم fixtures لإنشاء حسابات/قيود تجريبية.
* ادمج تشغيل الاختبارات في CI (GitHub Actions).

مثال GitHub Actions snippet:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest -q
```

---

## 📦 النشر (Production)

1. بناء الحاويات (multi-stage Dockerfile).
2. نشر على Kubernetes مع:

   * Secrets management (Vault / Kubernetes Secrets)
   * Horizontal Pod Autoscaler للـ backend
   * PersistentVolume لقاعدة البيانات
3. إعداد CDN وTLS (Let's Encrypt / Cert-Manager)
4. إعداد مراقبة وصحة endpoints (liveness/readiness probes)
5. إعداد استراتيجية ترحيل سلسة (blue/green أو canary)

---

## ♻️ التوسعة والملحقات

* بوابة دفع (Stripe/PayPal) للفواتير
* تكامل مع أنظمة بنكية (Open Banking)
* تقارير ضريبية قابلة للتصدير (XML/ISO)
* دعم تعدد الشركات (multi-entity)
* واجهات محاسبية معيارية (IFRS/LOCAL GAAP)

---

## 🧭 خارطة الطريق (اقتراح)

1. MVP: دليل الحسابات، قيود اليومية، تقارير أساسية، فواتير، دفع
2. إصدار 1.0: مصادقة/صلاحيات، سجلات تدقيق، ترحيل بيانات
3. إصدار 2.0: تقارير ضريبية متقدمة، تعدد عملات، تسويات بنكية
4. إصدار 3.0: تنبيهات ذكية، تحليل مالي، AI-based reconciliation (اختياري)

---

## 🤝 المساهمة (How to Contribute)

1. افتح issue أو feature request.
2. اتبع نمط الفروع: `feature/xxx` أو `fix/yyy`.
3. أرسل Pull Request مع وصف مفصل واختبارات.
4. اتبع قواعد الترميز (formatters, linters).

---

## 🧾 الترخيص

اختر ترخيصاً مناسباً للمشروع (MIT، Apache-2.0، أو ترخيص تجاري مخصص). مثال: `MIT License`.

---

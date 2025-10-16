# نشر النظام على Ubuntu

هذه إرشادات مختصرة لنشر البنية الأساسية والباكند على خادم Ubuntu جديد.

## المتطلبات
- مستخدم لديه صلاحيات sudo
- منفذ 8000 مفتوح (أو خلف Proxy)

## خطوات سريعة
1. استنسخ المستودع إلى الخادم:
   ```bash
   git clone <REPO_URL> accounting-system && cd accounting-system
   ```
2. انسخ ملف البيئة الافتراضي:
   ```bash
   cp backend/.env.example backend/.env
   # عدّل SECRET_KEY و DATABASE_URL إذا لزم
   ```
3. نفّذ سكربت النشر:
   ```bash
   ./infra/scripts/deploy_ubuntu.sh <DOMAIN_OR_IP>
   ```
4. بعد اكتمال النشر:
   - واجهة Swagger على: `http://<DOMAIN_OR_IP>:8000/docs`

## ملاحظات
- لتشغيل Alembic يدويًا:
  ```bash
  docker compose -f infra/docker-compose.yml run --rm backend alembic upgrade head
  ```
- لإيقاف الخدمات:
  ```bash
  docker compose -f infra/docker-compose.yml down
  ```

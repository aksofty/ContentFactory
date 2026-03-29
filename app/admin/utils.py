from app.admin.views import AIPromtView, FilterView, SourceRssView, SourceTgView, TargetTgView

def add_all_views(appbuilder):
    appbuilder.add_view(SourceTgView, "Telegram", category="Откуда?")
    appbuilder.add_view(SourceRssView, "RSS", category="Откуда?")

    appbuilder.add_view(TargetTgView, "Telegram", category="Куда?")

    appbuilder.add_view(FilterView, "Фильтры", category="Сервисы")
    appbuilder.add_view(AIPromtView, "AI промпты", category="Сервисы")

def create_admin(appbuilder, admin_name, admin_pass):
    if not appbuilder.sm.find_user(username="admin"):
        role_admin = appbuilder.sm.find_role("Admin")
        appbuilder.sm.add_user(
            username=admin_name,
            first_name="Admin",
            last_name="Adminov",
            email="admin@example.com",
            role=role_admin,
            password=admin_pass)
        print(f"Администратор создан: {admin_name}")
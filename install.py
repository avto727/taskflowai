import subprocess
import sys
import os

VENV_DIR = ".venv"


def create_venv():
    if not os.path.exists(VENV_DIR):
        print("Создаю виртуальное окружение...")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    else:
        print("Виртуальное окружение уже создано.")


def install_packages():
    print("Устанавливаю зависимости...")
    pip_path = os.path.join(
        VENV_DIR, "Scripts" if os.name == "nt" else "bin", "pip"
    )
    subprocess.check_call([pip_path, "install", "--upgrade", "pip"])

    # Устанавливаем из requirements.txt если файл существует
    if os.path.exists("requirements.txt"):
        subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
    else:
        # Fallback: устанавливаем минимальный набор для TaskFlowAI
        subprocess.check_call(
            [pip_path, "install", "requests", "fastapi", "uvicorn"]
        )


def create_env_file():
    """Создание .env файла с настройками TaskFlowAI"""
    if not os.path.exists(".env"):
        print("Создаю .env файл...")
        print("\n📋 Для работы TaskFlowAI нужны:")
        print(
            "1. Todoist API Token (https://todoist.com/app/settings/integrations)"
        )
        print("2. Telegram Bot Token (получить у @BotFather) - опционально")

        todoist_token = input("\nВведите Todoist API Token: ").strip()
        telegram_token = input(
            "Введите Telegram Bot Token (или Enter для пропуска): "
        ).strip()

        with open(".env", "w", encoding="utf-8") as f:
            f.write(
                "# Todoist API Token (получен на https://todoist.com/app/settings/integrations)\n"
            )
            f.write(f"TODOIST_API_TOKEN={todoist_token}\n\n")

            if telegram_token:
                f.write("# Telegram Bot Token (получить у @BotFather)\n")
                f.write(f"TELEGRAM_BOT_TOKEN={telegram_token}\n\n")

            f.write("# Ollama настройки\n")
            f.write("OLLAMA_MODEL=qwen2.5:7b\n")
            f.write("OLLAMA_BASE_URL=http://localhost:11434\n")

        print(".env файл создан.")
    else:
        print(".env файл уже существует.")


def check_todoist_setup():
    """Проверка настройки Todoist"""
    print("\n📝 Настройка Todoist:")
    print("1. Зарегистрируйтесь на https://todoist.com")
    print("2. Создайте 5 проектов:")
    print("   💰 Деньги")
    print("   👨👩👧👦 Семья")
    print("   💪 Здоровье")
    print("   💕 Отношения")
    print("   📚 Развитие")
    print(
        "3. Получите API token: https://todoist.com/app/settings/integrations"
    )

    setup_done = (
        input("\nВы выполнили настройку Todoist? (y/n): ").lower().strip()
    )
    if setup_done != "y":
        print("⚠️  Завершите настройку Todoist перед использованием TaskFlowAI")


def check_ollama():
    """Проверка установки Ollama"""
    print("\n🤖 Проверка Ollama...")
    try:
        result = subprocess.run(
            ["ollama", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Ollama установлен")

            # Проверяем модель qwen2.5:7b
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True
            )
            if "qwen2.5:7b" in result.stdout:
                print("✅ Модель qwen2.5:7b найдена")
            else:
                print("⚠️  Модель qwen2.5:7b не найдена")
                install_model = (
                    input("Установить модель qwen2.5:7b? (y/n): ")
                    .lower()
                    .strip()
                )
                if install_model == "y":
                    print("Устанавливаю модель qwen2.5:7b...")
                    subprocess.check_call(["ollama", "pull", "qwen2.5:7b"])
                    print("✅ Модель установлена")
        else:
            print("❌ Ollama не найден")
            print("Установите Ollama: https://ollama.ai")
    except FileNotFoundError:
        print("❌ Ollama не найден")
        print("Установите Ollama: https://ollama.ai")


if __name__ == "__main__":
    print("🚀 Установка TaskFlowAI (Irga New)")
    print("=" * 40)

    create_venv()
    install_packages()
    create_env_file()
    check_todoist_setup()
    check_ollama()

    print("\n✅ Установка завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Активируйте виртуальное окружение:")
    print("   source .venv/bin/activate  # Linux/Mac")
    print("   .venv\\Scripts\\activate    # Windows")
    print("2. Запустите разработку:")
    print("   python -m backend.api.main  # когда будет готов API")
    print("\n📖 Подробнее в README.md")

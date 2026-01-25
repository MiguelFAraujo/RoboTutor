try:
    from core.models import Conversation
    print("Import Success")
except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()

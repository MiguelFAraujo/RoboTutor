from core.catalog import PROJECT_PACKS, get_pack_by_slug, get_pack_pdf_path


def get_catalog_overview():
    platforms = sorted({pack["platform"] for pack in PROJECT_PACKS})
    return {
        "platforms": platforms,
        "pack_count": len(PROJECT_PACKS),
        "packs": [decorate_pack(pack) for pack in PROJECT_PACKS],
    }


def decorate_pack(pack):
    decorated = dict(pack)
    decorated["project_count"] = len(pack["projects"])
    decorated["pdf_exists"] = get_pack_pdf_path(pack["slug"]).exists()
    decorated["download_url"] = f"/academy/pdfs/{pack['slug']}/"
    return decorated


def get_catalog_pack(slug):
    pack = get_pack_by_slug(slug)
    if not pack:
        return None
    return decorate_pack(pack)

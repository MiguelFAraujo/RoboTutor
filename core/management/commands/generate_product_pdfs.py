from django.core.management.base import BaseCommand, CommandError

from core.services.pdf_service import generate_catalog_bundle, generate_single_pack


class Command(BaseCommand):
    help = "Gera PDFs comerciais dos packs de projetos do RoboTutor."

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str, help="Gera apenas o pack indicado.")
        parser.add_argument("--output-dir", type=str, help="Diretorio de saida opcional.")

    def handle(self, *args, **options):
        slug = options.get("slug")
        output_dir = options.get("output_dir")

        if slug:
            try:
                created = generate_single_pack(slug, output_dir)
            except ValueError as exc:
                raise CommandError(str(exc)) from exc
            self.stdout.write(self.style.SUCCESS(f"PDF gerado: {created}"))
            return

        created_files = generate_catalog_bundle(output_dir)
        self.stdout.write(self.style.SUCCESS(f"{len(created_files)} PDFs gerados com sucesso."))
        for path in created_files:
            self.stdout.write(f" - {path}")

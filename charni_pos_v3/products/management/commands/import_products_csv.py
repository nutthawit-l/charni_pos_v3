"""Import products from a v2-style products CSV into the v3 schema.

CSV columns: image_url, name, category, thb, sgd

Each row becomes:
  - Category (get-or-create by name + shop)
  - Product (name, image_url, shop, category; stock defaults to 0)
  - ProductPrice rows for non-empty thb / sgd values
"""

from __future__ import annotations

import csv
from decimal import Decimal
from decimal import InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from charni_pos_v3.products.models import Category
from charni_pos_v3.products.models import Product
from charni_pos_v3.products.models import ProductPrice
from charni_pos_v3.shops.models import Shop


class Command(BaseCommand):
    help = "Import products from a CSV file (image_url, name, category, thb, sgd)."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path to products.csv",
        )
        parser.add_argument(
            "--shop-id",
            type=int,
            help="Existing shop primary key to attach products to",
        )
        parser.add_argument(
            "--shop-name",
            type=str,
            help="Shop name to get or create (used when --shop-id is omitted)",
        )
        parser.add_argument(
            "--stock",
            type=int,
            default=0,
            help="Initial stock for imported products (default: 0)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and report what would be created without writing",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Skip rows whose product name already exists for the shop",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"]).expanduser().resolve()
        if not csv_path.is_file():
            error_msg = f"CSV not found: {csv_path}"
            raise CommandError(error_msg)

        stock = options["stock"]
        if stock < 0:
            error_msg = "--stock must be >= 0"
            raise CommandError(error_msg)

        rows = self._read_csv(csv_path)
        if not rows:
            error_msg = "CSV has no data rows"
            raise CommandError(error_msg)

        dry_run = options["dry_run"]
        skip_existing = options["skip_existing"]

        created_products = 0
        skipped_products = 0
        created_categories = 0
        created_prices = 0
        shop: Shop | None = None

        with transaction.atomic():
            shop = self._resolve_shop(options)

            for index, row in enumerate(rows, start=2):
                name = row["name"]
                if (
                    skip_existing
                    and Product.objects.filter(
                        shop=shop,
                        name=name,
                    ).exists()
                ):
                    skipped_products += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Line {index}: skip existing product '{name}'",
                        ),
                    )
                    continue

                category, cat_created = Category.objects.get_or_create(
                    name=row["category"],
                    shop=shop,
                )
                if cat_created:
                    created_categories += 1

                product = Product.objects.create(
                    name=name,
                    image_url=row["image_url"],
                    stock=stock,
                    shop=shop,
                    category=category,
                )
                created_products += 1

                for currency_code, amount in (
                    ("THB", row["thb"]),
                    ("SGD", row["sgd"]),
                ):
                    if amount is None:
                        continue
                    ProductPrice.objects.create(
                        product=product,
                        price=amount,
                        currency_code=currency_code,
                    )
                    created_prices += 1

            if dry_run:
                transaction.set_rollback(True)

        assert shop is not None
        prefix = "[dry-run] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}Shop: {shop.name} (id={shop.pk}) | "
                f"products={created_products} skipped={skipped_products} | "
                f"categories_created={created_categories} | "
                f"prices={created_prices}",
            ),
        )

    def _resolve_shop(self, options) -> Shop:
        shop_id = options.get("shop_id")
        shop_name = options.get("shop_name")

        if shop_id is not None:
            try:
                return Shop.objects.get(pk=shop_id)
            except Shop.DoesNotExist as exc:
                error_msg = f"Shop id={shop_id} does not exist"
                raise CommandError(error_msg) from exc

        if shop_name:
            shop, created = Shop.objects.get_or_create(name=shop_name)
            if created:
                self.stdout.write(
                    self.style.WARNING(f"Created shop '{shop.name}' (id={shop.pk})"),
                )
            return shop

        error_msg = "Provide either --shop-id or --shop-name"
        raise CommandError(error_msg)

    def _read_csv(self, csv_path: Path) -> list[dict]:
        required = {"image_url", "name", "category", "thb", "sgd"}
        rows: list[dict] = []

        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                error_msg = "CSV is empty or missing a header row"
                raise CommandError(error_msg)

            headers = {h.strip() for h in reader.fieldnames if h}
            missing = required - headers
            if missing:
                error_msg = f"CSV missing columns: {', '.join(sorted(missing))}"
                raise CommandError(error_msg)

            for line_no, raw in enumerate(reader, start=2):
                name = (raw.get("name") or "").strip()
                image_url = (raw.get("image_url") or "").strip()
                category = (raw.get("category") or "").strip()

                if not name:
                    error_msg = f"Line {line_no}: name is required"
                    raise CommandError(error_msg)
                if not image_url:
                    error_msg = f"Line {line_no}: image_url is required"
                    raise CommandError(error_msg)
                if not category:
                    error_msg = f"Line {line_no}: category is required"
                    raise CommandError(error_msg)

                thb = self._parse_price(raw.get("thb"), line_no, "thb")
                sgd = self._parse_price(raw.get("sgd"), line_no, "sgd")
                if thb is None and sgd is None:
                    error_msg = f"Line {line_no}: at least one of thb/sgd is required"
                    raise CommandError(error_msg)

                rows.append(
                    {
                        "image_url": image_url,
                        "name": name,
                        "category": category,
                        "thb": thb,
                        "sgd": sgd,
                    },
                )

        return rows

    def _parse_price(self, value, line_no: int, field: str) -> Decimal | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            amount = Decimal(text)
        except InvalidOperation as exc:
            error_msg = f"Line {line_no}: invalid {field} price '{value}'"
            raise CommandError(error_msg) from exc
        if amount < 0:
            error_msg = f"Line {line_no}: {field} cannot be negative"
            raise CommandError(error_msg)
        return amount

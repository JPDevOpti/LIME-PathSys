#!/usr/bin/env python3
"""
Script to insert system residents

This script creates residents in the database with the specified codes and names.
Residents include medical residents in pathology.

Usage:
    python3 Scripts/9_import_residents.py [--dry-run]

Arguments:
    --dry-run: Only show what would be done without executing real changes
"""

import sys
import os
import asyncio
import argparse
from typing import Optional, Tuple, List, Dict
from datetime import datetime

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import get_database, close_mongo_connection
from app.modules.residents.schemas.resident import ResidentCreate
from app.modules.residents.services.resident_service import ResidentService


def derive_initials(raw_name: str) -> str:
    # Take initials from name
    parts = [p for p in str(raw_name).strip().split() if p]
    return ("".join(p[0] for p in parts)[:4]).upper() if parts else "XX"


# Embedded list of residents provided
RESIDENTS_DATA: List[Dict[str, str]] = [
    {"documento": "1148205818", "nombre": "Manuela Ocampo Medina", "email": "manuela.ocampom@udea.edu.co"},
    {"documento": "1085325220", "nombre": "Germán Dario Zamudio Burbano", "email": "german.zamudio@udea.edu.co"},
    {"documento": "1090441696", "nombre": "Jesús David Díaz Mosquera", "email": "jesusd.diaz@udea.edu.co"},
    {"documento": "1152202153", "nombre": "María Carolina Aguilar Arango", "email": "mcarolina.aguilar@udea.edu.co"},
    {"documento": "1128457685", "nombre": "Oscar Mauricio Yepes Grajales", "email": "oscar.yepes@udea.edu.co"},
    {"documento": "1040747654", "nombre": "Santiago Alzate Giraldo", "email": "santiago.alzate11@udea.edu.co"},
    {"documento": "1052970426", "nombre": "Juan Armando Guzmán Mendoza", "email": "websjagm@gmail.com"},
    {"documento": "1037575729", "nombre": "Juan Ricardo Cadavid Castrillón", "email": "ricardo.cadavid@udea.edu.co"},
    {"documento": "1037655805", "nombre": "Juan Camilo López Bedoya", "email": "juan.lopez32@udea.edu.co"},
    {"documento": "1152200744", "nombre": "José Fernando Rojas Agudelo", "email": "josef.rojas@udea.edu.co"},
    {"documento": "8164627", "nombre": "Juan David Cuartas Ramírez", "email": "juand.cuartas@udea.edu.co"},
]


async def import_residents(dry_run: bool) -> Tuple[int, int]:
    """Import embedded residents list. Returns (created, skipped)."""
    created = 0
    skipped = 0
    errors = 0
    users_created = 0
    users_skipped = 0

    print(f"{'='*60}")
    print("RESIDENT IMPORT")
    print(f"{'='*60}")
    print(f"Mode: {'DRY-RUN (no changes)' if dry_run else 'REAL EXECUTION'}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total residents to process: {len(RESIDENTS_DATA)}")
    print(f"{'='*60}")

    # Dry run: do not connect to DB
    if dry_run:
        for i, row in enumerate(RESIDENTS_DATA, 1):
            raw_code = str(row.get("documento", "")).strip()
            raw_name = str(row.get("nombre", "")).strip()
            email = str(row.get("email", "")).strip()
            
            print(f"\n[{i}/{len(RESIDENTS_DATA)}] Processing: {raw_name}")
            print(f"  Code: {raw_code}")
            
            # Previous validations
            if not raw_code or not raw_name:
                print(f"  [SKIP] Empty code or name")
                skipped += 1
                continue
                
            # Validate code length according to schema (max 11 characters)
            if len(raw_code) > 11:
                print(f"  [SKIP] Code must have maximum 11 characters, current: {len(raw_code)}")
                skipped += 1
                continue
                
            # Validate name length (max 100 characters)
            if len(raw_name) > 100:
                print(f"  [SKIP] Name must have maximum 100 characters, current: {len(raw_name)}")
                skipped += 1
                continue
                
            initials = derive_initials(raw_name)
            medical_license = raw_code
            password = raw_code
            
            # Validate initials length (max 10 characters)
            if len(initials) > 10:
                print(f"  [SKIP] Initials must have maximum 10 characters, current: {len(initials)}")
                skipped += 1
                continue
            
            print(f"  [DRY-RUN] Would create resident: {raw_name}")
            print(f"    - Code: {raw_code}")
            print(f"    - Email: {email}")
            print(f"    - Initials: {initials}")
            print(f"    - Medical License: {medical_license}")
            print(f"    - Password: {password}")
            print(f"  [DRY-RUN] Would create user account: {raw_name}")
            print(f"    - Email: {email}")
            print(f"    - Role: resident")
            print(f"    - Password: {password} (will be encrypted)")
            print(f"    - Resident Code: {raw_code}")
            
            created += 1
            users_created += 1
        return created, skipped

    db = await get_database()
    try:
        service = ResidentService(db)

        for i, row in enumerate(RESIDENTS_DATA, 1):
            raw_code = str(row.get("documento", "")).strip()
            raw_name = str(row.get("nombre", "")).strip()
            email = str(row.get("email", "")).strip()

            print(f"\n[{i}/{len(RESIDENTS_DATA)}] Processing: {raw_name}")
            print(f"  Code: {raw_code}")

            try:
                # Previous validations
                if not raw_code or not raw_name:
                    print(f"  [SKIP] Empty code or name")
                    skipped += 1
                    continue
                    
                # Validate code length according to schema (max 11 characters)
                if len(raw_code) > 11:
                    print(f"  [SKIP] Code must have maximum 11 characters, current: {len(raw_code)}")
                    skipped += 1
                    continue

                # Validate name length (max 100 characters)
                if len(raw_name) > 100:
                    print(f"  [SKIP] Name must have maximum 100 characters, current: {len(raw_name)}")
                    skipped += 1
                    continue

                initials = derive_initials(raw_name)
                medical_license = raw_code
                password = raw_code

                # Validate initials length (max 10 characters)
                if len(initials) > 10:
                    print(f"  [SKIP] Initials must have maximum 10 characters, current: {len(initials)}")
                    skipped += 1
                    continue

                # Validate password length
                if len(password) < 6:
                    print(f"  [ERROR] Password is too short (min 6 chars): {password}")
                    errors += 1
                    continue
                
                payload = ResidentCreate(
                    resident_code=raw_code,
                    resident_name=raw_name,
                    initials=initials,
                    resident_email=email,
                    medical_license=medical_license,
                    is_active=True,
                    observations=None,
                    password=password
                )

                # Create resident (this also creates the user account automatically)
                await service.create_resident(payload)
                print(f"  [OK] Resident created successfully")
                print(f"    - Code: {raw_code}")
                print(f"    - Email: {email}")
                print(f"    - Initials: {initials}")
                print(f"    - Medical License: {medical_license}")
                print(f"    - Password: {password} (encrypted in database)")
                created += 1
                users_created += 1
                
            except ValueError as e:
                print(f"  [SKIP] Validation error: {str(e)}")
                skipped += 1
            except Exception as e:
                print(f"  [ERROR] Unexpected error: {type(e).__name__}: {str(e)}")
                # import traceback
                # print(f"  Traceback: {traceback.format_exc()}")
                errors += 1

        # Final summary
        print(f"\n{'='*60}")
        print("IMPORT SUMMARY")
        print(f"{'='*60}")
        print(f"Total processed: {len(RESIDENTS_DATA)}")
        print(f"Residents created: {created}")
        print(f"Residents skipped: {skipped}")
        print(f"Users created: {users_created}")
        print(f"Users skipped: {users_skipped}")
        print(f"Errors: {errors}")
        
        if dry_run:
            print(f"\n⚠️  DRY-RUN MODE: No changes were made to the database")
            print(f"To execute for real, run the script without --dry-run")
        else:
            print(f"\n✅ Import completed")
            
        print(f"{'='*60}")

        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Import system residents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 Scripts/9_import_residents.py --dry-run    # Only show what would be done
  python3 Scripts/9_import_residents.py              # Execute for real
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be done without executing real changes"
    )
    
    args = parser.parse_args()
    
    # Execute import
    asyncio.run(import_residents(dry_run=args.dry_run))


if __name__ == "__main__":
    main()

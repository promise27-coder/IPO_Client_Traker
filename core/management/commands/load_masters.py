import csv
from django.core.management.base import BaseCommand
from core.models import MasterClient
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Load Master Clients from a CSV file'

    def handle(self, *args, **kwargs):
        # 1. Tamari CSV file nu naam
        file_path = 'masters.csv' 
        
        # 2. Default Owner (Admin) shoધી lo
        # (Ahya assume kariye chiye k pehlo user admin che)
        admin_user = User.objects.first() 
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('Pehla ek Superuser/User banavo!'))
            return

        print("Importing data... Please wait.")

        # 3. File Read karvanu logic
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:  # <--- '-sig' add karyu
                reader = csv.DictReader(file)
                count = 0
                
                for row in reader:
                    # Duplicate check (Jo nickname pehlethi hoy to skip kare)
                    if not MasterClient.objects.filter(nickname=row['nickname'], owner=admin_user).exists():
                        MasterClient.objects.create(
                            owner=admin_user,
                            nickname=row['nickname'],
                            broker=row['broker'],
                            demat_acc=row.get('demat_acc', ''), # Jo khali hoy to blank
                            pan_number=row.get('pan_number', '')
                        )
                        count += 1
                        print(f"Added: {row['nickname']}")
                    else:
                        print(f"Skipped (Already exists): {row['nickname']}")

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} clients! 🚀'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{file_path}" na mali! Project folder ma muko.'))
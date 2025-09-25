from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from timb_dashboard.models import TobaccoGrade, TobaccoFloor, Merchant
from authentication.models import UserProfile
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Load initial data for the TIMB system'
    
    def handle(self, *args, **options):
        self.create_superuser()
        self.create_tobacco_grades()
        self.create_tobacco_floors()
        self.create_sample_users()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded initial data')
        )
    
    def create_superuser(self):
        """Create superuser if it doesn't exist"""
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@timb.co.zw',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                is_timb_staff=True
            )
            
            # Update the automatically created profile instead of creating a new one
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': 'TIMB',
                    'theme_preference': 'timb'
                }
            )
            
            if not created:
                profile.company_name = 'TIMB'
                profile.theme_preference = 'timb'
                profile.save()
            
            self.stdout.write('Created superuser: admin/admin123')
    
    def create_tobacco_grades(self):
        """Create standard tobacco grades"""
        grades_data = [
            # Strip Grades (A)
            ('A1', 'Strip Grade A1', 'STRIP', 5.50),
            ('A2', 'Strip Grade A2', 'STRIP', 5.00),
            ('A3', 'Strip Grade A3', 'STRIP', 4.50),
            
            # Leaf Grades (L)
            ('L1', 'Leaf Grade L1', 'LEAF', 4.20),
            ('L2', 'Leaf Grade L2', 'LEAF', 3.80),
            ('L3', 'Leaf Grade L3', 'LEAF', 3.40),
            ('L4', 'Leaf Grade L4', 'LEAF', 3.00),
            ('L5', 'Leaf Grade L5', 'LEAF', 2.60),
            
            # Lug Grades (X)
            ('X1', 'Lug Grade X1', 'LUG', 3.20),
            ('X2', 'Lug Grade X2', 'LUG', 2.80),
            ('X3', 'Lug Grade X3', 'LUG', 2.40),
            ('X4', 'Lug Grade X4', 'LUG', 2.00),
            ('X5', 'Lug Grade X5', 'LUG', 1.60),
            
            # Tip Grades (T)
            ('T1', 'Tip Grade T1', 'TIP', 2.50),
            ('T2', 'Tip Grade T2', 'TIP', 2.10),
            ('T3', 'Tip Grade T3', 'TIP', 1.70),
            
            # Smoking Grades (H)
            ('H1', 'Smoking Grade H1', 'SMOKING', 1.80),
            ('H2', 'Smoking Grade H2', 'SMOKING', 1.50),
            ('H3', 'Smoking Grade H3', 'SMOKING', 1.20),
            
            # Cutter Grades (C)
            ('C1', 'Cutter Grade C1', 'CUTTER', 2.20),
            ('C2', 'Cutter Grade C2', 'CUTTER', 1.90),
            
            # Scrap Grades (B)
            ('B1', 'Scrap Grade B1', 'SCRAP', 1.00),
            ('B2', 'Scrap Grade B2', 'SCRAP', 0.80),
        ]
        
        for grade_code, grade_name, category, base_price in grades_data:
            grade, created = TobaccoGrade.objects.get_or_create(
                grade_code=grade_code,
                defaults={
                    'grade_name': grade_name,
                    'category': category,
                    'base_price': base_price,
                    'description': f'Standard {category.lower()} grade tobacco'
                }
            )
            
            if created:
                self.stdout.write(f'Created grade: {grade_code}')
    
    def create_tobacco_floors(self):
        """Create tobacco auction floors"""
        floors_data = [
            ('Harare Tobacco Floors', 'Harare', 500000),
            ('Bulawayo Tobacco Floors', 'Bulawayo', 300000),
            ('Mutare Tobacco Floors', 'Mutare', 200000),
            ('Gweru Tobacco Floors', 'Gweru', 250000),
            ('Chinhoyi Tobacco Floors', 'Chinhoyi', 150000),
        ]
        
        for name, location, capacity in floors_data:
            floor, created = TobaccoFloor.objects.get_or_create(
                name=name,
                defaults={
                    'location': location,
                    'capacity': capacity,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created floor: {name}')
    
    def create_sample_users(self):
        """Create sample TIMB staff and merchants"""
        # Create TIMB staff
        if not User.objects.filter(username='timb_staff').exists():
            staff_user = User.objects.create_user(
                username='timb_staff',
                email='staff@timb.co.zw',
                password='staff123',
                first_name='TIMB',
                last_name='Staff',
                is_timb_staff=True
            )
            
            # Update the automatically created profile
            profile, created = UserProfile.objects.get_or_create(
                user=staff_user,
                defaults={
                    'company_name': 'TIMB',
                    'theme_preference': 'timb'
                }
            )
            
            if not created:
                profile.company_name = 'TIMB'
                profile.theme_preference = 'timb'
                profile.save()
            
            self.stdout.write('Created TIMB staff user: timb_staff/staff123')
        
        # Create sample merchant
        if not User.objects.filter(username='merchant_demo').exists():
            merchant_user = User.objects.create_user(
                username='merchant_demo',
                email='demo@merchant.com',
                password='merchant123',
                first_name='Demo',
                last_name='Merchant',
                is_merchant=True
            )
            
            # Update the automatically created profile
            profile, created = UserProfile.objects.get_or_create(
                user=merchant_user,
                defaults={
                    'company_name': 'Demo Tobacco Company',
                    'license_number': 'LIC-DEMO-001',
                    'theme_preference': 'merchant'
                }
            )
            
            if not created:
                profile.company_name = 'Demo Tobacco Company'
                profile.license_number = 'LIC-DEMO-001'
                profile.theme_preference = 'merchant'
                profile.save()
            
            # Create merchant record
            merchant, created = Merchant.objects.get_or_create(
                user=merchant_user,
                defaults={
                    'company_name': 'Demo Tobacco Company',
                    'license_number': 'LIC-DEMO-001',
                    'registration_date': '2024-01-01',
                    'status': 'ACTIVE',
                    'risk_score': 25.5
                }
            )
            
            if created:
                self.stdout.write('Created merchant user: merchant_demo/merchant123')
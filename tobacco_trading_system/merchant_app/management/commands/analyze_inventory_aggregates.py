from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from merchant_app.models import MerchantInventory, AggregatedGrade, AggregatedGradeComponent
from timb_dashboard.models import TobaccoGrade
import pandas as pd
import os
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Analyze merchant inventory against TIMB grades CSV to determine possible aggregate grades'

    def add_arguments(self, parser):
        parser.add_argument('--merchant_id', type=int, help='Specific merchant ID to analyze')
        parser.add_argument('--csv_path', type=str, default='../Aggregate grades and TIMB list.csv', help='Path to the CSV file')

    def handle(self, *args, **options):
        merchant_id = options['merchant_id']
        csv_path = options['csv_path']
        
        # Get the absolute path to the CSV file
        if not os.path.isabs(csv_path):
            csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), csv_path)
        
        self.stdout.write(self.style.SUCCESS("Starting inventory analysis for aggregate grades..."))
        
        try:
            # Load the CSV file
            self.stdout.write(f"Loading CSV file: {csv_path}")
            df = pd.read_csv(csv_path)
            self.stdout.write(f"CSV loaded successfully. Shape: {df.shape}")
            self.stdout.write(f"Columns: {df.columns.tolist()}")
            
            # Display first few rows to understand structure
            self.stdout.write("\nFirst 5 rows of CSV:")
            self.stdout.write(str(df.head()))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading CSV: {e}"))
            return
        
        # Get merchants to analyze
        if merchant_id:
            merchants = User.objects.filter(id=merchant_id, is_merchant=True)
        else:
            merchants = User.objects.filter(is_merchant=True)
        
        if not merchants.exists():
            self.stdout.write(self.style.ERROR("No merchants found to analyze"))
            return
        
        for merchant in merchants:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Analyzing inventory for: {merchant.company_name}")
            self.stdout.write(f"{'='*60}")
            
            # Get merchant's inventory
            inventory = MerchantInventory.objects.filter(merchant=merchant)
            
            if not inventory.exists():
                self.stdout.write(self.style.WARNING(f"No inventory found for {merchant.company_name}"))
                continue
            
            # Create inventory summary
            inventory_summary = {}
            total_inventory = Decimal('0')
            
            for item in inventory:
                grade_code = item.grade.grade_code
                quantity = item.available_quantity
                inventory_summary[grade_code] = {
                    'quantity': quantity,
                    'grade_name': item.grade.grade_name,
                    'category': item.grade.category,
                    'base_price': item.grade.base_price
                }
                total_inventory += quantity
            
            self.stdout.write(f"\nInventory Summary for {merchant.company_name}:")
            self.stdout.write(f"Total Inventory: {total_inventory} kg")
            self.stdout.write(f"Number of different grades: {len(inventory_summary)}")
            
            # Display inventory by category
            categories = {}
            for grade_code, data in inventory_summary.items():
                category = data['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append((grade_code, data))
            
            self.stdout.write(f"\nInventory by Category:")
            for category, grades in categories.items():
                category_total = sum(data['quantity'] for _, data in grades)
                self.stdout.write(f"  {category}: {category_total} kg ({len(grades)} grades)")
                
                # Show top grades in this category
                sorted_grades = sorted(grades, key=lambda x: x[1]['quantity'], reverse=True)
                for grade_code, data in sorted_grades[:3]:  # Top 3
                    self.stdout.write(f"    - {grade_code}: {data['quantity']} kg")
            
            # Analyze possible aggregate grades based on CSV
            self.stdout.write(f"\nAnalyzing possible aggregate grades from CSV...")
            
            # This is where we would analyze the CSV structure and match it with inventory
            # For now, let's create some sample aggregate grade suggestions
            
            self._suggest_aggregate_grades(merchant, inventory_summary, df)
    
    def _suggest_aggregate_grades(self, merchant, inventory_summary, csv_df):
        """Suggest possible aggregate grades based on inventory and CSV data"""
        
        self.stdout.write(f"\nSuggested Aggregate Grades for {merchant.company_name}:")
        
        # Group inventory by category and quality level
        category_groups = {}
        for grade_code, data in inventory_summary.items():
            category = data['category']
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append((grade_code, data))
        
        suggestions = []
        
        # Suggestion 1: Premium Blend (P1, L1, T1 grades)
        premium_grades = []
        for category in ['PRIMING', 'LEAF', 'TIP']:
            if category in category_groups:
                for grade_code, data in category_groups[category]:
                    if '1' in grade_code and data['quantity'] > 0:
                        premium_grades.append((grade_code, data))
        
        if len(premium_grades) >= 2:
            total_premium = sum(data['quantity'] for _, data in premium_grades)
            suggestions.append({
                'name': 'Premium Blend',
                'description': 'High-quality blend of Grade 1 tobacco',
                'grades': premium_grades,
                'total_quantity': total_premium,
                'estimated_price': self._calculate_blend_price(premium_grades)
            })
        
        # Suggestion 2: Standard Blend (P2, L2, T2 grades)
        standard_grades = []
        for category in ['PRIMING', 'LEAF', 'TIP']:
            if category in category_groups:
                for grade_code, data in category_groups[category]:
                    if '2' in grade_code and data['quantity'] > 0:
                        standard_grades.append((grade_code, data))
        
        if len(standard_grades) >= 2:
            total_standard = sum(data['quantity'] for _, data in standard_grades)
            suggestions.append({
                'name': 'Standard Blend',
                'description': 'Standard quality blend of Grade 2 tobacco',
                'grades': standard_grades,
                'total_quantity': total_standard,
                'estimated_price': self._calculate_blend_price(standard_grades)
            })
        
        # Suggestion 3: Category-specific blends
        for category, grades in category_groups.items():
            if len(grades) >= 2:
                total_category = sum(data['quantity'] for _, data in grades)
                suggestions.append({
                    'name': f'{category} Blend',
                    'description': f'Blend of {category} tobacco grades',
                    'grades': grades,
                    'total_quantity': total_category,
                    'estimated_price': self._calculate_blend_price(grades)
                })
        
        # Display suggestions
        for i, suggestion in enumerate(suggestions, 1):
            self.stdout.write(f"\n{i}. {suggestion['name']}")
            self.stdout.write(f"   Description: {suggestion['description']}")
            self.stdout.write(f"   Total Quantity: {suggestion['total_quantity']} kg")
            self.stdout.write(f"   Estimated Price: ${suggestion['estimated_price']:.2f}/kg")
            self.stdout.write(f"   Components:")
            
            for grade_code, data in suggestion['grades']:
                percentage = (data['quantity'] / suggestion['total_quantity']) * 100
                self.stdout.write(f"     - {grade_code}: {data['quantity']} kg ({percentage:.1f}%)")
        
        if not suggestions:
            self.stdout.write(self.style.WARNING("No aggregate grade suggestions found. Consider adding more diverse inventory."))
    
    def _calculate_blend_price(self, grades):
        """Calculate estimated price for a blend based on component grades"""
        if not grades:
            return 0.0
        
        total_quantity = sum(data['quantity'] for _, data in grades)
        if total_quantity == 0:
            return 0.0
        
        weighted_price = 0.0
        for grade_code, data in grades:
            weight = data['quantity'] / total_quantity
            price = float(data['base_price']) if data['base_price'] else 0.0
            weighted_price += weight * price
        
        return weighted_price


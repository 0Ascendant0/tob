from django.core.management.base import BaseCommand
from timb_dashboard.models import TobaccoGrade


class Command(BaseCommand):
    help = 'Load TIMB tobacco grades from Excel data'
    
    def handle(self, *args, **options):
        """Load all TIMB tobacco grades"""
        
        # Define all grades from Excel file
        grades_data = {
            # PRIMING GRADES (P)
            'PRIMING': [
                # P1 Series
                ('P1E', 'Priming Grade 1 Eastern'),
                ('P1EA', 'Priming Grade 1 Eastern A'),
                ('P1EV', 'Priming Grade 1 Eastern V'),
                ('P1EVA', 'Priming Grade 1 Eastern VA'),
                ('P1L', 'Priming Grade 1 Light'),
                ('P1LA', 'Priming Grade 1 Light A'),
                ('P1LF', 'Priming Grade 1 Light F'),
                ('P1LFA', 'Priming Grade 1 Light FA'),
                ('P1LV', 'Priming Grade 1 Light V'),
                ('P1LVA', 'Priming Grade 1 Light VA'),
                ('P1O', 'Priming Grade 1 Orange'),
                ('P1OA', 'Priming Grade 1 Orange A'),
                ('P1OF', 'Priming Grade 1 Orange F'),
                ('P1OFA', 'Priming Grade 1 Orange FA'),
                ('P1OV', 'Priming Grade 1 Orange V'),
                ('P1OVA', 'Priming Grade 1 Orange VA'),
                
                # P2 Series
                ('P2E', 'Priming Grade 2 Eastern'),
                ('P2ED', 'Priming Grade 2 Eastern D'),
                ('P2EA', 'Priming Grade 2 Eastern A'),
                ('P2EAD', 'Priming Grade 2 Eastern AD'),
                ('P2EAQ', 'Priming Grade 2 Eastern AQ'),
                ('P2EV', 'Priming Grade 2 Eastern V'),
                ('P2EQ', 'Priming Grade 2 Eastern Q'),
                ('P2EVD', 'Priming Grade 2 Eastern VD'),
                ('P2EVA', 'Priming Grade 2 Eastern VA'),
                ('P2EVQ', 'Priming Grade 2 Eastern VQ'),
                ('P2EG', 'Priming Grade 2 Eastern G'),
                ('P2EGA', 'Priming Grade 2 Eastern GA'),
                ('P2EGD', 'Priming Grade 2 Eastern GD'),
                ('P2EGQ', 'Priming Grade 2 Eastern GQ'),
                ('P2EK', 'Priming Grade 2 Eastern K'),
                ('P2EKA', 'Priming Grade 2 Eastern KA'),
                ('P2EKD', 'Priming Grade 2 Eastern KD'),
                ('P2EKQ', 'Priming Grade 2 Eastern KQ'),
                ('P2EKV', 'Priming Grade 2 Eastern KV'),
                ('P2EKG', 'Priming Grade 2 Eastern KG'),
                ('P2EY', 'Priming Grade 2 Eastern Y'),
                ('P2EYD', 'Priming Grade 2 Eastern YD'),
                
                ('P2L', 'Priming Grade 2 Light'),
                ('P2LD', 'Priming Grade 2 Light D'),
                ('P2LA', 'Priming Grade 2 Light A'),
                ('P2LAD', 'Priming Grade 2 Light AD'),
                ('P2LAQ', 'Priming Grade 2 Light AQ'),
                ('P2LF', 'Priming Grade 2 Light F'),
                ('P2LFA', 'Priming Grade 2 Light FA'),
                ('P2LV', 'Priming Grade 2 Light V'),
                ('P2LQ', 'Priming Grade 2 Light Q'),
                ('P2LVD', 'Priming Grade 2 Light VD'),
                ('P2LVA', 'Priming Grade 2 Light VA'),
                ('P2LVQ', 'Priming Grade 2 Light VQ'),
                ('P2LG', 'Priming Grade 2 Light G'),
                ('P2LGA', 'Priming Grade 2 Light GA'),
                ('P2LGD', 'Priming Grade 2 Light GD'),
                ('P2LGQ', 'Priming Grade 2 Light GQ'),
                ('P2LK', 'Priming Grade 2 Light K'),
                ('P2LKA', 'Priming Grade 2 Light KA'),
                ('P2LKD', 'Priming Grade 2 Light KD'),
                ('P2LKQ', 'Priming Grade 2 Light KQ'),
                ('P2LKV', 'Priming Grade 2 Light KV'),
                ('P2LKG', 'Priming Grade 2 Light KG'),
                ('P2LY', 'Priming Grade 2 Light Y'),
                ('P2LYD', 'Priming Grade 2 Light YD'),
                
                ('P20', 'Priming Grade 2 Orange'),
                ('P2OD', 'Priming Grade 2 Orange D'),
                ('P2OA', 'Priming Grade 2 Orange A'),
                ('P2OAD', 'Priming Grade 2 Orange AD'),
                ('P2OAQ', 'Priming Grade 2 Orange AQ'),
                ('P2OF', 'Priming Grade 2 Orange F'),
                ('P2OFA', 'Priming Grade 2 Orange FA'),
                ('P2OV', 'Priming Grade 2 Orange V'),
                ('P2OQ', 'Priming Grade 2 Orange Q'),
                ('P2OVD', 'Priming Grade 2 Orange VD'),
                ('P2OVA', 'Priming Grade 2 Orange VA'),
                ('P2OVQ', 'Priming Grade 2 Orange VQ'),
                ('P2OG', 'Priming Grade 2 Orange G'),
                ('P2OGA', 'Priming Grade 2 Orange GA'),
                ('P2OGD', 'Priming Grade 2 Orange GD'),
                ('P2OGQ', 'Priming Grade 2 Orange GQ'),
                ('P2OK', 'Priming Grade 2 Orange K'),
                ('P2OKA', 'Priming Grade 2 Orange KA'),
                ('P2OKD', 'Priming Grade 2 Orange KD'),
                ('P2OKQ', 'Priming Grade 2 Orange KQ'),
                ('P2OKV', 'Priming Grade 2 Orange KV'),
                ('P2OKG', 'Priming Grade 2 Orange KG'),
                ('P2OY', 'Priming Grade 2 Orange Y'),
                ('P2OYD', 'Priming Grade 2 Orange YD'),
                
                # P3, P4, P5 Series would continue similarly...
                # Adding key P3-P5 grades
                ('P3E', 'Priming Grade 3 Eastern'),
                ('P3L', 'Priming Grade 3 Light'),
                ('P30', 'Priming Grade 3 Orange'),
                ('P4E', 'Priming Grade 4 Eastern'),
                ('P4L', 'Priming Grade 4 Light'),
                ('P40', 'Priming Grade 4 Orange'),
                ('P5E', 'Priming Grade 5 Eastern'),
                ('P5L', 'Priming Grade 5 Light'),
                ('P50', 'Priming Grade 5 Orange'),
            ],
            
            # LUG GRADES (X)
            'LUG': [
                ('X1E', 'Lug Grade 1 Eastern'),
                ('X1EA', 'Lug Grade 1 Eastern A'),
                ('X1EV', 'Lug Grade 1 Eastern V'),
                ('X1EVA', 'Lug Grade 1 Eastern VA'),
                ('X1L', 'Lug Grade 1 Light'),
                ('X1LA', 'Lug Grade 1 Light A'),
                ('X1LF', 'Lug Grade 1 Light F'),
                ('XILFA', 'Lug Grade 1 Light FA'),
                ('X1LV', 'Lug Grade 1 Light V'),
                ('X1LVA', 'Lug Grade 1 Light VA'),
                ('X1O', 'Lug Grade 1 Orange'),
                ('X1OA', 'Lug Grade 1 Orange A'),
                ('X1OF', 'Lug Grade 1 Orange F'),
                ('XIOFA', 'Lug Grade 1 Orange FA'),
                ('X1OV', 'Lug Grade 1 Orange V'),
                ('X1OVA', 'Lug Grade 1 Orange VA'),
                
                ('X2E', 'Lug Grade 2 Eastern'),
                ('X2L', 'Lug Grade 2 Light'),
                ('X2O', 'Lug Grade 2 Orange'),
                ('X3E', 'Lug Grade 3 Eastern'),
                ('X3L', 'Lug Grade 3 Light'),
                ('X3O', 'Lug Grade 3 Orange'),
                ('X4E', 'Lug Grade 4 Eastern'),
                ('X4L', 'Lug Grade 4 Light'),
                ('X4O', 'Lug Grade 4 Orange'),
                ('X5E', 'Lug Grade 5 Eastern'),
                ('X5L', 'Lug Grade 5 Light'),
                ('X5O', 'Lug Grade 5 Orange'),
            ],
            
            # LEAF GRADES (L)
            'LEAF': [
                ('L1E', 'Leaf Grade 1 Eastern'),
                ('L1EA', 'Leaf Grade 1 Eastern A'),
                ('L1EV', 'Leaf Grade 1 Eastern V'),
                ('L1EVA', 'Leaf Grade 1 Eastern VA'),
                ('L1L', 'Leaf Grade 1 Light'),
                ('L1LA', 'Leaf Grade 1 Light A'),
                ('L1LF', 'Leaf Grade 1 Light F'),
                ('L1LFA', 'Leaf Grade 1 Light FA'),
                ('L1LV', 'Leaf Grade 1 Light V'),
                ('L1LVA', 'Leaf Grade 1 Light VA'),
                ('L1O', 'Leaf Grade 1 Orange'),
                ('L1OA', 'Leaf Grade 1 Orange A'),
                ('L1OF', 'Leaf Grade 1 Orange F'),
                ('L1OFA', 'Leaf Grade 1 Orange FA'),
                ('L1OV', 'Leaf Grade 1 Orange V'),
                ('L1OVA', 'Leaf Grade 1 Orange VA'),
                ('L1R', 'Leaf Grade 1 Red'),
                ('L1RA', 'Leaf Grade 1 Red A'),
                ('L1RF', 'Leaf Grade 1 Red F'),
                ('L1RFA', 'Leaf Grade 1 Red FA'),
                ('L1RV', 'Leaf Grade 1 Red V'),
                ('L1S', 'Leaf Grade 1 Stripped'),
                ('L1SA', 'Leaf Grade 1 Stripped A'),
                
                ('L2E', 'Leaf Grade 2 Eastern'),
                ('L2L', 'Leaf Grade 2 Light'),
                ('L2O', 'Leaf Grade 2 Orange'),
                ('L2R', 'Leaf Grade 2 Red'),
                ('L2S', 'Leaf Grade 2 Stripped'),
                ('L3E', 'Leaf Grade 3 Eastern'),
                ('L3L', 'Leaf Grade 3 Light'),
                ('L3O', 'Leaf Grade 3 Orange'),
                ('L3R', 'Leaf Grade 3 Red'),
                ('L3S', 'Leaf Grade 3 Stripped'),
                ('L4E', 'Leaf Grade 4 Eastern'),
                ('L4L', 'Leaf Grade 4 Light'),
                ('L4O', 'Leaf Grade 4 Orange'),
                ('L4R', 'Leaf Grade 4 Red'),
                ('L4S', 'Leaf Grade 4 Stripped'),
                ('L5E', 'Leaf Grade 5 Eastern'),
                ('L5L', 'Leaf Grade 5 Light'),
                ('L5O', 'Leaf Grade 5 Orange'),
                ('L5R', 'Leaf Grade 5 Red'),
                ('L5S', 'Leaf Grade 5 Stripped'),
            ],
            
            # TIP GRADES (T)
            'TIP': [
                ('T1E', 'Tip Grade 1 Eastern'),
                ('T1EA', 'Tip Grade 1 Eastern A'),
                ('T1EV', 'Tip Grade 1 Eastern V'),
                ('T1EVA', 'Tip Grade 1 Eastern VA'),
                ('T1L', 'Tip Grade 1 Light'),
                ('T1LA', 'Tip Grade 1 Light A'),
                ('T1LF', 'Tip Grade 1 Light F'),
                ('T1LFA', 'Tip Grade 1 Light FA'),
                ('T1LV', 'Tip Grade 1 Light V'),
                ('T1LVA', 'Tip Grade 1 Light VA'),
                ('T1O', 'Tip Grade 1 Orange'),
                ('T1OA', 'Tip Grade 1 Orange A'),
                ('T1OF', 'Tip Grade 1 Orange F'),
                ('T1OFA', 'Tip Grade 1 Orange FA'),
                ('T1OV', 'Tip Grade 1 Orange V'),
                ('T1OVA', 'Tip Grade 1 Orange VA'),
                ('T1R', 'Tip Grade 1 Red'),
                ('T1RA', 'Tip Grade 1 Red A'),
                ('T1RF', 'Tip Grade 1 Red F'),
                ('T1RFA', 'Tip Grade 1 Red FA'),
                ('T1RV', 'Tip Grade 1 Red V'),
                ('T1RVA', 'Tip Grade 1 Red VA'),
                ('T1S', 'Tip Grade 1 Stripped'),
                ('T1SA', 'Tip Grade 1 Stripped A'),
                
                ('T2E', 'Tip Grade 2 Eastern'),
                ('T2L', 'Tip Grade 2 Light'),
                ('T2O', 'Tip Grade 2 Orange'),
                ('T2R', 'Tip Grade 2 Red'),
                ('T2S', 'Tip Grade 2 Stripped'),
                ('T3E', 'Tip Grade 3 Eastern'),
                ('T3L', 'Tip Grade 3 Light'),
                ('T3O', 'Tip Grade 3 Orange'),
                ('T3R', 'Tip Grade 3 Red'),
                ('T3S', 'Tip Grade 3 Stripped'),
            ],
            
            # STRIP GRADES (A)
            'STRIP': [
                ('A1E', 'Strip Grade 1 Eastern'),
                ('A1EV', 'Strip Grade 1 Eastern V'),
                ('A1EVD', 'Strip Grade 1 Eastern VD'),
                ('A1EVA', 'Strip Grade 1 Eastern VA'),
                ('A1L', 'Strip Grade 1 Light'),
                ('A1LA', 'Strip Grade 1 Light A'),
                ('A1LF', 'Strip Grade 1 Light F'),
                ('A1LFA', 'Strip Grade 1 Light FA'),
                ('A1LV', 'Strip Grade 1 Light V'),
                ('A1LVD', 'Strip Grade 1 Light VD'),
                ('A1LVA', 'Strip Grade 1 Light VA'),
                ('A1O', 'Strip Grade 1 Orange'),
                ('A1OA', 'Strip Grade 1 Orange A'),
                ('A1OF', 'Strip Grade 1 Orange F'),
                ('A1OFA', 'Strip Grade 1 Orange FA'),
                ('A1OV', 'Strip Grade 1 Orange V'),
                ('A1OVD', 'Strip Grade 1 Orange VD'),
                ('A1OVA', 'Strip Grade 1 Orange VA'),
                ('A1R', 'Strip Grade 1 Red'),
                ('A1RA', 'Strip Grade 1 Red A'),
                ('A1RF', 'Strip Grade 1 Red F'),
                ('A1RFA', 'Strip Grade 1 Red FA'),
                ('A1RV', 'Strip Grade 1 Red V'),
                ('A1RVA', 'Strip Grade 1 Red VA'),
                ('A1S', 'Strip Grade 1 Stripped'),
                ('A1SA', 'Strip Grade 1 Stripped A'),
                
                ('A2E', 'Strip Grade 2 Eastern'),
                ('A2L', 'Strip Grade 2 Light'),
                ('A2O', 'Strip Grade 2 Orange'),
                ('A2R', 'Strip Grade 2 Red'),
                ('A2S', 'Strip Grade 2 Stripped'),
                ('A3E', 'Strip Grade 3 Eastern'),
                ('A3L', 'Strip Grade 3 Light'),
                ('A3O', 'Strip Grade 3 Orange'),
                ('A3R', 'Strip Grade 3 Red'),
                ('A3S', 'Strip Grade 3 Stripped'),
            ],
            
            # CUTTER GRADES (C)
            'CUTTER': [
                ('C1E', 'Cutter Grade 1 Eastern'),
                ('C1EA', 'Cutter Grade 1 Eastern A'),
                ('C1EV', 'Cutter Grade 1 Eastern V'),
                ('C2E', 'Cutter Grade 2 Eastern'),
                ('C2EA', 'Cutter Grade 2 Eastern A'),
                ('C2EV', 'Cutter Grade 2 Eastern V'),
                ('C3E', 'Cutter Grade 3 Eastern'),
                ('C3EA', 'Cutter Grade 3 Eastern A'),
                ('C3EV', 'Cutter Grade 3 Eastern V'),
                ('C4E', 'Cutter Grade 4 Eastern'),
                ('C4EA', 'Cutter Grade 4 Eastern A'),
                ('C4EV', 'Cutter Grade 4 Eastern V'),
                ('C5E', 'Cutter Grade 5 Eastern'),
                ('C5EA', 'Cutter Grade 5 Eastern A'),
                ('C5EV', 'Cutter Grade 5 Eastern V'),
            ],
            
            # SMOKING GRADES (H)
            'SMOKING': [
                ('H1L', 'Smoking Grade 1 Light'),
                ('H1O', 'Smoking Grade 1 Orange'),
                ('H1R', 'Smoking Grade 1 Red'),
                ('H2L', 'Smoking Grade 2 Light'),
                ('H2O', 'Smoking Grade 2 Orange'),
                ('H2R', 'Smoking Grade 2 Red'),
                ('H3L', 'Smoking Grade 3 Light'),
                ('H3O', 'Smoking Grade 3 Orange'),
                ('H3R', 'Smoking Grade 3 Red'),
                ('H4L', 'Smoking Grade 4 Light'),
                ('H4O', 'Smoking Grade 4 Orange'),
                ('H4R', 'Smoking Grade 4 Red'),
                ('H5L', 'Smoking Grade 5 Light'),
                ('H5O', 'Smoking Grade 5 Orange'),
                ('H5R', 'Smoking Grade 5 Red'),
            ],
            
            # SCRAP GRADES (B)
            'SCRAP': [
                ('B1', 'Scrap Grade 1'),
                ('B2', 'Scrap Grade 2'),
                ('B3', 'Scrap Grade 3'),
            ],
            
            # LOOSE LEAF
            'LOOSE_LEAF': [
                ('PTL', 'Primings Tied Leaf'),
                ('TTL', 'Tips Tied Leaf'),
            ],
            
            # REJECTION CODES
            'REJECTION': [
                ('BGR', 'Badly Handled (Too Wet/Dry)'),
                ('BMR', 'Mixed in the Hands'),
                ('DR', 'Soot'),
                ('MR', 'Mixed Hands'),
                ('RR', 'Oversized/Overweight Bale'),
                ('NDR', 'Undeclared Split'),
                ('SR', 'Stemrot'),
                ('NE', 'Nesting'),
                ('KR', 'Withdrawn for Funked'),
                ('WR', 'Withdrawn for Any Other Reason'),
                ('OR', 'Hot'),
            ],
            
            # DEFECT CODES
            'DEFECT': [
                ('BGD', 'Badly Handled (Too Wet/Dry)'),
                ('LD', 'Mouldy'),
                ('MXD', 'Mixed Bale'),
                ('DD', 'Declared Defects'),
                ('OT', 'Hot Bale'),
                ('SAD', 'Stemrot'),
                ('SD', 'Split Bale'),
                ('FD', 'Funked'),
            ],
        }
        
        # Base prices for different categories (USD per kg)
        base_prices = {
            'PRIMING': {1: 8.50, 2: 7.00, 3: 5.50, 4: 4.00, 5: 2.50},
            'LUG': {1: 7.50, 2: 6.00, 3: 4.50, 4: 3.00, 5: 2.00},
            'LEAF': {1: 9.00, 2: 7.50, 3: 6.00, 4: 4.50, 5: 3.00},
            'TIP': {1: 6.50, 2: 5.00, 3: 3.50},
            'STRIP': {1: 8.00, 2: 6.50, 3: 5.00},
            'CUTTER': {1: 5.00, 2: 4.50, 3: 4.00, 4: 3.50, 5: 3.00},
            'SMOKING': {1: 4.00, 2: 3.50, 3: 3.00, 4: 2.50, 5: 2.00},
            'SCRAP': {1: 1.50, 2: 1.00, 3: 0.50},
            'LOOSE_LEAF': None,
            'REJECTION': None,
            'DEFECT': None,
        }
        
        created_count = 0
        updated_count = 0
        
        for category, grades in grades_data.items():
            for grade_code, grade_name in grades:
                # Extract quality level from grade code
                quality_level = None
                if category in ['PRIMING', 'LUG', 'LEAF', 'CUTTER', 'SMOKING', 'SCRAP']:
                    # Extract number after the first letter
                    try:
                        quality_level = int(grade_code[1])
                    except (ValueError, IndexError):
                        if category == 'TIP':
                            try:
                                quality_level = int(grade_code[1])
                                if quality_level > 3:
                                    quality_level = None
                            except:
                                quality_level = None
                        elif category == 'STRIP':
                            try:
                                quality_level = int(grade_code[1])
                                if quality_level > 3:
                                    quality_level = None
                            except:
                                quality_level = None
                
                # Calculate base price
                base_price = 0
                if base_prices.get(category) and quality_level:
                    base_price = base_prices[category].get(quality_level, 0)
                
                # Set tradeable status
                is_tradeable = category not in ['REJECTION', 'DEFECT']
                
                # Create or update grade
                grade, created = TobaccoGrade.objects.get_or_create(
                    grade_code=grade_code,
                    defaults={
                        'grade_name': grade_name,
                        'category': category,
                        'quality_level': quality_level,
                        'base_price': base_price,
                        'minimum_price': base_price * 0.8 if base_price > 0 else 0,
                        'maximum_price': base_price * 1.5 if base_price > 0 else 0,
                        'is_tradeable': is_tradeable,
                        'is_active': True,
                        'specifications': {
                            'category_description': dict(TobaccoGrade.GRADE_CATEGORIES).get(category, ''),
                            'tradeable': is_tradeable,
                        }
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created grade: {grade_code} - {grade_name}')
                    )
                else:
                    # Update existing grade
                    grade.grade_name = grade_name
                    grade.category = category
                    grade.quality_level = quality_level
                    if grade.base_price == 0 and base_price > 0:
                        grade.base_price = base_price
                        grade.minimum_price = base_price * 0.8
                        grade.maximum_price = base_price * 1.5
                    grade.is_tradeable = is_tradeable
                    grade.save()
                    updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded TIMB grades: {created_count} created, {updated_count} updated'
            )
        )
        
        # Create sample floors
        floors_data = [
            ('Harare Tobacco Floors', 'Harare', 'Willowvale Industrial Area, Harare'),
            ('Marondera Tobacco Floors', 'Marondera', 'Industrial Area, Marondera'),
            ('Chinhoyi Tobacco Floors', 'Chinhoyi', 'Industrial Area, Chinhoyi'),
            ('Kadoma Tobacco Floors', 'Kadoma', 'Industrial Area, Kadoma'),
        ]
        
        from timb_dashboard.models import TobaccoFloor
        floor_count = 0
        
        for name, location, address in floors_data:
            floor, created = TobaccoFloor.objects.get_or_create(
                name=name,
                defaults={
                    'location': location,
                    'address': address,
                    'capacity': 10000,  # 10,000 bales capacity
                    'current_stock': 0,
                    'operating_hours': {
                        'monday': {'open': '07:00', 'close': '17:00'},
                        'tuesday': {'open': '07:00', 'close': '17:00'},
                        'wednesday': {'open': '07:00', 'close': '17:00'},
                        'thursday': {'open': '07:00', 'close': '17:00'},
                        'friday': {'open': '07:00', 'close': '17:00'},
                        'saturday': {'open': '08:00', 'close': '12:00'},
                        'sunday': 'closed'
                    },
                    'is_active': True,
                }
            )
            
            if created:
                floor_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created tobacco floor: {name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {floor_count} tobacco floors')
        )
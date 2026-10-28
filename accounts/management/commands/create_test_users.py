from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserDetails, Vendor


class Command(BaseCommand):
    help = 'Create test user and vendor credentials'

    def handle(self, *args, **options):
        # Regular Users
        users_data = [
            {
                'username': 'user1',
                'password': 'User@123',
                'email': 'user1@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'user_details': {
                    'phone': 9876543210,
                    'age': 28,
                    'house_no': 123,
                    'street': 'Main Street',
                    'landmark': 'Near Park',
                    'city': 'New York',
                    'state': 'NY',
                    'zipcode': 10001
                }
            },
            {
                'username': 'user2',
                'password': 'User@456',
                'email': 'user2@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'user_details': {
                    'phone': 9876543211,
                    'age': 25,
                    'house_no': 456,
                    'street': 'Second Avenue',
                    'landmark': 'Near Mall',
                    'city': 'Los Angeles',
                    'state': 'CA',
                    'zipcode': 90001
                }
            }
        ]

        # Create Regular Users
        self.stdout.write(self.style.WARNING('\n========== REGULAR USERS ==========\n'))
        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                UserDetails.objects.create(
                    user=user,
                    **user_data['user_details']
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created User: {user_data['username']}\n"
                        f"  Password: {user_data['password']}\n"
                        f"  Email: {user_data['email']}\n"
                    )
                )
            else:
                self.stdout.write(f"✗ User {user_data['username']} already exists\n")

        # Vendors
        vendors_data = [
            {
                'username': 'vendor1',
                'password': 'Vendor@123',
                'email': 'vendor1@example.com',
                'first_name': 'Ahmed',
                'last_name': 'Khan',
                'vendor_details': {
                    'vendor_name': 'Ahmed Food Business',
                    'restaurant_name': 'The Golden Fork',
                    'phone_num': 9876543220,
                    'address1': '789 Restaurant Blvd',
                    'address2': 'Suite 100',
                    'city': 'Chicago',
                    'state': 'IL',
                    'zipcode': 60601,
                    'gst_no': 'GST123456789'
                }
            },
            {
                'username': 'vendor2',
                'password': 'Vendor@456',
                'email': 'vendor2@example.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'vendor_details': {
                    'vendor_name': 'Priya Catering Services',
                    'restaurant_name': 'Spice Garden',
                    'phone_num': 9876543221,
                    'address1': '321 Culinary Lane',
                    'address2': 'Floor 2',
                    'city': 'Mumbai',
                    'state': 'MH',
                    'zipcode': 400001,
                    'gst_no': 'GST987654321'
                }
            }
        ]

        # Create Vendors
        self.stdout.write(self.style.WARNING('\n========== VENDORS (PENDING APPROVAL) ==========\n'))
        for vendor_data in vendors_data:
            if not User.objects.filter(username=vendor_data['username']).exists():
                user = User.objects.create_user(
                    username=vendor_data['username'],
                    password=vendor_data['password'],
                    email=vendor_data['email'],
                    first_name=vendor_data['first_name'],
                    last_name=vendor_data['last_name']
                )
                Vendor.objects.create(
                    user=user,
                    **vendor_data['vendor_details']
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created Vendor: {vendor_data['username']}\n"
                        f"  Password: {vendor_data['password']}\n"
                        f"  Email: {vendor_data['email']}\n"
                        f"  Restaurant: {vendor_data['vendor_details']['restaurant_name']}\n"
                        f"  Status: Pending Approval\n"
                    )
                )
            else:
                self.stdout.write(f"✗ Vendor {vendor_data['username']} already exists\n")

        # Approved Vendor
        self.stdout.write(self.style.WARNING('\n========== VENDORS (APPROVED) ==========\n'))
        approved_vendor_data = {
            'username': 'vendor_approved',
            'password': 'ApprovedVendor@123',
            'email': 'approved@example.com',
            'first_name': 'Rajesh',
            'last_name': 'Patel',
            'vendor_details': {
                'vendor_name': 'Rajesh Restaurant Group',
                'restaurant_name': 'Flavor Express',
                'phone_num': 9876543222,
                'address1': '654 Fast Food Court',
                'address2': 'Downtown',
                'city': 'Bangalore',
                'state': 'KA',
                'zipcode': 560001,
                'gst_no': 'GST111222333',
                'is_approved': True
            }
        }

        if not User.objects.filter(username=approved_vendor_data['username']).exists():
            user = User.objects.create_user(
                username=approved_vendor_data['username'],
                password=approved_vendor_data['password'],
                email=approved_vendor_data['email'],
                first_name=approved_vendor_data['first_name'],
                last_name=approved_vendor_data['last_name']
            )
            vendor_details = approved_vendor_data['vendor_details'].copy()
            is_approved = vendor_details.pop('is_approved')
            Vendor.objects.create(
                user=user,
                is_approved=is_approved,
                **vendor_details
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created Approved Vendor: {approved_vendor_data['username']}\n"
                    f"  Password: {approved_vendor_data['password']}\n"
                    f"  Email: {approved_vendor_data['email']}\n"
                    f"  Restaurant: {approved_vendor_data['vendor_details']['restaurant_name']}\n"
                    f"  Status: APPROVED ✓\n"
                )
            )
        else:
            self.stdout.write(f"✗ Vendor {approved_vendor_data['username']} already exists\n")

        self.stdout.write(self.style.SUCCESS('\n✓ Test data creation completed!\n'))

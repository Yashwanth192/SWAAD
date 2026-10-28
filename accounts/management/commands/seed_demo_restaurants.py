from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Menu, Vendor


LEGACY_FOOD_PHOTOS = {
    'food/idli_vada.avif',
    'food/47f0baa37a353990e7aa13c17dbe1843.jpg',
    'food/16f596c2f28b068cc2df93de7bd07a2a.jpg',
    'food/download.webp',
    'food/ven-pongal-1.webp',
}

RESTAURANT_PHOTOS = [
    f'restaurant_image/restaurant_scene_{index:02}.jpg'
    for index in range(1, 11)
]

MENU_PHOTOS = {
    'Breakfast': ['food/idli_vada.avif', 'food/ven-pongal-1.webp', 'food/menu_uttapam.jpg'],
    'Biryani': ['food/menu_biryani.jpg', 'food/menu_curry_rice.jpg', 'food/OIP_1.webp'],
    'Chaat': ['food/menu_chaat_vada.jpg', 'food/menu_chaat_street.jpg', 'food/menu_indian_snacks.jpg'],
    'Street Food': ['food/menu_chaat_street.jpg', 'food/menu_samosa.jpg', 'food/menu_indian_snacks.jpg'],
    'Dessert': ['food/menu_indian_sweets.jpg'],
    'Beverages': ['food/menu_masala_chai.jpg'],
    'Main Course': ['food/menu_curry_meal.jpg', 'food/menu_indian_spread.jpg', 'food/menu_curry_rice.jpg'],
    'Thali': ['food/menu_thali.jpg', 'food/menu_sadya.jpg'],
    'Starters': ['food/menu_samosa.jpg', 'food/menu_indian_snacks.jpg'],
    'Breads': ['food/menu_indian_spread.jpg', 'food/menu_thali.jpg'],
    'South Indian': ['food/47f0baa37a353990e7aa13c17dbe1843.jpg', 'food/menu_uttapam.jpg', 'food/ven-pongal-1.webp'],
}


RESTAURANTS = [
    {
        'username': 'demo_namma_dosa',
        'vendor_name': 'Namma Dosa Team',
        'restaurant_name': 'Namma Dosa House',
        'cuisine': 'South Indian',
        'address1': '12 Church Street',
        'delivery_time': '25-35 min',
        'delivery_fee': '25.00',
        'minimum_order': '99.00',
        'items': [
            ('Mysore Masala Dosa', '149.00', 'Breakfast', 'Crisp dosa with potato masala and red chutney.'),
            ('Ghee Podi Idli', '99.00', 'Breakfast', 'Soft idlis tossed in ghee and house podi.'),
            ('Medu Vada Sambar', '79.00', 'Breakfast', 'Golden lentil fritters served with sambar.'),
            ('Kesari Bath', '69.00', 'Dessert', 'Warm semolina sweet with saffron and cashews.'),
            ('Filter Coffee', '39.00', 'Beverages', 'Freshly brewed South Indian filter coffee.'),
        ],
    },
    {
        'username': 'demo_chaat_junction',
        'vendor_name': 'Chaat Junction Team',
        'restaurant_name': 'Chaat Junction',
        'cuisine': 'Street Food',
        'address1': '24 Indiranagar Main Road',
        'delivery_time': '20-30 min',
        'delivery_fee': '20.00',
        'minimum_order': '79.00',
        'items': [
            ('Pani Puri', '79.00', 'Chaat', 'Crisp puris with spiced water and potato filling.'),
            ('Dahi Puri', '109.00', 'Chaat', 'Puris topped with yogurt, chutneys and sev.'),
            ('Aloo Tikki Chaat', '99.00', 'Chaat', 'Crisp potato patties with tangy chutneys.'),
            ('Pav Bhaji', '149.00', 'Street Food', 'Buttery pav with slow-cooked vegetable bhaji.'),
            ('Masala Chaas', '49.00', 'Beverages', 'Chilled buttermilk with roasted cumin.'),
        ],
    },
    {
        'username': 'demo_mysore_tiffin',
        'vendor_name': 'Mysore Tiffin Team',
        'restaurant_name': 'Mysore Tiffin Co.',
        'cuisine': 'South Indian',
        'address1': '8 Jayanagar 4th Block',
        'delivery_time': '25-35 min',
        'delivery_fee': '25.00',
        'minimum_order': '89.00',
        'items': [
            ('Benne Masala Dosa', '159.00', 'Breakfast', 'Mysore-style dosa finished with cultured butter.'),
            ('Thatte Idli Set', '109.00', 'Breakfast', 'Two soft plate idlis with chutney and sambar.'),
            ('Bisibele Bath', '119.00', 'Main Course', 'Rice and lentils simmered with a house spice blend.'),
            ('Chow Chow Bath', '129.00', 'Breakfast', 'A comforting pairing of khara bath and kesari bath.'),
            ('Filter Coffee', '39.00', 'Beverages', 'Strong filter coffee poured fresh to order.'),
        ],
    },
    {
        'username': 'demo_malabar_coast',
        'vendor_name': 'Malabar Coast Team',
        'restaurant_name': 'Malabar Coast Kitchen',
        'cuisine': 'Kerala',
        'address1': '31 Koramangala 5th Block',
        'delivery_time': '30-40 min',
        'delivery_fee': '30.00',
        'minimum_order': '149.00',
        'items': [
            ('Appam with Vegetable Stew', '189.00', 'Main Course', 'Lacy appams with gently spiced coconut stew.'),
            ('Malabar Vegetable Biryani', '199.00', 'Biryani', 'Fragrant rice layered with vegetables and spices.'),
            ('Parotta with Vegetable Kurma', '169.00', 'Main Course', 'Flaky Kerala parotta with creamy vegetable kurma.'),
            ('Puttu Kadala Curry', '149.00', 'Breakfast', 'Steamed rice cakes with black chickpea curry.'),
            ('Fresh Lime Soda', '59.00', 'Beverages', 'Fresh lime with your choice of sweet or salted soda.'),
        ],
    },
    {
        'username': 'demo_punjabi_tandoor',
        'vendor_name': 'Punjabi Tandoor Team',
        'restaurant_name': 'Punjabi Tandoor House',
        'cuisine': 'North Indian',
        'address1': '17 HSR Layout Sector 2',
        'delivery_time': '30-40 min',
        'delivery_fee': '30.00',
        'minimum_order': '149.00',
        'items': [
            ('Paneer Tikka', '229.00', 'Starters', 'Char-grilled paneer with peppers and mint chutney.'),
            ('Dal Makhani', '199.00', 'Main Course', 'Slow-cooked black lentils finished with cream.'),
            ('Chole Kulche', '149.00', 'Main Course', 'Spiced chickpeas served with soft kulche.'),
            ('Butter Naan', '49.00', 'Breads', 'Tandoor-baked naan brushed with butter.'),
            ('Sweet Lassi', '69.00', 'Beverages', 'Chilled yogurt drink blended until smooth.'),
        ],
    },
    {
        'username': 'demo_millet_masala',
        'vendor_name': 'Millet and Masala Team',
        'restaurant_name': 'Millet & Masala',
        'cuisine': 'Healthy Indian',
        'address1': '6 Whitefield Main Road',
        'delivery_time': '25-35 min',
        'delivery_fee': '25.00',
        'minimum_order': '129.00',
        'items': [
            ('Ragi Dosa', '129.00', 'Breakfast', 'Crisp finger-millet dosa with coconut chutney.'),
            ('Millet Khichdi', '159.00', 'Main Course', 'Comforting millet and lentil khichdi with vegetables.'),
            ('Jowar Roti Thali', '189.00', 'Thali', 'Jowar rotis served with seasonal curry and sides.'),
            ('Foxtail Millet Pulao', '169.00', 'Main Course', 'Lightly spiced foxtail millet with vegetables.'),
            ('Jaggery Payasam', '79.00', 'Dessert', 'Traditional slow-simmered payasam sweetened with jaggery.'),
        ],
    },
]


class Command(BaseCommand):
    help = 'Add six approved demo restaurants and their menu items.'

    def handle(self, *args, **options):
        restaurant_count = 0
        item_count = 0
        photo_count = 0
        menu_photo_count = 0
        photo_index = 0
        menu_photo_indexes = {}

        for restaurant in RESTAURANTS:
            user, _ = User.objects.get_or_create(
                username=restaurant['username'],
                defaults={'email': f"{restaurant['username']}@example.test"},
            )
            user.set_unusable_password()
            user.save(update_fields=['password'])

            vendor, created = Vendor.objects.get_or_create(
                user=user,
                defaults={
                    'vendor_name': restaurant['vendor_name'],
                    'restaurant_name': restaurant['restaurant_name'],
                    'phone_num': 9876500000 + restaurant_count,
                    'address1': restaurant['address1'],
                    'city': 'Bengaluru',
                    'state': 'Karnataka',
                    'zipcode': 560001,
                    'cuisine': restaurant['cuisine'],
                    'delivery_time': restaurant['delivery_time'],
                    'delivery_fee': restaurant['delivery_fee'],
                    'minimum_order': restaurant['minimum_order'],
                    'is_approved': True,
                },
            )
            if created:
                restaurant_count += 1
            elif not vendor.is_approved:
                vendor.is_approved = True
                vendor.save(update_fields=['is_approved'])

            for name, price, category, description in restaurant['items']:
                _, created = Menu.objects.get_or_create(
                    vendor=vendor,
                    food_name=name,
                    defaults={
                        'price': price,
                        'category': category,
                        'description': description,
                        'is_available': True,
                    },
                )
                item_count += int(created)

        for vendor in Vendor.objects.filter(is_approved=True, restaurant_img='').order_by('id'):
            vendor.restaurant_img = RESTAURANT_PHOTOS[photo_index % len(RESTAURANT_PHOTOS)]
            vendor.save(update_fields=['restaurant_img'])
            photo_count += 1
            photo_index += 1

        for vendor in Vendor.objects.filter(is_approved=True).order_by('id'):
            if vendor.restaurant_img.name in LEGACY_FOOD_PHOTOS:
                vendor.restaurant_img = RESTAURANT_PHOTOS[photo_index % len(RESTAURANT_PHOTOS)]
                vendor.save(update_fields=['restaurant_img'])
                photo_count += 1
                photo_index += 1

        for menu in Menu.objects.filter(food_image='').order_by('vendor_id', 'id'):
            category_photos = MENU_PHOTOS.get(menu.category, MENU_PHOTOS['Main Course'])
            photo_index = menu_photo_indexes.get(menu.category, 0)
            menu.food_image = category_photos[photo_index % len(category_photos)]
            menu.save(update_fields=['food_image'])
            menu_photo_indexes[menu.category] = photo_index + 1
            menu_photo_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Added {restaurant_count} restaurants, {item_count} menu items, '
            f'{photo_count} restaurant photos, and {menu_photo_count} menu photos '
            '(existing demo records were kept).'
        ))
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from milk.models import MilkPrice, MilkEntry
from datetime import date
from decimal import Decimal

class DashboardRestructureTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create admin user
        self.admin_user = User.objects.create_user(username='adminuser', password='password123')
        admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin_user)
        admin_profile.is_admin = True
        admin_profile.save()

        # Create regular member
        self.member_user = User.objects.create_user(username='memberuser', password='password123')
        member_profile, _ = UserProfile.objects.get_or_create(user=self.member_user)
        member_profile.is_admin = False
        member_profile.save()

    def test_navbar_for_member_has_no_bill_or_price_links(self):
        """Member navbar must only have Home and Milk Logs (no Monthly Bill, Set Price, Price History)."""
        self.client.login(username='memberuser', password='password123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Milk Logs', content)
        self.assertIn('Home', content)
        # Should not have Monthly Bill link in header nav
        self.assertNotIn('Monthly Bill', content)
        self.assertNotIn('Set Price', content)
        self.assertNotIn('Price History', content)

    def test_navbar_for_admin_has_no_bill_or_price_links(self):
        """Admin navbar must only have Home, Dashboard, Milk Logs (no Monthly Bill, Set Price, Price History)."""
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Dashboard', content)
        self.assertIn('Milk Logs', content)
        self.assertIn('Home', content)
        # Should not have Monthly Bill, Set Price, Price History in navbar
        self.assertNotIn('Monthly Bill', content)
        self.assertNotIn('Set Price', content)
        self.assertNotIn('Price History', content)

    def test_member_cannot_access_dashboard_tabs(self):
        """Standard member should be redirected when trying to access any dashboard tab."""
        self.client.login(username='memberuser', password='password123')
        for url_name in ['admin_dashboard', 'dashboard_milk', 'dashboard_members']:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302)

    def test_admin_can_access_all_dashboard_tabs(self):
        """Admin can access Overview, Milk Management, and Members tabs."""
        self.client.login(username='adminuser', password='password123')

        # 1. Overview
        res1 = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res1.status_code, 200)
        self.assertContains(res1, 'Overview & KPIs')
        self.assertContains(res1, 'Milk Management')
        self.assertContains(res1, 'Household Members')

        # 2. Milk Management
        res2 = self.client.get(reverse('dashboard_milk'))
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, 'Set New Milk Price')
        self.assertContains(res2, 'Current Active Rates')
        self.assertContains(res2, 'Monthly Milk Billing Audit')
        self.assertContains(res2, 'Cow Milk Price History')
        self.assertContains(res2, 'Buffalo Milk Price History')

        # 3. Members
        res3 = self.client.get(reverse('dashboard_members'))
        self.assertEqual(res3.status_code, 200)
        self.assertContains(res3, 'Household Members & Permissions')
        self.assertContains(res3, 'adminuser')
        self.assertContains(res3, 'memberuser')

    def test_admin_can_set_milk_price_in_dashboard(self):
        """Admin can submit new milk price directly on the Milk Management tab."""
        self.client.login(username='adminuser', password='password123')
        post_data = {
            'milk_type': 'cow',
            'price_per_litre': '72.50',
            'effective_from_date': date.today().isoformat(),
        }
        response = self.client.post(reverse('dashboard_milk'), post_data)
        self.assertRedirects(response, reverse('dashboard_milk'))

        # Check that price is saved in database
        latest_price = MilkPrice.objects.filter(milk_type='cow').order_by('-id').first()
        self.assertIsNotNone(latest_price)
        self.assertEqual(latest_price.price_per_litre, Decimal('72.50'))

    def test_standalone_price_urls_redirect_to_dashboard_milk(self):
        """Old standalone price URLs redirect to dashboard_milk."""
        self.client.login(username='adminuser', password='password123')
        res_set = self.client.get(reverse('set_milk_price'))
        self.assertRedirects(res_set, reverse('dashboard_milk'))

        res_hist = self.client.get(reverse('milk_price_history'))
        self.assertRedirects(res_hist, reverse('dashboard_milk'))

    def test_aggregate_monthly_bill_page(self):
        """Aggregate monthly bill page loads with Milk section and placeholders for Kirana & Electricity."""
        self.client.login(username='memberuser', password='password123')
        response = self.client.get(reverse('aggregate_monthly_bill'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Household Monthly Bills')
        self.assertContains(response, 'Milk Bill')
        self.assertContains(response, 'Kirana & Grocery')
        self.assertContains(response, 'Electricity & Power')
        self.assertContains(response, 'Coming Soon')

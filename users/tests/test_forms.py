from django.contrib.auth import get_user_model
from django.test import TestCase

from users.forms import UserRegistrationForm, UserUpdateForm

User = get_user_model()


class UserRegistrationFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="existinguser", email="existing@example.com", password="existingpass123"
        )
        self.valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
            "terms": True,
        }

    def test_registration_form_valid_data(self):
        """Test form with valid data"""
        form = UserRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_duplicate_email(self):
        """Test form with duplicate email"""
        data = self.valid_data.copy()
        data["email"] = "existing@example.com"
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("This email is already registered", str(form.errors["email"]))

    def test_registration_form_invalid_email(self):
        """Test form with invalid email"""
        data = self.valid_data.copy()
        data["email"] = "invalid-email"
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_registration_form_password_mismatch(self):
        """Test form with mismatched passwords"""
        data = self.valid_data.copy()
        data["password2"] = "differentpass123"
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_registration_form_terms_not_accepted(self):
        """Test form when terms are not accepted"""
        data = self.valid_data.copy()
        data["terms"] = False
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("terms", form.errors)

    def test_registration_form_missing_required_fields(self):
        """Test form with missing required fields"""
        required_fields = ["username", "email", "password1", "password2", "terms"]
        for field in required_fields:
            data = self.valid_data.copy()
            data.pop(field)
            form = UserRegistrationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)


class UserUpdateFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )

    def test_update_form_valid_data(self):
        """Test form with valid data"""
        form = UserUpdateForm(data={"email": "new@example.com"}, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_update_form_duplicate_email(self):
        """Test form with duplicate email"""
        form = UserUpdateForm(data={"email": "other@example.com"}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("This email is already registered", str(form.errors["email"]))

    def test_update_form_same_email(self):
        """Test form when user keeps their current email"""
        form = UserUpdateForm(data={"email": "test@example.com"}, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_update_form_invalid_email(self):
        """Test form with invalid email"""
        form = UserUpdateForm(data={"email": "invalid-email"}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

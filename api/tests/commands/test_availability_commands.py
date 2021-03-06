from django.test import TestCase
from core.factories import *
from api.commands.availabilities import *
from core.models import *


class AddAvailabilityChangeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.resource = ResourceFactory()
        self.resource.location.house_admins.add(self.user)

    def test_that_command_with_valid_data_creates_an_availability(self):
        command = UpdateOrAddAvailabilityChange(self.user, start_date="4016-01-13", resource=self.resource.pk, quantity=2)

        if not command.execute():
            print command.result()
            self.assertTrue(False)

        availability = Availability.objects.filter(resource=self.resource).last()
        self.assertTrue(availability)
        self.assertEqual(availability.quantity, 2)
        self.assertEqual(availability.start_date, datetime.date(4016, 1, 13))

        expected_data = {'quantity': 2, 'resource': self.resource.pk, 'id': availability.pk, 'start_date': '4016-01-13'}
        self.assertEqual(command.result().serialize(), {'data': expected_data})

    def test_that_command_from_non_house_admin_fails(self):
        non_admin = UserFactory(username="samwise")
        command = UpdateOrAddAvailabilityChange(non_admin, start_date="4016-01-13", resource=self.resource.pk, quantity=2)
        self.assertFalse(command.execute())

    def test_that_command_with_missing_data_fails(self):
        command = UpdateOrAddAvailabilityChange(self.user, resource=self.resource.pk, quantity=2)

        self.assertFalse(command.execute())

        expected_data = {'errors': {'start_date': [u'This field is required.']}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_that_a_date_in_the_past_fails(self):
        command = UpdateOrAddAvailabilityChange(self.user, start_date="1016-01-13", resource=self.resource.pk, quantity=2)

        self.assertFalse(command.execute())

        expected_data = {'errors': {
            'start_date': [u'The start date must not be in the past']
        }}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_that_changing_availability_to_the_same_quantity_has_no_effect(self):
        availability = Availability.objects.create(start_date="4016-01-13", resource=self.resource, quantity=2)

        command = UpdateOrAddAvailabilityChange(self.user, start_date="4016-01-15", resource=self.resource.pk, quantity=2)
        self.assertTrue(command.execute())
        self.assertEqual(Availability.objects.count(), 1)

        expected_data = {'warnings': {'quantity': [u'This is not a change from the previous availability']}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_setting_availability_to_another_quantity_updates_a_record_on_that_date(self):
        availability = Availability.objects.create(start_date="4016-01-13", resource=self.resource, quantity=2)

        command = UpdateOrAddAvailabilityChange(self.user, start_date="4016-01-13", resource=self.resource.pk, quantity=3)
        self.assertTrue(command.execute())
        self.assertEqual(Availability.objects.count(), 1)

        expected_data = {'quantity': 3, 'resource': self.resource.pk, 'id': availability.pk, 'start_date': '4016-01-13'}
        self.assertEqual(command.result().serialize(), {'data': expected_data})

    def test_cannot_udpate_availability_in_the_past(self):
        availability = Availability.objects.create(start_date="1016-01-13", resource=self.resource, quantity=2)

        command = UpdateOrAddAvailabilityChange(self.user, start_date="1016-01-13", resource=self.resource.pk, quantity=3)
        self.assertFalse(command.execute())
        self.assertEqual(Availability.objects.count(), 1)

        expected_data = {'errors': {'start_date': [u'The start date must not be in the past']}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_that_update_command_from_non_house_admin_fails(self):
        availability = Availability.objects.create(start_date="4016-01-13", resource=self.resource, quantity=2)

        non_admin = UserFactory(username="samwise")
        command = UpdateOrAddAvailabilityChange(non_admin, start_date="4016-01-13", resource=self.resource.pk, quantity=3)
        self.assertFalse(command.execute())


class DeleteAvailabilityChangeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.resource = ResourceFactory()
        self.resource.location.house_admins.add(self.user)

    def expect_deleted_availabilities(self, expected_ids, remaining=0):
        self.assertTrue(self.command.execute())
        self.assertEqual(Availability.objects.count(), remaining)
        expected_data = {'data': {'deleted': {'availabilities': expected_ids}}}
        self.assertEqual(self.command.result().serialize(), expected_data)

    def test_that_command_from_non_house_admin_fails(self):
        availability = Availability.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)
        non_admin = UserFactory(username="samwise")
        self.command = DeleteAvailabilityChange(non_admin, availability=availability)
        self.assertFalse(self.command.execute())

    def test_cant_delete_availability_in_the_past(self):
        availability = Availability.objects.create(start_date=datetime.date(1016, 1, 13), resource=self.resource, quantity=2)

        command = DeleteAvailabilityChange(self.user, availability=availability)
        self.assertFalse(command.execute())
        self.assertEqual(Availability.objects.count(), 1)
        expected_data = {'errors': {'start_date': [u'The start date must not be in the past']}}
        self.assertEqual(command.result().serialize(), expected_data)

    def test_can_delete_availability_in_the_future(self):
        availability = Availability.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)
        self.command = DeleteAvailabilityChange(self.user, availability=availability)
        self.expect_deleted_availabilities([availability.pk])

    def test_deleting_availability_also_deletes_next_one_if_it_is_the_same_as_previous(self):
        previous_availability = Availability.objects.create(start_date=datetime.date(4016, 1, 12), resource=self.resource, quantity=3)
        availability = Availability.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)
        next_availability = Availability.objects.create(start_date=datetime.date(4016, 1, 14), resource=self.resource, quantity=3)
        self.command = DeleteAvailabilityChange(self.user, availability=availability)
        self.expect_deleted_availabilities([availability.pk, next_availability.pk], remaining=1)

    def test_deleting_availability_doesnt_deletes_next_one_if_it_different_to_previous(self):
        previous_availability = Availability.objects.create(start_date=datetime.date(4016, 1, 12), resource=self.resource, quantity=4)
        availability = Availability.objects.create(start_date=datetime.date(4016, 1, 13), resource=self.resource, quantity=2)
        next_availability = Availability.objects.create(start_date=datetime.date(4016, 1, 14), resource=self.resource, quantity=3)
        self.command = DeleteAvailabilityChange(self.user, availability=availability)
        self.expect_deleted_availabilities([availability.pk], remaining=2)

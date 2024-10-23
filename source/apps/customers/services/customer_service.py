# services/customer_service.py

from django.contrib.auth.models import User

from ..models import Customer, CustomerInteraction, LoyaltyProgram


class CustomerService:
    @staticmethod
    def create_customer(
        first_name, last_name, email, phone_number, is_loyalty_member=False
    ):
        """Creates a new customer and returns it."""
        user = User.objects.create(
            username=email, first_name=first_name, last_name=last_name, email=email
        )
        customer = Customer.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            is_loyalty_member=is_loyalty_member,
        )
        return customer

    @staticmethod
    def update_customer(customer_id, data):
        """Updates customer data."""
        customer = Customer.objects.get(id=customer_id)
        for key, value in data.items():
            setattr(customer, key, value)
        customer.save()
        return customer

    @staticmethod
    def add_interaction(customer, interaction_type, notes):
        """Adds a customer interaction."""
        return CustomerInteraction.objects.create(
            customer=customer, interaction_type=interaction_type, notes=notes
        )

    @staticmethod
    def enroll_in_loyalty_program(customer):
        """Enrolls a customer in the loyalty program if not already enrolled."""
        if not customer.is_loyalty_member:
            customer.is_loyalty_member = True
            LoyaltyProgram.objects.create(customer=customer)
            customer.save()
        return customer

    @staticmethod
    def add_loyalty_points(customer, points):
        """Adds loyalty points to a customer."""
        if customer.is_loyalty_member:
            loyalty_program = customer.loyalty_program
            loyalty_program.points += points
            loyalty_program.save()
        return loyalty_program

    @staticmethod
    def change_tier(customer, new_tier):
        loyalty_program = LoyaltyProgram.objects.get(customer=customer)
        loyalty_program.tier = new_tier
        loyalty_program.save()
        return loyalty_program

    @staticmethod
    def remove_loyalty_points(customer, points):
        """Removes loyalty points from a customer."""
        if customer.is_loyalty_member:
            loyalty_program = customer.loyalty_program
            loyalty_program.points = max(loyalty_program.points - points, 0)
            loyalty_program.save()
        return loyalty_program

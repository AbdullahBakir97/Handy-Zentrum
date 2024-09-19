# controllers/customer_controller.py

from ..services.customer_service import CustomerService

class CustomerController:
    @staticmethod
    def create_customer_with_loyalty(data):
        """Creates a customer and enrolls them in the loyalty program."""
        customer = CustomerService.create_customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data['phone_number'],
            is_loyalty_member=data.get('is_loyalty_member', False)
        )
        if data.get('is_loyalty_member', False):
            CustomerService.enroll_in_loyalty_program(customer)
        return customer

    @staticmethod
    def handle_customer_interaction(customer_id, interaction_type, notes):
        """Handles a customer interaction and updates loyalty points if applicable."""
        customer = CustomerService.update_customer(customer_id, {'interaction_type': interaction_type})
        return CustomerService.add_interaction(customer, interaction_type, notes)

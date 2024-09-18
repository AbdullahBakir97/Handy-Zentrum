from .models import Customer, LoyaltyProgram

class LoyaltyService:
    @staticmethod
    def add_loyalty_points(customer, points):
        loyalty_program = LoyaltyProgram.objects.get(customer=customer)
        loyalty_program.points += points
        loyalty_program.save()
        return loyalty_program

    @staticmethod
    def change_tier(customer, new_tier):
        loyalty_program = LoyaltyProgram.objects.get(customer=customer)
        loyalty_program.tier = new_tier
        loyalty_program.save()
        return loyalty_program

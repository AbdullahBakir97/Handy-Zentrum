from .models import Shipment, ReturnShipment
from .services import ShipmentService, ReturnService
from .utils import adjust_stock_level


class ShipmentController:
    def create_shipment(self, product, quantity, origin, destination):
        shipment = ShipmentService().create_shipment(product, quantity, origin, destination)
        adjust_stock_level(product.inventory_records.first(), quantity, 'remove')
        return shipment
    
    
        
        
class ReturnController:
    def handle_return(self, shipment, reason):
        return_shipment = ReturnService().initiate_return(shipment, reason)
        adjust_stock_level(shipment.product.inventory_records.first(), shipment.quantity, 'add')
        return return_shipment


    
    
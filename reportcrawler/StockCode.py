class StockCode:
    def __init__(self, serial_no: str = None, plate: str = None):
        assert serial_no is not None and len(serial_no) > 0
        assert plate is not None and len(plate) > 0
        self.serial_no = serial_no or '000000'
        self.plate = plate.lower() or 'non'

    def get_serial_no(self):
        return self.serial_no

    def get_plate(self):
        return self.plate

    def __str__(self):
        return "%s.%s" % (self.serial_no, self.plate)
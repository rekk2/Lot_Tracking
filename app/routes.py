from flask import Blueprint, render_template, request, jsonify
from .models import Inventory
from . import db
from .printer import generate_zpl, send_zpl_to_printer
import os
import datetime
import qrcode
import csv

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/receive')
def receive():
    recent_items = Inventory.query.order_by(Inventory.id.desc()).limit(5).all()
    return render_template('receive.html', recent_items=recent_items)

@main.route('/inspect')
def inspect():
    return render_template('inspect.html')

@main.route('/transfer')
def transfer():
    return render_template('transfer.html')

@main.route('/pick')
def pick():
    return render_template('pick.html')

def get_description_from_csv(part_number):
    csv_path = os.path.join(os.path.dirname(__file__), 'static', 'item_attributes.csv')
    print(f"Looking for part number: {part_number}")  # Debug print to show the part number being searched for
    print(f"CSV path: {csv_path}")  # Debug print to check CSV path
    try:
        with open(csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            print(f"CSV headers: {reader.fieldnames}")  # Debug print to check headers
            for row in reader:
                print(f"CSV row: {row}")  # Debug print to see each row
                if row['Part Number'] == part_number:
                    description = row['Description']
                    print(f"Description found for part {part_number}: {description}")  # Debug print
                    return description
    except FileNotFoundError:
        print("CSV file not found.")
    except KeyError as e:
        print(f"CSV format is incorrect. Missing key: {e}")
    return ""

@main.route('/api/receive', methods=['POST'])
def receive_inventory():
    data = request.get_json()
    print(f"Received data: {data}")  # Debug print

    inspection_status = 'INQC' if data.get('inspection_flag') else 'RECEIVED'
    location = 'RECV RACK 01'

    # Generate a sequential QR code ID
    last_inventory = Inventory.query.order_by(Inventory.id.desc()).first()
    qr_code_id = last_inventory.id + 1 if last_inventory else 1

    # Get description from CSV
    description = get_description_from_csv(data['part_number'])
    print(f"Fetched description: {description}")  # Debug print

    new_inventory = Inventory(
        part_number=data['part_number'],
        lot_number=data['lot_number'],
        receipt_date=datetime.datetime.strptime(data['receipt_date'], '%Y-%m-%d'),
        quantity=data['quantity'],
        location=location,
        inspection_status=inspection_status,
        qr_code_id=qr_code_id,
        description=description
    )
    db.session.add(new_inventory)
    db.session.commit()
    print(f"Inventory item added: {new_inventory}")  # Debug print

    # Ensure the static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')

    # Generate the QR code with the serialized ID
    qr_data = f"ID: {qr_code_id}, PN: {data['part_number']}, RD: {data['receipt_date']}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(f"static/{qr_code_id}.png")
    print(f"QR code generated and saved: static/{qr_code_id}.png")  # Debug print

    # Generate ZPL
    zpl_code = generate_zpl(
        part_number=data['part_number'],
        description=description,
        qr_code_id=qr_code_id,
        receipt_date=data['receipt_date'],
        quantity=data['quantity'],
        lot_number=data['lot_number']
    )
    print(f"Generated ZPL: {zpl_code}")  # Debug print
    
    return jsonify({'message': 'Inventory received and assigned location', 'qr_code_id': qr_code_id, 'zpl_code': zpl_code}), 201

@main.route('/api/reprint', methods=['POST'])
def reprint_label():
    data = request.get_json()
    inventory_item = Inventory.query.filter_by(qr_code_id=data['qr_code_id']).first()
    if inventory_item:
        # Fetch the description from the CSV
        description = get_description_from_csv(inventory_item.part_number)
        print(f"Description for reprint: {description}")  # Debug print
        zpl_code = generate_zpl(
            inventory_item.part_number,
            description,
            inventory_item.qr_code_id,
            inventory_item.receipt_date,
            inventory_item.quantity,
            inventory_item.lot_number
        )
        print(f"Generated ZPL for reprint: {zpl_code}")  # Debug print
        send_zpl_to_printer(zpl_code)  # Send to printer via TCP/IP
        return jsonify({'message': 'Label reprinted successfully'}), 200
    return jsonify({'error': 'Item not found'}), 404

@main.route('/api/print', methods=['POST'])
def print_label():
    data = request.get_json()
    zpl_code = data['zpl_code']
    print(f"Generated ZPL for print: {zpl_code}")  # Debug print
    send_zpl_to_printer(zpl_code)  # Send to printer via TCP/IP
    return jsonify({'message': 'Label printed successfully'}), 200

@main.route('/api/inspect', methods=['POST'])
def inspect_inventory():
    data = request.get_json()
    inventory_item = Inventory.query.filter_by(id=data['id']).first()
    if inventory_item and inventory_item.inspection_status == 'INQC':
        inventory_item.location = 'INQC2STK'
        inventory_item.inspection_status = 'INQC2STK'
        db.session.commit()
        return jsonify({'message': 'Part moved to INQC2STK'}), 200
    return jsonify({'error': 'Invalid operation or item not found'}), 400

@main.route('/api/complete_inspection', methods=['POST'])
def complete_inspection():
    data = request.get_json()
    inventory_item = Inventory.query.filter_by(id=data['id']).first()
    if inventory_item and inventory_item.inspection_status == 'INQC2STK':
        inventory_item.location = get_default_location(inventory_item.part_number)
        inventory_item.inspection_status = 'STOCK'
        db.session.commit()
        return jsonify({'message': 'Part moved to stock location'}), 200
    return jsonify({'error': 'Invalid operation or item not found'}), 400

def get_default_location(part_number):
    last_inventory = Inventory.query.filter_by(part_number=part_number, inspection_status='STOCK').order_by(Inventory.receipt_date.desc()).first()
    return last_inventory.location if last_inventory else 'DEFAULT_LOCATION'

@main.route('/api/transfer', methods=['POST'])
def transfer_inventory():
    data = request.get_json()
    inventory_item = Inventory.query.filter_by(id=data['id']).first()
    if inventory_item and inventory_item.inspection_status == 'STOCK':
        inventory_item.location = data['new_location']
        db.session.commit()
        return jsonify({'message': 'Part transferred to new location'}), 200
    return jsonify({'error': 'Invalid operation or item not found'}), 400

@main.route('/api/pick', methods=['POST'])
def pick_inventory():
    data = request.get_json()
    inventory_item = Inventory.query.filter_by(qr_code_id=data['qr_code_id']).first()
    if inventory_item and inventory_item.inspection_status == 'STOCK':
        if inventory_item.quantity >= data['quantity']:
            inventory_item.quantity -= data['quantity']
            if inventory_item.quantity == 0:
                db.session.delete(inventory_item)
            db.session.commit()
            return jsonify({'message': 'Pick validated and inventory updated'}), 200
        else:
            return jsonify({'error': 'Insufficient quantity'}), 400
    return jsonify({'error': 'Invalid operation or item not found'}), 400

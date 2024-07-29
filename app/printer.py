import socket

default_printer_ip = "192.168.50.12"

def generate_zpl(part_number, description, qr_code_id, receipt_date, quantity, lot_number):
    zpl_template = f"""
    ^XA
    ^PW609
    ^LL0406
    ^LS0
    ^FT18,95^A0N,80,80^FD{part_number}^FS
    ^FT489,37^A0N,28,21^FD{qr_code_id}^FS
    ^FT18,150^A0N,28,28^FB570,2,0,L,0^FD{description}^FS
    ^FT18,206^A0N,28,28^FB380,0,0,L,0^FD{description}^FS
    ^FT25,250^A0N,28,28^FDLot number: {lot_number}^FS
    ^FT25,300^A0N,28,28^FDRecv Date: {receipt_date}^FS
    ^FT25,350^A0N,28,28^FDQuantity: {quantity}^FS
    ^FO373,160^BQN,2,10^FDQA,{qr_code_id}^FS
    ^PQ1,0,1,Y^XZ
    """
    return zpl_template



def send_zpl_to_printer(zpl_code, printer_ip=default_printer_ip):
    try:
        print(f"Connecting to printer at {printer_ip}:9100")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((printer_ip, 9100))
        sock.sendall(zpl_code.encode())
        sock.close()
        print("ZPL sent to printer successfully.")
    except Exception as e:
        print(f"Failed to print to TCP/IP printer at {printer_ip}: {e}")
        raise Exception(f"Failed to print to TCP/IP printer at {printer_ip}: {e}")


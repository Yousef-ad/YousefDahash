# Network_handler.py network handler
import serial
import sys
import serial.tools.list_ports
import serial




def get_arduino_port():
    arduino_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'Arduino' in p.description
    ]
    if arduino_ports:
        try:
            arduino_port = serial.Serial(arduino_ports[0], 9600)
            print(f"Arduino connected at port: {arduino_ports[0]}")
            return arduino_port
        except serial.SerialException as e:
            print(f"Serial Error: {e}")
            return None
    else:
        return None

def int_to_ascii(input_int):
    # Define ASCII lookup table
    ascii_table = {
        0: 0x30, 1: 0x31, 2: 0x32, 3: 0x33, 4: 0x34,
        5: 0x35, 6: 0x36, 7: 0x37, 8: 0x38, 9: 0x39
    }
    
    # Convert input int to ASCII
    if 0 <= input_int <= 9:
        return ascii_table[input_int]
    else:
        return None  # Return None for out of range values

def send_TOR(command, TOR, arduino):
    try:
        if arduino is not None:
            # Construct packet for set TOR command
            if command == 'SET TOR':
                if TOR > 9:
                    digit1 = TOR // 10
                    digit2 = TOR % 10
                    hex_value1 = int_to_ascii(digit1)
                    hex_value2 = int_to_ascii(digit2)
                    
                    # Construct packet
                    packet = bytearray()
                    packet.extend([0x53, 0x45, 0x54, 0x20, 0x54, 0x4F, 0x52, 0x3A, 0x20, hex_value1, hex_value2, 0x0A])
                    print(f"packet: {packet.decode('utf-8')}")
                else:
                    hex_value = int_to_ascii(TOR)
                    packet = bytearray([0x53, 0x45, 0x54, 0x20, 0x54, 0x4F, 0x52, 0x3A, 0x20, hex_value, 0x0A])
                    print(f"packet: {packet.decode('utf-8')}")
            
            # Construct packet for reset command
            elif command == 'reset':
                packet = bytearray([0x52, 0x45, 0x53, 0x45, 0x54, 0x3A, 0x0A])
                print(f"packet: {packet.decode('utf-8')}")
            
            # Construct packet for SET TOG command (added elif here)
            elif command == 'SET TOG':
                if TOR > 9:
                    digit1 = TOR // 10
                    digit2 = TOR % 10
                    hex_value1 = int_to_ascii(digit1)
                    hex_value2 = int_to_ascii(digit2)
                    
                    # Construct packet
                    packet = bytearray()
                    packet.extend([0x53, 0x45, 0x54, 0x20, 0x54, 0x4F, 0x47, 0x3A, 0x20, hex_value1, hex_value2, 0x0A])
                    print(f"packet: {packet.decode('utf-8')}")
                else:
                    hex_value = int_to_ascii(TOR)
                    packet = bytearray([0x53, 0x45, 0x54, 0x20, 0x54, 0x4F, 0x47, 0x3A, 0x20, hex_value, 0x0A])
                    print(f"packet: {packet.decode('utf-8')}")
            
            arduino.write(packet)
            print(f"Sent {command} command to Arduino")
            
        else:
            print("Arduino is not connected.")
    except serial.SerialException as e:
        print(f"Serial Error: {e}", file=sys.stderr)
    except IOError as e:
        print(f"Arduino Error: {e}", file=sys.stderr)




if __name__ == "__main__":
    # Assuming you have initialized 'arduino' and 'TOR' variables somewhere in your script
    command = input("Enter command (set TOR/reset): ")
    send_TOR(command, TOR, arduino)


# (c) 2024 Pei-Ying Lin and Alex McLean

# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# <http://www.gnu.org/licenses/>.

# Related work:
# Shanel Wu, Xavier A Corr, Xi Gao, Sasha De Koninck, Robin Bowers,
# and Laura Devendorf. 2024. Loom Pedals: Retooling Jacquard Weaving
# for Improvisational Design Workflows. In Proceedings of the
# Eighteenth International Conference on Tangible, Embedded, and
# Embodied Interaction (TEI '24). Association for Computing Machinery,
# New York, NY, USA, Article 10,
# 1–16. https://doi.org/10.1145/3623509.3633358

# Lea Albaugh, Scott E. Hudson, Lining Yao, and Laura
# Devendorf. 2020. Investigating Underdetermination Through
# Interactive Computational Handweaving. In Proceedings of the 2020
# ACM Designing Interactive Systems Conference (DIS '20). Association for Computing Machinery, New York, NY, USA, 1033–1046. https://doi.org/10.1145/3357236.3395538

import socket, re, select, time

class TC2:
    tc2_ip = "192.168.0.100"
    tc2_port = 62000
    modules = [[5, 3, 1], [4, 2, 0]]
    module_count = sum(map(len, modules))
    module_index = [136, 138, 88, 90, 92, 232, 234, 140, 142, 128, 184,
                    186, 94, 80, 82, 236, 238, 130, 132, 134, 188, 190, 84, 86, 224, 226,
                    120, 122, 124, 176, 178, 72, 74, 76, 228, 230, 126, 112, 114, 180,
                    182, 78, 64, 66, 216, 218, 116, 118, 104, 168, 170, 68, 70, 56, 220,
                    222, 106, 96, 98, 172, 174, 58, 48, 50, 208, 210, 100, 102, 160, 162,
                    52, 54, 40, 212, 214, 137, 139, 141, 164, 166, 42, 44, 46, 200, 202,
                    143, 129, 131, 152, 154, 32, 34, 36, 192, 194, 133, 135, 121, 144,
                    146, 38, 24, 26, 196, 198, 123, 125, 127, 148, 150, 28, 30, 233, 235,
                    113, 115, 117, 185, 187, 16, 18, 20, 237, 239, 119, 105, 107, 189,
                    191, 22, 8, 10, 225, 227, 97, 99, 101, 177, 179, 0, 2, 4, 229, 231,
                    103, 89, 91, 181, 183, 6, 41, 43, 217, 219, 93, 95, 169, 171, 45, 47,
                    33, 221, 223, 81, 83, 85, 173, 175, 35, 37, 39, 209, 211, 87, 73, 75,
                    161, 163, 25, 27, 29, 213, 215, 77, 79, 65, 165, 167, 31, 17, 19, 201,
                    203, 67, 69, 71, 153, 155, 21, 23, 193, 195, 57, 59, 49, 145, 147, 9,
                    11, 1, 197, 199, 51, 53, 55, 149, 151, 3, 5, 7 ]
    warps_per_module = len(module_index)
    extra_module_bytes = 5 # Some 'gaps' in the module..

    warps = warps_per_module * module_count
    tc2_ready = False
    last_footswitch = time.time()

    def __init__(self, host="192.168.0.100", port=62000):
        self.host = host
        self.port = port
        self.calculate_warp_mapping()
        self.sequence = 0
        self.history = []
        self.future = []
        # True when a pick has been sent and hasn't yet been woven
        self.weaving = False
        self.on_footswitch = None

    def calculate_warp_mapping(self):
        warp_mapping = []
        for side in self.modules:
            module_column = len(side)
            for i in range(0, self.warps_per_module):
                for module_n in range(0, module_column):
                    warp_mapping.append({'module': side[module_n], 'index': self.module_index[i]})
        self.warp_mapping = warp_mapping

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self.sock = sock
        # Start
        self.send_hex("010104")

    def send_hex(self, msg):
        print("sending " + msg)
        self.sock.sendall(bytes.fromhex(msg))

    def shed_to_string(self, shed):
        modules = []
        for i in range(0,self.module_count):
            modules.append(['0'] * (self.warps_per_module + (self.extra_module_bytes * 4)))

        for i, bit in enumerate(shed):
            if bit:
                mapping = self.warp_mapping[i]
                modules[mapping['module']][mapping['index']] = '1'
        result = ""
        for i in range(0,self.module_count):
            result += "%02d" % (i+1)
            bits = modules[i]
            while len(bits) > 0:
                byte = bits[:4]
                bits = bits[4:]
                result += hex(15-int(''.join(byte), 2))[2]
        
        return result

    def pick(self, shed):
        self.history.append(shed)
        self.sequence = self.sequence + 1

        _command = '02'
        _sequence = '%04d' % self.sequence
        _packet = '01'
        _modules = ("%02d" % self.module_count)
        header = "05" + _command + _sequence + _modules + _packet + _modules
        data = self.shed_to_string(shed)
        self.send_hex(header + data)

    def pick_next(self):
        if (len(self.future) > 0):
            shed = self.future.pop(0)
            self.pick(shed)
            self.weaving = True

    def stop(self):
        self.send_hex("010101")

    def queue(self, shed):
        self.future.append(shed)
        if not self.weaving:
            self.pick_next()

    def status(self):
        return {"ready": self.tc2_ready}
        
    
    def poll(self, timeout=0.1):
        status_changed = False
        tc2_received = select.select([self.sock], [], [], timeout)
        if tc2_received[0]:
            data = self.sock.recv(1024).hex()
            
            print("tc2 says: ", data)
            if re.search("^0503", data):
                print("footswitch")
                t = time.time()
                d = t - self.last_footswitch
                self.last_footswitch = t
                self.weaving = False
                if self.on_footswitch:
                    self.on_footswitch(d)
                self.pick_next()
            elif re.search("^0504$", data):
                print("resting")
            elif re.search("^01010101$", data):
                print("stopped")
                self.tc2_ready = False
                self.weaving = False
            elif data == "01010401":
                print("tc2 ready")
                self.sock.sendall(b'')
                self.tc2_ready = True
                status_changed = True
        return status_changed

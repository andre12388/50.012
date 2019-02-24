from random import gauss
import socket
import math
import time
import threading

################################# CONSTANTS ###########################
STANDARD_COMMANDS = ["filter", "incFlow", "decFlow", "incVit", "decVit", "incpH", "decpH", "halt", "run"]
BUFFER_SIZE = 1024
#effects on durability for each particle remove/added
decay_rate = [0.02,0.02,0.02,0.02]

#dirt, bateria level, H+ count, vitamins, h20
input_percentage = [0.05,0.05,0.09,0.01,0.8]
input_variance = 0.005

################################# Global variable ###############################
input_batch_size = 1000

ph_target_percentage = 0.05
vitamin_target_percentage = 0.05
#0 = slowest (clear most bacteria), # 1 = fastest(clear least)
flow_rate = 0.3

##durability
#1 = fresh
#0 = used up
durability = [1,1,1,1]

########## processing variables
purifying_time = 1.5
replacement_time = 4
command_time = 2

plant_running = True
plant_replacing = False
plant_executing_command = False

################################### step size #####################################
BATCH_STEP_SIZE = 100
VITAMIN_STEP_SIZE = 0.05
PH_STEP_SIZE = 0.05
FLOW_RATE_STEP_SIZE = 0.1

class Plant(object):
    def __init__(self,plant_address="10.0.0.92", port=1024):
        self._plant_address = plant_address
        self._port = port
        self._s = None
        self._connection = None

#######creating a variance for input_batch#######
    def create_input_batch(self):
        batch_size = globals()['input_batch_size']
        percentage = globals()['input_percentage']
        # variant_percentage = self.create_variance_percentage(percentage, 0.005)
        input_batch = []
        for i in range(len(globals()['input_percentage'])):
            input_batch.append(round(batch_size*percentage[i]))
        return input_batch
    
    def non_negative_gauss(self, mean, variance):
        count = 0
        while True:
            count += 1
            random_value = gauss(mean, math.sqrt(mean*variance))
            if(random_value > 0):
                break
            if(count>100 and random_value<=0):
                return None
        return random_value

    def create_variance_percentage(self, means, variance):
        new_means = []
        percentage = []
        for i in range(len(means)):
            random_value = self.non_negative_gauss(means[i],variance)
            new_means.append(random_value)

        total = sum(new_means)
        for i in range(len(new_means)):
            percentage.append(new_means[i]/total)
        return percentage
    # print(create_input_batch(100,percentage))


    #returns the effectiveness of doing its job
    def durability_effectiveness(self):
        durability = globals()['durability']
        effectiveness = []
        # for formula
        opp_durability = []
        for i in range(len(durability)):
            if durability[i] == 1 :
                opp_durability.append(0.000000000000000000001)
            elif durability[i]<0 :
                opp_durability.append(1)
            else:
                opp_durability.append(1 - durability[i])

        #formula
        for i in range(len(opp_durability)):
            e = 2.71828
            x = opp_durability[i]
            power = 1 - 1 / (x**4)
            loss = e**power
            effectiveness.append(1-loss)
        return effectiveness

    # print(durability_effectiveness([1.0,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.05]))

    def amount_to_remove(self, type, water_count, component_count, effectiveness):
        #dirt , remove everything
        if(type == 0):
            return round(component_count * (effectiveness))
        #bacteria, depends on flow rate
        #slower the flow rate, the more bacteria it kills
        elif(type == 1):
            flow_rate_multiplier = (1 - globals()['flow_rate']) / 1
            return round(flow_rate_multiplier * effectiveness * component_count)
        #ph and vitamins, try to maintain at target concentration
        else:
            # ph
            if(type==2):
                target_percentage = globals()['ph_target_percentage']
            #vitamin
            else:
                target_percentage = globals()['vitamin_target_percentage']

            component_percentage = component_count / water_count
            percentage_to_change = component_percentage - target_percentage
            return round(water_count * percentage_to_change * effectiveness)


    ## purify
    def purify_batch(self,input_batch):
        _durability = globals()['durability']
        _decay_rate = globals()['decay_rate']
        water_count = input_batch[4]
        output_batch = []

        #calculate how effective it does its job
        effectiveness = self.durability_effectiveness()
        #do the job
        for i in range(len(_durability)):
            #i + 1 cause first index is water content
            amt_to_remove = self.amount_to_remove(i,water_count,input_batch[i],effectiveness[i])
            # print("amount_to_remove: " + str(amt_to_remove))

            #remove dirt and bateria first
            output_batch.append(input_batch[i]-amt_to_remove)

            #decay the durability
            decay_amount= _decay_rate[i]
            # print("decay amount: " + str(decay_amount))
            _durability[i] -= decay_amount

        #set durability
        globals()['durability'] = _durability
        #add back water
        output_batch.append(water_count)

        return self.pack(input_batch,output_batch)



    ################################# DATA PACKET #########################
    def pack(self,input_batch, output_batch):
        packet = ""
        for i in range(len(input_batch)):
            if(i==len(input_batch)-1):
                packet += str(input_batch[i])+"|"
            else:
                packet += str(input_batch[i])+","
        for i in range(len(output_batch)):
            if(i==len(output_batch)-1):
                packet += str(output_batch[i])
            else:
                packet += str(output_batch[i])+","
        return packet

    def unpack(self,packet):
        input_str, output_str = str.split(packet,'|')
        input_str_batch = input_str.split(',')
        output_str_batch = output_str.split(',')
        input_batch = []
        output_batch = []
        for i in range(len(input_str_batch)):
            input_batch.append(int(input_str_batch[i]))
            output_batch.append(int(output_str_batch[i]))
        return input_batch, output_batch

    def purify(self):
        _input_batch = self.create_input_batch()
        message = self.purify_batch(_input_batch)
        return message

    def boot_up(self):
        if self._s == None:
            self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Plant waiting for info center client")
        try:
            self._s.bind((self._plant_address, self._port))
            self._s.listen(1)
            self._connection, _addr = self._s.accept()
            print("Connection to Information Center Successful")
        except:
            print("Connection to Information Center Failed")



    def main(self):
        self.boot_up()
        # self._s.recv(BUFFER_SIZE)
        print("\nPurifying ...")
        while True:
            if globals()['plant_running'] == False:
                globals()['plant_executing_command'] = False
                time.sleep(0.5)
                continue
            if globals()['plant_replacing'] == False:
                if globals()['plant_executing_command'] == False:
                    data = self.purify()
                    self._connection.send(data.encode('utf-8'))
                    time.sleep(purifying_time)
                else:
                    time.sleep(globals()['command_time'])
                    print('Done command, continue Purifying ...')
                    globals()['plant_executing_command'] = False
            else:
                globals()['durability'] = [1, 1, 1, 1]
                print("Replacing Filter ...")
                time.sleep(replacement_time)
                print("Filter replaced")
                globals()['plant_replacing'] = False
        self._connection.close()
        print("Plant processing Halted")

    def test_main(self):
        while globals()['plant_running']:
            if(globals()['plant_replacing'] == False):
                data = self.purify()
                print("data: " + data)
                # print("Purifying batch ...")
                time.sleep(purifying_time)
                # print("Purified, data packet sent")
            else:
                globals()['durability'] = [1, 1, 1, 1]
                print("Replacing filter ...")
                time.sleep(replacement_time)
                print("Filter replaced")
                globals()['plant_replacing'] = False
        print("Plant processing Halted")



class Plant_Controller(object):
    def __init__(self, plant_controller_address="10.0.0.92", port=1025):
        self._plant_controller_address = plant_controller_address
        self._port = port
        self._s = None
        self._connection = None

    def boot_up(self):
        if(self._s == None):
            self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Plant controller waiting for control unit client ...")
        try:
            self._s.bind((self._plant_controller_address, self._port))
            self._s.listen(1)
            self._connection, _addr = self._s.accept()
            print("Connection to Control Unit Successful")
        except:
            print("Connection to Control Unit Failed")

    def incFlowRate(self,is_increase):
        if is_increase:
            if globals()['flow_rate'] > 0 and globals()['flow_rate'] < (1 - globals()["FLOW_RATE_STEP_SIZE"]):
                globals()['flow_rate'] += globals()['FLOW_RATE_STEP_SIZE']
        else:
            if globals()['flow_rate'] < 1 and globals()['flow_rate'] > globals()["FLOW_RATE_STEP_SIZE"]:
                globals()['flow_rate'] -= globals()['FLOW_RATE_STEP_SIZE']

    def main(self):
        self.boot_up()

        while True:
            try:
                command = self._connection.recv(BUFFER_SIZE)
                command = command.decode('utf-8')
                if globals()['plant_executing_command'] == False:
                    if command in STANDARD_COMMANDS:
                        globals()['plant_executing_command'] = True
                        print("\nExecuting " + str(command) + " command ...")
                    else:
                        continue
                else:
                    print("Cannot execute " + str(command) + " command because another command is being processed")
                    continue

                if command == "filter":
                    globals()['plant_replacing'] = True
                elif command == "halt":
                    globals()['plant_running'] = False
                    print("Plant Halted")
                elif command == "run":
                    globals()['plant_running'] = True
                    print("Plant Running")
                elif command == "incFlow":
                    self.incFlowRate(True)
                elif command == "decFlow":
                    self.incFlowRate(False)
                elif command == "incVit":
                    if globals()['vitamin_target_percentage'] < 100 - globals()['VITAMIN_STEP_SIZE']:
                        globals()['vitamin_target_percentage'] += 0.05
                elif command == "decVit":
                    if globals()['vitamin_target_percentage'] > globals()['VITAMIN_STEP_SIZE']:
                        globals()['vitamin_target_percentage'] -= 0.05
                elif command == "incpH":
                    if globals()['vitamin_target_percentage'] < 100 - globals()['PH_STEP_SIZE']:
                        globals()['ph_target_percentage'] += 0.05
                elif command == "decpH":
                    if globals()['vitamin_target_percentage'] > globals()['PH_STEP_SIZE']:
                        globals()['ph_target_percentage'] -= 100
                else:
                    continue
            except KeyboardInterrupt:
                break

            except:
                self._connection.close()



class Plant_Thread (threading.Thread):
    def __init__(self, plant):
        threading.Thread.__init__(self)
        self._plant = plant

    def run(self):
        self._plant.main()
        
class PlantCU_Thread (threading.Thread):
    def __init__(self, plantcu):
        threading.Thread.__init__(self)
        self._plantcu = plantcu

    def run(self):
        self._plantcu.main()

p = Plant()
c = Plant_Controller()
thread1 = Plant_Thread(p)
thread2 = PlantCU_Thread(c)
thread1.start()
thread2.start()


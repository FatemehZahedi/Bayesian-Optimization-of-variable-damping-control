import json
import argparse
from pathlib import Path
from collections import OrderedDict

def load_step_01_config_txt(filename):
    config = dict()
    lines = []
    with open(filename) as f:
        lines = f.readlines()

    for count, line in enumerate(lines):
        print(f'line {count}: {line}')    
        if(count == 0): 
            config["remote_folder_src"] = str(line.strip("\n"))
        if(count == 1): 
            config["local_folder_dest"] = str(line.strip("\n"))
        if(count == 2): 
            config["remote_file_dest"] = str(line.strip("\n"))

    return config

class config_file_client(object):
    def __init__(self, filename):
        self.config = self.load_json(filename)
        self.config_filename = filename

    def load_txt(self, filename, key_lists): 
        data = dict()
        lines = []
        with open(filename) as f:
            lines = f.readlines()    

        for count, line in enumerate(lines):
            print(f'line {count}: {line}')   
            key = key_lists[count]
            data[key] = str(line.strip("\n"))
        return data

    def load_json(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        return data

    def update_dict(self, dict_1, dict_2):
        #dict_1 <- dict_2 update
        new_dict = {**dict_1, **dict_2}
        return new_dict

    def convert_ssh_client_dict(self, src, dest, remote_ip, username, password, hostname):
        data = dict()
        data["src"]         = src
        data["dest"]        = dest
        data["remote_ip"]   = remote_ip
        data["username"]    = username
        data["password"]    = password
        data["hostname"]    = hostname
        return data

    def init_config(self):
        txtfile = str(Path(self.config["copy_config"]["local_config_folder"]) /  self.config["copy_config"]["config_filename"])
        data = self.load_txt(txtfile, ["remote_folder_src", "local_folder_dest", "remote_folder_dest","no1", "no2", "no3", "no4"])
        print("data (before):", data)
        self.config["copy_config"]["data"] = self.update_dict(self.config["copy_config"]["data"], data)
        print("data (after):")
        self.print_dict(self.config)
        self.save_global_json()

    def init_param(self):

        param_loc_filename = str(Path(self.config["copy_param"]["local_param_loc_folder"]) /  self.config["copy_param"]["param_location_filename"])
        data = self.load_txt(param_loc_filename, ["local_param_loc"])

        self.config["copy_param"]["data"] = self.update_dict(self.config["copy_param"]["data"], data)
        self.print_dict(self.config)
        self.save_global_json()        

    def print_dict(self, dict_data):
        import pprint
        pp = pprint.PrettyPrinter(depth=4)
        pp.pprint(dict_data)
    
    def save_global_json(self):
        with open(self.config_filename,'w') as output:    
            json.dump(self.config, output, indent=4)

    def save_json(self, data, filename):
        with open(filename,'w') as output:    
            json.dump(data, output, indent=4)

    def update(self, mode):
        if(mode == 1):           # get_config_from_kukapc (Step01)
            
            copy_config = self.config["copy_config"]
            remote_config = self.config["remote_config"]
            tag = "step_01"

            info_ssh_data = self.convert_ssh_client_dict(
                                src = str(Path(copy_config["remote_config_folder"]) / copy_config["config_filename"]), 
                                dest = str(Path(copy_config["local_config_folder"]) / copy_config["config_filename"]),   
                                remote_ip = remote_config["remote_ip"],
                                username = remote_config["username"],
                                password = remote_config["password"], 
                                hostname = remote_config["hostname"])

            self.config["ssh_client"][tag]["data"]  = info_ssh_data
            self.config["ssh_client"][tag]["label"]  = "get_config_from_KukaPC"
            self.config["ssh_client"][tag]["type"] = 0
            self.config["ssh_client"][tag]["travel"] = 1

            filename = str(Path("config") / (tag + ".json"))
            self.save_json(data = self.config["ssh_client"][tag], filename = filename)

            self.save_global_json()

        elif(mode == 2):        # get_files_KukaPC (Step02)

            copy_config_data = self.config["copy_config"]["data"]
            remote_config = self.config["remote_config"]
            tag = "step_02"

            info_ssh_data = self.convert_ssh_client_dict(
                                src = str(Path(copy_config_data["remote_folder_src"])), 
                                dest = str(Path(copy_config_data["local_folder_dest"])),   
                                remote_ip = remote_config["remote_ip"],
                                username = remote_config["username"],
                                password = remote_config["password"], 
                                hostname = remote_config["hostname"])

            self.config["ssh_client"][tag]["data"]  = info_ssh_data
            self.config["ssh_client"][tag]["label"]  = "get_files_from_KukaPC"
            self.config["ssh_client"][tag]["type"] = 1
            self.config["ssh_client"][tag]["travel"] = 1

            #filename = str(Path("config") / (tag + "_" + self.config["ssh_client"][tag]["label"] + ".json"))
            filename = str(Path("config") / (tag + ".json"))
            self.save_json(data = self.config["ssh_client"][tag], filename = filename)

            self.save_global_json()

        elif(mode == 6):        # get_files_KukaPC (Step06)

            copy_param_data = self.config["copy_param"]["data"]
            copy_config_data = self.config["copy_config"]["data"]
            remote_config = self.config["remote_config"]
            tag = "step_06"

            info_ssh_data = self.convert_ssh_client_dict(
                                src = str(Path(copy_param_data["local_param_loc"])), 
                                dest = str(Path(copy_config_data["remote_folder_dest"])),   
                                remote_ip = remote_config["remote_ip"],
                                username = remote_config["username"],
                                password = remote_config["password"], 
                                hostname = remote_config["hostname"])

            self.config["ssh_client"][tag]["data"]  = info_ssh_data
            self.config["ssh_client"][tag]["label"]  = "copy_files_to_KukaPC"
            self.config["ssh_client"][tag]["type"] = 1
            self.config["ssh_client"][tag]["travel"] = 0

            #filename = str(Path("config") / (tag + "_" + self.config["ssh_client"][tag]["label"] + ".json"))
            filename = str(Path("config") / (tag + ".json"))
            self.save_json(data = self.config["ssh_client"][tag], filename = filename)

            self.save_global_json()

def test():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='0', type=int, help='1 : "step_01", 2: "step_02"')
    args = parser.parse_args()
    mode = int(args.mode)
    #step_01 = load_last_json()
    #load_step_01_config_txt()
    client = config_file_client("config/config.json")
    client.init_config()
    client.init_param()
    client.update(mode = mode)
    print("[mode :", mode, "] cofiguration file updated!")

if __name__ == "__main__":
    test()
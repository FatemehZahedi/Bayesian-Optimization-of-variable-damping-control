# Dongjune Chang April.02th.2021

# this is for python script for sending the file via openssh
# 1) reading info file and parse it
# 2) send "the file" written in the info file

# pip install paramiko
# pip install scp
# https://stackoverflow.com/questions/4409502/directory-transfers-with-paramiko
"""
 History : 0421 version : 1) update file and folder is copied
                          2) Fixed bug that the file is not transfered, if the folder does not exist
"""

import json
from pathlib import Path
import argparse
import paramiko
import logging
import scp
from collections import deque

log = logging.getLogger(__name__)

class ssh_client(object):    
    def get_ssh_client(self):
        success = False

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            success = True
        except Exception as e:
            print("Operation error: %s", e)
            success = False

        return success

    def login(self, hostname, username, password):
        success = False

        try:
            log.info("Establishing ssh connection")
            get_client_success = self.get_ssh_client()
            self.client.load_system_host_keys()
            self.client.connect(hostname, username=username, password=password)
            success = True

        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials: %s")
            success = False

        except paramiko.SSHException as sshException:
            print("Unable to establish SSH connection: %s" % sshException)
            success = False

        except paramiko.BadHostKeyException as badHostKeyException:
            print("Unable to verify server's host key: %s" % badHostKeyException)
            success = False

        except Exception as e:
            print(e.args)
            success = False

        if(success):
            self.hostname = hostname
            self.username = username
            self.password = password
            
            log.info("Hostname: %s", hostname)
        
        return success

    def create_sftp_dir_recursive(self, sftp, path):

        def is_sftp_dir_exists(sftp, path):
            try:
                sftp.stat(path)
                return True
            except Exception:
                return False

        def create_sftp_dir(sftp, path):
            try:
                sftp.mkdir(path)
            except IOError as exc:
                if not is_sftp_dir_exists(sftp, path):
                    raise exc

        parts = deque(Path(path).parts)

        to_create = Path()
        while parts:
            to_create /= parts.popleft()
            create_sftp_dir(sftp, str(to_create))

    def send_file(self, src_file, dest_file, travel = 0):
        success = False

        try:       
            log.info("Getting SCP Client")
            scpclient = scp.SCPClient(self.client.get_transport())
            log.info(scpclient)

            destPath = Path(dest_file).parents[0]
            #try:
            if(travel == 0):   # if travel == 0, current -> remote
                log.info("Getting SFTP Client")
                sftp_client = self.client.open_sftp()
                self.create_sftp_dir_recursive(sftp_client, str(destPath))
                sftp_client.close()

                scpclient.put(src_file, dest_file)
            else:               # if travel == 0,  remote -> current
                destPath.mkdir(parents=True, exist_ok=True)
                scpclient.get(src_file, dest_file)

            #except:
            #    pass

            success = True
        except scp.SCPException as e:
            print("Operation error: %s", e) 
            success = False

        if(success):
            log.info("source file: %s", src_file)
            log.info("target file: %s", dest_file)

        return success

    def send_folder(self, src_folder, dest_folder, travel = 0):
        
        def local_walk(dir_path_to_search):
            filename_list = []

            file_iterator = dir_path_to_search.iterdir()

            for entry in file_iterator:
                    if entry.is_file():
                        filename_list.append(entry.name)

            return filename_list

        def remote_walk(sftp, dest_folder):
            from stat import S_ISDIR
            path=dest_folder
            files=[]
            folders=[]
            for f in sftp.listdir_attr(dest_folder):
                if S_ISDIR(f.st_mode):
                    folders.append(f.filename)
                else:
                    files.append(f.filename)
            if files:
                yield path, files
            for folder in folders:
                new_path = str(Path(dest_folder) / folder)
                for x in remote_walk(sftp, new_path):
                    yield x
        """
        def downLoadFile(sftp, remotePath, localPath):
            import stat, os
            for fileattr in sftp.listdir_attr(remotePath):  
                if stat.S_ISDIR(fileattr.st_mode):
                    path_from = str(os.path.join(remotePath, fileattr.filename))
                    path_to = str(os.path.join(localPath, fileattr.filename))

                    if(os.path.isdir(path_from)):
                        print("path_from :", path_from, " path_to:", path_to)
                        downLoadFile(sftp, path_from, path_to)
        """            
        
        from stat import S_ISDIR, S_ISREG
        from collections import deque

        def listdir_r(sftp, remotedir):
            dirs_to_explore = deque([remotedir])
            list_of_files = deque([])
            list_of_folders = []

            while len(dirs_to_explore) > 0:
                current_dir = dirs_to_explore.popleft()

                for entry in sftp.listdir_attr(current_dir):
                    current_fileordir = current_dir + "/" + entry.filename

                    if S_ISDIR(entry.st_mode):
                        dirs_to_explore.append(current_fileordir)
                        list_of_folders.append(current_fileordir)
                    elif S_ISREG(entry.st_mode):
                        list_of_files.append(current_fileordir)

            return list(set(list_of_folders)), list(list_of_files)
                
        try:       
            log.info("Getting SCP Client")
            scpclient = scp.SCPClient(self.client.get_transport())
            log.info(scpclient)

            inbound_files = []   
            rootdir = Path(src_folder)

            sftp_client = self.client.open_sftp()
            log.info("Getting SFTP Client")

            if(travel == 0):   # if travel == 0, current -> remote  
                inbound_files = local_walk(Path(src_folder))    
                print(inbound_files)        
                self.create_sftp_dir_recursive(sftp_client, dest_folder)  # make directory recursively

                for ele in inbound_files:
                    try:
                        path_from = str(Path(src_folder) / ele)
                        path_to = str(Path(dest_folder) / ele)
                        print("path_from :", path_from, " path_to:", path_to)

                        if(travel == 0): 
                            sftp_client.put(path_from, path_to)
                    except:
                        print(ele, ": failed")

            else:               # if travel == 1, remote -> current 
                #inbound_files = remote_walk(sftp_client, str(Path(src_folder)))
                Path(dest_folder).mkdir(parents=True, exist_ok=True)
                # from remote to download into local

                path_from = str(Path(src_folder))
                path_to = str(Path(dest_folder))
                print("path_from :", path_from, " path_to:", path_to)

                folders, files = listdir_r(sftp_client, path_from)
                print ("folders : ", folders)
                print ("files : ", files)

                for folder in folders:
                    real_folder_path = str(Path(folder).relative_to(Path(path_from)))
                    new_folder_path = str(Path(path_to) / real_folder_path)
                    Path(new_folder_path).mkdir(parents=True, exist_ok=True)
                    print("folder generated:", new_folder_path)

                for file in files:
                    real_path = str(Path(file).relative_to(Path(path_from)))
                    #print("real_path:", real_path)
                    new_path = str(Path(path_to) / real_path)

                    print("new_path:", new_path)
                    sftp_client.get(file, new_path)

                """
                import os
                str_cmd = "scp -r " + path_from + " " + path_to + "/"
                print("str_cmd:", str_cmd)

                os.system(str_cmd)

                ##downLoadFile(sftp_client, path_from, path_to)
                """
                """
                for path, files in remote_walk(sftp_client, str(Path(src_folder))):

                    for file in files:
                        #sftp.get(remote, local) line for dowloading.
                        path_from = str(Path(path)/file)
                        path_to = str(Path(dest_folder)/file)
                        sftp_client.get(path_from, path_to)
                        print("path_from :", path_from, " path_to:", path_to)
                """
                    
                """
                for ele in inbound_files:
                    try:
                        path_from = str(Path(src_folder) / ele)
                        path_to = str(Path(dest_folder) / ele)
                        print("path_from :", path_from, " path_to:", path_to)

                        if(travel == 0): 
                            sftp_client.put(path_from, path_to)
                        else:
                            sftp_client.get(path_from, path_to)
                    except:
                        print(ele, ": failed")
                """
            sftp_client.close()
            success = True

        except scp.SCPException as e:
            print("Operation error: %s", e) 
            success = False

        if(success):
            log.info("source folder: %s", src_folder)
            log.info("target folder: %s", dest_folder)

        return success

    def close(self):
        self.client.close()

def test():
    parser = argparse.ArgumentParser()
    #parser.add_argument('--type', default='0', type=int, help='0 : file copy, 1: folder copy')
    parser.add_argument('--info', default='file.json', type=str, help='infomation file or folder name (full path)')
    #parser.add_argument('--travel', default='0', type=int, help='0 : current -> remote, 1: remote -> current')

    args = parser.parse_args()
#    copy_type = int(args.type)
    info_file = str(Path(args.info))
#    travel = int(args.travel)

    with open(info_file) as json_file:
        info = json.load(json_file)

    data        = info["data"]
    copy_type   = info["type"]
    travel      = info["travel"]

    print(data)
    src = str(Path(data["src"]))                    # full path of source file 
    dest = str(Path(data["dest"]))                  # full path of destination file 
    remote_ip = str(Path(data["remote_ip"]))        # remote ip
    username = str(Path(data["username"]))          # remote username
    password = str(Path(data["password"]))          # remote password
    hostname = str(Path(data["hostname"]))          # remote hostname

    print("travel:", travel)
    client = ssh_client()

    login_success = client.login(remote_ip, username, password)  # it is acceptable replacinh remote_ip into hostname
    print("login_success", login_success)

    if(login_success):
        if(copy_type == 0):
            send_success = client.send_file(src, dest, travel)
        else:
            send_success = client.send_folder(src, dest, travel)            

    if(send_success):
        print("send file(s) completed!")
    else:
        print("send file(s) failed!")

    client.close()

def main():
    test()

if __name__ == "__main__":
    main()


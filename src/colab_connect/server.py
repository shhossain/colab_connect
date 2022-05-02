import os
from .helper import File, safe_username
from .create_tunnel import Ngrok
from .custom_log import Log

class Colab:
    def __init__(self,username='root',password='root',hostname="ColabConnect",log_level='info'):
        self.log = Log(log_level) 
        self.hostname = hostname
        self.username = safe_username(username)
        self.password = password
        if username != 'root':
            self.create_user(self.username,password)
        else:
            self.set_root_password(password)
        self._set_hostname()
        self._check_colab()
        
        self.log.debug(f'Colab Connect initialized')

    def _set_hostname(self):
        name = self.hostname
        l1 = '/etc/hostname'
        l2 = '/etc/hosts'

        #set hostname
        file1 = File(l1)
        file2 = File(l2)
        old_hostname = file1.read()
        file1.write(name)
        file2.write(file2.read().replace(old_hostname,name))
        cmd = f'hostname {name}'
        e = self.execute(cmd)
        if e:
            #log debug hostname changed to self.hostname
            self.log.debug(f'Hostname changed to {name}')
        else:
            #log error hostname not changed
            self.log.error(f'Hostname not changed to {name}')


    
    # create sudo user
    def create_user(self,username,password):
        a = self.execute(f"useradd -m {username}")
        b = self.execute(f"adduser {username} sudo")
        c = self.execute(f"echo '{username}:{password}' | sudo chpasswd")
        d = self.execute("sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd")
        e = self.execute(f"touch /home/{username}/.hushlogin")

        if a and b and c and d and e:
            #log debug user created
            self.log.debug(f'User {username} created')

            #log debug changed home directory ownership to self.username
            cmd2 = f'chown {self.uesrname} -G /home/{self.username}'
            self.execute(cmd2)
            self.log.debug(f'Changed home directory ownership to {self.username}')
            return True 
        else:
            #log error user not created
            self.log.error(f'User {username} already exists')
            return False
    
    #set root password
    def set_root_password(self,password):
        cmd = f'echo root:{password} | chpasswd'
        #log debug root password changed
        e = self.execute(cmd)
        if e:
            self.log.debug(f'Root password changed')
        else:
            self.log.error(f'Root password not changed')
        return e

    def _check_colab(self):
        if not os.environ.get('COLAB_GPU'):
            print('Not connected to colab')
            exit()
    
    #check if a package is installed
    def check_package(self,package):
        cmd = f'which {package}'
        return self.execute(cmd)
    
    #install a package
    def install_package(self,package):
        cmd = f'apt install {package}'
        return self.execute(cmd)

    def execute(self,command):
        return True if os.system(command)==0 else False

class DriveBackup:
    def __init__(self,colab:Colab,drive_backup_path=None):
        if drive_backup_path is None:
            drive_backup_path = os.path.join('CloudConnect','backup')
        self.drive_path = os.path.join(os.sep,'content','drive','MyDrive')
        self.drive_backup_path = drive_backup_path
        self.log = colab.log
        self.ismounted =  self._check_drive_is_mounted()
        if self.ismounted:
            self._create_backup_folder()
        self.log_path = os.path.join(self.drive_backup_path,'log.txt')
        
    def _check_drive_is_mounted(self):
        if os.path.exists(self.drive_path):
            self.log.info('Drive is mounted')
            return True
        else:
            self.log.error('Mount drive to backup')
            return False
    
    #create backup folder if it doesn't exist
    def _create_backup_folder(self):
        if not os.path.exists(self.drive_backup_path):
            os.makedirs(self.drive_backup_path)
            self.log.info('Created backup folder')
    
    def backup_log(self,path):
        #create a log file if it doesn't exist
        folder_name = os.path.basename(path)
        key,val = folder_name,path
        
        file = File(self.log_path)
        if not os.path.exists(self.log_path):
            new_log = {key:val}
            file.jdump(new_log)
        else:
            log = file.jload()
            log[key] = val
            file.jdump(log)
    
    def restore(self,folder_name):
        #get restore path from log file
        if self.ismounted:
            file = File(self.log_path)
            log = file.jload()
            if folder_name in log:
                path = log[folder_name]
                self.log.info(f'Restoring {folder_name} from {path}')
                # copy folder from backup to path
                copy_path = os.path.join(self.drive_backup_path,folder_name)
                cmd = f'cp -r {copy_path} {path}'
                e = self.execute(cmd)
                if e:
                    self.log.info(f'Restored {folder_name}')
                else:
                    self.log.error(f'{folder_name} not restored')
            else:
                self.log.error(f'{folder_name} not found in log')
        else:
            self.log.error('Drive not mounted')
            
    
    def backup(self,path):
        # copy path folder to backup folder
        if self.ismounted:
            self.backup_log(path)
            cmd = f'cp -r {path} {self.drive_backup_path}'
            e = self.colab.execute(cmd)
            if e:
                self.log.info(f'Backup of {path} complete')
            else:
                self.log.error(f'Backup of {path} failed')
        else:
            self.log.error('Drive not mounted')
    
    def backup_path(self,folder_name):
        return os.path.join(self.drive_backup_path,folder_name)

class SSH:
    def __init__(self,colab:Colab,tunnel_name='ngrok',auth_token=None) -> None:
        self.colab = colab
        self.auth_token = auth_token
        self.tunnel_name = tunnel_name
        if tunnel_name.lower()=='ngrok':
            self.tunnel = Ngrok(auth_token)
            self._create_ngrok_tunnel()
            self._show_ssh_cmd()
        self.log = colab.log
        self._install_ssh()
        self._start_ssh()
        self._check_ssh()
        self.backup = DriveBackup(self.colab)
        self.ssh_backup_folder =  self.backup.backup_path('ssh')
        self.ssh_etc_folder = os.path.join(os.sep,'etc','ssh')
        self._check_ssh_backup()
        self.ssh_public_url = None
    
    #check .ssh backup folder exists
    def _check_ssh_backup(self):
        if os.path.exists(self.ssh_backup_folder):
            self.backup.restore('ssh')
        else:
            self.backup.backup(self.ssh_etc_folder)
    
    def _install_ssh(self):
        if self.colab.check_package('openssh-server'):
            self.log.debug('SSH already installed')
        else:
            self.log.debug('Installing SSH')
            self.colab.install_package('openssh-server')
    
    #start ssh service
    def _start_ssh(self):
        cmd = 'service ssh start'
        e = self.colab.execute(cmd)
        if e:
            self.log.debug('SSH started')
        else:
            self.log.error('SSH not started')
    
    # check ssh status
    def _check_ssh(self):
        cmd = 'service ssh status'
        e = self.colab.execute(cmd)
        if e:
            self.log.debug('SSH running')
        else:
            self.log.error('SSH not running')
    
    #create ngrok tcp port 22 tunnel
    def _create_ngrok_tunnel(self):
        tunnel = self.tunnel.tcp(22)
        #log tunnel public url
        self.log.info(f'Tunnel public url: {tunnel.public_url}')
        self.ssh_public_url = tunnel.public_url
    
    def _show_ssh_cmd(self):
        cmd = f'ssh {self.colab.username}@{self.ssh_public_url}'
        self.log.info(f'SSH command: {cmd}')

    # stop ssh service
    def stop_ssh(self):
        cmd = 'service ssh stop'
        e = self.colab.execute(cmd)
        if e:
            self.log.debug('SSH stopped')
        else:
            self.log.error('SSH not stopped')
    

    

    


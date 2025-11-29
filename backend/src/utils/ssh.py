import json, io, base64, queue, threading, paramiko, time, socket
from channels.generic.websocket import WebsocketConsumer
from apps.host.models import Host

class SSHConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = None
        self.ssh = None
        self.chan = None
        self._alive = False
        self._to_ssh_q = queue.Queue()      # 浏览器 → SSH

    # ---------------- 主线程：只负责握手 & 框架回调 ----------------
    def connect(self):
        if(self._alive):
            self.disconnect()
        self._alive = True
        host_id = self.scope['url_route']['kwargs']['host_id']
        try:
            self.host = Host.objects.get(pk=host_id)
        except Host.DoesNotExist:
            self.close(code=3000); return

        # 可选 JWT 子协议校验
        protocols = self.scope.get('subprotocols', [])
        if len(protocols) >= 2:
            from rest_framework_simplejwt.tokens import AccessToken
            try:
                AccessToken(protocols[1])
            except Exception:
                self.close(code=3003); return
        self.accept(subprotocol='jwt' if protocols else None)

        # 建立 SSH
        ok, msg = self._open_ssh()
        if not ok:
            print("SSH初始化失败")
            print(json.dumps({'error': msg}))
            self.disconnect(code=3002); return

        # 启动前端-后端-SSH通信链路
        # # 把线程标记为“守护线程”,主线程退出时它会被强制结束,不会阻止整个进程关闭
        threading.Thread(target=self._start,daemon=True).start()

    # ---------- 建立 SSH ----------
    def _open_ssh(self):
        try:
            pkey = paramiko.RSAKey.from_private_key(io.StringIO(self.host.private_key))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=self.host.ip_addr,
                port=int(self.host.port),
                username=self.host.username,
                pkey=pkey,
                timeout=10
            )
            self.chan = ssh.get_transport().open_session()
            self.chan.get_pty(term='xterm', width=80, height=48)
            self.chan.invoke_shell()                # 打开shell
            self.chan.send('exec bash -l\n')        # 以login-shell方式启动
            self.chan.send('stty -echo\n')          # 关闭SSH回显
            print(f"SSH初始化成功")
            return True, None
        except Exception as e:
            return False, str(e)

    def _start(self):
        try:
            while self._alive:
                self._reader()
                self._writer()
        except Exception as e:
            raise RuntimeError(f"error:{e}")
        finally:
            self.disconnect(code=3001)

    # ---------- 侦听SSH数据,并转发给前端 ----------
    def _reader(self):
        try:
            self.chan.settimeout(0.01)
            data = self.chan.recv(4096)                     # 阻塞0.01s,切换线程
            if(data):
                text_data = base64.b64encode(data).decode() # bytes二进制编码 => b64 => b64文本
                self.send(text_data=text_data)
        except socket.timeout:
            pass
        except Exception as e:
            self._alive = False
            raise RuntimeError("error:_reader数据转发失败",e)

    # ---------- 侦听前端数据,并转发给SSH ----------
    def _writer(self):
        try:
            msg = self._to_ssh_q.get(timeout=0.01)          # 阻塞0.01s,切换线程
            if msg:
                raw = base64.b64decode(msg)                 # b64 => bytes二进制编码
                if not raw.endswith((b'\r', b'\n')):        # 保证有换行
                    raw += b'\n'
                if raw == b'exit\n':
                    self._alive = False
                else:
                    self.chan.sendall(raw)
        except queue.Empty:
            pass
        except Exception as e:
            self._alive = False
            raise RuntimeError("error:_writer数据转发失败",e)

    # ---------- 主线程框架回调：只负责塞队列 ----------
    # # 注意,不能阻塞主线程
    def receive(self, text_data=None, bytes_data=None):
        try:
            payload = text_data or bytes_data.decode()
            self._to_ssh_q.put(payload)
        except Exception:
            self.disconnect(code=3001)

    # ---------- 断开：关闭连接端口----------
    def disconnect(self, code):
        self._alive = False
        if getattr(self, 'chan', None):
            self.chan.close()
        if getattr(self, 'ssh', None):
            self.ssh.close()
        self.close(code=code)

def generate_key_pair() -> tuple[str, str]:
    """
    返回 (私钥PEM, 公钥PEM)
    """
    try:
        key = paramiko.RSAKey.generate(2048)
        # --- 私钥 ---
        private_io = io.StringIO()
        key.write_private_key(private_io)   # Paramiko 原生方法
        private_io.seek(0)
        private = private_io.read()
        # --- 公钥 ---
        public = f"{key.get_name()} {key.get_base64()} generated@web-ssh\n"
    except Exception as e:
        print(f"error:{e}")
    finally:
        return private, public

def push_public_key(host_info):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_info.get('ip_addr'),
            port=int(host_info.get('port')),
            username=host_info.get('username'),
            password=host_info.get('connect_pwd')
        )
        ssh.exec_command('mkdir -p -m 700 ~/.ssh')
        cmd = f'echo {host_info.get("public_key").strip()} >> ~/.ssh/authorized_keys'
        ssh.exec_command(cmd)
        ssh.exec_command('chmod 600 ~/.ssh/authorized_keys')
        print("公钥已上传至远端ssh服务器")
    except Exception as e:
        print(f"error:{e}")
    finally:
        if ssh:
            ssh.close()

def probe_ssh_connect(ip_addr, port, username, password=None, pkey_pem=None, timeout=5):
    """
    仅尝试连接并立即断开,返回 None 表示成功,否则返回错误字符串
    """
    try:
        key = None
        if pkey_pem:                       # 优先用密钥
            key = paramiko.RSAKey.from_private_key(io.StringIO(pkey_pem))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=ip_addr,
            port=int(port),
            username=username,
            password=password,
            pkey=key,
            timeout=timeout,
            allow_agent=False,
            look_for_keys=False
        )
        print('远程服务器连接测试成功')
        return None
    except Exception as e:
        return str(e)
    finally:
        if ssh:
            ssh.close()

def exec_cmd(host_info=None,cmd=None,timeout=5):
    """
    执行SSH命令
    """
    try:
        key_raw = host_info.get('private_key')
        if key_raw:                       # 优先用密钥
            pkey = paramiko.RSAKey.from_private_key(io.StringIO(key_raw))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_info.get('ip_addr'),
            port=int(host_info.get('port')),
            username=host_info.get('username'),
            pkey=pkey,
            timeout=timeout
        )
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.settimeout(1)          # 最大等1s
        try:
            stdout.channel.recv_exit_status()
        except socket.timeout:
            raise RuntimeError('命令执行超时(>1s)')
        return stdout.read().decode()
    except Exception as e:
        return str(e)
    finally:
        if ssh:
            ssh.close()

def upload_file(host_info=None,file_obj=None,remote_path=None,filename=None,timeout=5):
    """
    上传文件到SSH主机
    """
    try:
        key_raw = host_info.get('private_key')
        if key_raw:                       # 优先用密钥
            pkey = paramiko.RSAKey.from_private_key(io.StringIO(key_raw))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_info.get('ip_addr'),
            port=int(host_info.get('port')),
            username=host_info.get('username'),
            pkey=pkey,
            timeout=timeout
        )
        sftp = ssh.open_sftp()
        with sftp.open(f'{remote_path}/{filename}', 'wb') as f:
            for chunk in file_obj.chunks(chunk_size= 64*1024):   # 每次 ≤ 64 KB 在内存
                f.write(chunk)
    except Exception as e:
        raise RuntimeError(e)
    finally:
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()

def download_file(host_info=None,remote_path=None,filename=None,timeout=5):
    """
    从SSH主机下载文件
    """
    try:
        key_raw = host_info.get('private_key')
        if key_raw:                       # 优先用密钥
            pkey = paramiko.RSAKey.from_private_key(io.StringIO(key_raw))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_info.get('ip_addr'),
            port=int(host_info.get('port')),
            username=host_info.get('username'),
            pkey=pkey,
            timeout=timeout
        )
        with ssh.open_sftp() as sftp:
            with sftp.file(f'{remote_path}/{filename}', 'rb') as f:
                file = io.BytesIO(f.read())   # 一次性读入内存
                file_size = sftp.stat(f'{remote_path}/{filename}').st_size
        return file,file_size
    except FileNotFoundError:
        raise RuntimeError('file not found')
    except Exception as e:
        raise RuntimeError(e)
    finally:
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()
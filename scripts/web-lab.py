#!/usr/bin/env python3
"""Create, verify, and delete the README lab using AWS CLI v2."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import uuid

REGION = 'ap-northeast-2'
ROOT = Path(__file__).resolve().parent
STATE_DIR = ROOT.parent / '.web-lab'
STATE = STATE_DIR / 'state.json'


def aws(service, *args):
    command = ['aws', '--profile', PROFILE, '--region', REGION, '--output', 'json',
               '--no-cli-pager', service, *args]
    result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
    return json.loads(result.stdout) if result.stdout.strip() else {}


def save():
    temporary = STATE.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.chmod(0o600)
    temporary.replace(STATE)


def record(key, value):
    state[key] = value
    save()
    print(f'{key}: {value}', flush=True)
    return value


def tags(name):
    return [{'Key': 'Name', 'Value': name}, {'Key': 'WebLab', 'Value': state['run']}]


def spec(kind, name):
    return json.dumps([{'ResourceType': kind, 'Tags': tags(name)}])


def create(cidr):
    import ipaddress
    network = ipaddress.ip_network(cidr, strict=True)
    if network.version != 4 or network.prefixlen != 32 or network.network_address.is_unspecified:
        raise ValueError('--ssh-cidr에는 본인 공인 IPv4/32를 입력하세요.')
    if STATE.exists():
        raise ValueError('상태 파일이 이미 있습니다. verify 또는 cleanup을 사용하세요.')
    state.update(account=ACCOUNT, profile=PROFILE, region=REGION, run=uuid.uuid4().hex)
    save()
    ami = aws('ec2', 'describe-images', '--owners', '099720109477', '--filters',
              'Name=name,Values=ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*',
              'Name=state,Values=available', 'Name=architecture,Values=x86_64')['Images']
    if not ami:
        raise ValueError('Canonical Ubuntu 24.04 AMI를 찾지 못했습니다.')
    image = max(ami, key=lambda x: x['CreationDate'])
    record('ami', image['ImageId'])
    vpc = record('vpc', aws('ec2', 'create-vpc', '--cidr-block', '10.0.0.0/16',
                           '--tag-specifications', spec('vpc', 'web-lab-vpc'))['Vpc']['VpcId'])
    aws('ec2', 'wait', 'vpc-available', '--vpc-ids', vpc)
    subnet = record('subnet', aws('ec2', 'create-subnet', '--vpc-id', vpc,
                    '--cidr-block', '10.0.1.0/24', '--availability-zone', REGION + 'a',
                    '--tag-specifications', spec('subnet', 'web-lab-public-subnet'))['Subnet']['SubnetId'])
    aws('ec2', 'modify-subnet-attribute', '--subnet-id', subnet, '--map-public-ip-on-launch')
    igw = record('igw', aws('ec2', 'create-internet-gateway', '--tag-specifications',
                           spec('internet-gateway', 'web-lab-igw'))['InternetGateway']['InternetGatewayId'])
    aws('ec2', 'attach-internet-gateway', '--internet-gateway-id', igw, '--vpc-id', vpc)
    record('igw_attached', True)
    rt = record('route_table', aws('ec2', 'create-route-table', '--vpc-id', vpc,
                '--tag-specifications', spec('route-table', 'web-lab-public-rt'))['RouteTable']['RouteTableId'])
    aws('ec2', 'create-route', '--route-table-id', rt, '--destination-cidr-block', '0.0.0.0/0',
        '--gateway-id', igw)
    record('association', aws('ec2', 'associate-route-table', '--route-table-id', rt,
                              '--subnet-id', subnet)['AssociationId'])
    sg = record('security_group', aws('ec2', 'create-security-group', '--group-name',
                'web-lab-sg', '--description', 'HTTP public, SSH my IP', '--vpc-id', vpc,
                '--tag-specifications', spec('security-group', 'web-lab-sg'))['GroupId'])
    for port, source in [(80, '0.0.0.0/0'), (22, str(network))]:
        aws('ec2', 'authorize-security-group-ingress', '--group-id', sg,
            '--protocol', 'tcp', '--port', str(port), '--cidr', source)
    key = record('key_name', 'web-lab-key-' + state['run'][:12])
    result = aws('ec2', 'create-key-pair', '--key-name', key, '--key-type', 'rsa',
                 '--tag-specifications', spec('key-pair', key))
    keyfile = STATE_DIR / (key + '.pem')
    with keyfile.open('x') as f:
        f.write(result['KeyMaterial'])
    keyfile.chmod(0o400)
    record('key_file', str(keyfile))
    instance = aws('ec2', 'run-instances', '--image-id', image['ImageId'],
        '--instance-type', 't3.micro', '--count', '1', '--key-name', key,
        '--subnet-id', subnet, '--security-group-ids', sg, '--associate-public-ip-address',
        '--client-token', state['run'], '--metadata-options', 'HttpTokens=required',
        '--block-device-mappings', json.dumps([{'DeviceName': image['RootDeviceName'],
            'Ebs': {'VolumeSize': 8, 'VolumeType': 'gp3', 'DeleteOnTermination': True}}]),
        '--tag-specifications', spec('instance', 'web-lab-ec2'),
        '--user-data', 'file://' + str(ROOT / 'user-data.sh'))['Instances'][0]
    instance_id = record('instance', instance['InstanceId'])
    record('volumes', [b['Ebs']['VolumeId'] for b in instance.get('BlockDeviceMappings', []) if 'Ebs' in b])
    aws('ec2', 'wait', 'instance-running', '--instance-ids', instance_id)
    refresh_instance()
    print('생성 완료. Docker 초기 설치에는 몇 분이 걸립니다. 다음으로 verify를 실행하세요.')


def refresh_instance():
    i = aws('ec2', 'describe-instances', '--instance-ids', state['instance'])['Reservations'][0]['Instances'][0]
    record('volumes', [b['Ebs']['VolumeId'] for b in i.get('BlockDeviceMappings', []) if 'Ebs' in b])
    return record('public_ip', i.get('PublicIpAddress', ''))


def verify():
    ip = refresh_instance()
    if not ip:
        raise ValueError('공인 IP가 없습니다. 인스턴스 상태를 확인하세요.')
    print('cloud-init 및 내부 검증을 기다립니다 (최대 10분).', flush=True)
    subprocess.run(['ssh', '-i', state['key_file'], '-o', 'StrictHostKeyChecking=accept-new',
        '-o', 'ConnectTimeout=10', 'ubuntu@' + ip,
        'sudo timeout 600 cloud-init status --wait && sudo docker ps && '
        'curl -fsSi http://localhost && curl -fsSi http://localhost/health && '
        'curl -fsSI https://example.com'], check=True)
    url = 'http://' + ip + '/health'
    with urllib.request.urlopen(url, timeout=15) as response:
        body = response.read().decode()
        print(f'GET {url}\nHTTP {response.status}\n{body}')
        if response.status != 200 or body.strip() != 'OK':
            raise ValueError('외부 health 검증 실패')
    record('verified_at', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))


def cleanup():
    answer = input(f"삭제 대상 계정 {ACCOUNT}, VPC {state.get('vpc', '없음')}. 삭제하려면 DELETE 입력: ")
    if answer != 'DELETE':
        raise ValueError('삭제를 취소했습니다.')
    if state.get('instance'):
        aws('ec2', 'terminate-instances', '--instance-ids', state['instance'])
        aws('ec2', 'wait', 'instance-terminated', '--instance-ids', state['instance'])
        for volume in state.get('volumes', []):
            remaining = aws('ec2', 'describe-volumes', '--filters', 'Name=volume-id,Values=' + volume)['Volumes']
            if remaining:
                if remaining[0]['State'] != 'available':
                    raise ValueError('볼륨이 아직 사용 중입니다. 잠시 후 cleanup을 재실행하세요.')
                aws('ec2', 'delete-volume', '--volume-id', volume)
            aws('ec2', 'wait', 'volume-deleted', '--volume-ids', volume)
        state.pop('instance'); save()
    operations = [
        ('association', ['disassociate-route-table', '--association-id']),
        ('subnet', ['delete-subnet', '--subnet-id']),
        ('route_table', ['delete-route-table', '--route-table-id']),
        ('security_group', ['delete-security-group', '--group-id']),
    ]
    for key, args in operations:
        if state.get(key):
            aws('ec2', *args, state[key])
            state.pop(key); save()
    if state.get('igw_attached'):
        aws('ec2', 'detach-internet-gateway', '--internet-gateway-id', state['igw'], '--vpc-id', state['vpc'])
        state.pop('igw_attached'); save()
    for key, flag, action in [('igw', '--internet-gateway-id', 'delete-internet-gateway'),
                               ('vpc', '--vpc-id', 'delete-vpc'), ('key_name', '--key-name', 'delete-key-pair')]:
        if state.get(key):
            aws('ec2', action, flag, state[key])
            state.pop(key); save()
    record('cleaned_at', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    STATE.rename(STATE_DIR / ('cleaned-' + state['run'] + '.json'))
    print('추적한 AWS 리소스 정리 완료. 로컬 PEM/로그는 보관합니다. Billing은 별도로 확인하세요.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['create', 'verify', 'cleanup'])
    parser.add_argument('--profile', required=True, help='AWS CLI 프로필 (IAM 사용자/Role)')
    parser.add_argument('--ssh-cidr', help='create에 필요한 관리자 공인 IPv4/32')
    args = parser.parse_args()
    PROFILE = args.profile
    os.umask(0o077)
    state = {}
    try:
        identity = aws('sts', 'get-caller-identity')
        if identity['Arn'].endswith(':root'):
            raise ValueError('루트 자격 증명 대신 IAM 사용자/Role을 사용하세요.')
        ACCOUNT = identity['Account']
        STATE_DIR.mkdir(mode=0o700, exist_ok=True)
        if args.action == 'create':
            if not args.ssh_cidr:
                raise ValueError('create에는 --ssh-cidr가 필요합니다.')
            create(args.ssh_cidr)
        else:
            state = json.loads(STATE.read_text())
            if (state['account'], state['profile'], state['region']) != (ACCOUNT, PROFILE, REGION):
                raise ValueError('생성 당시 계정/프로필/리전과 다릅니다.')
            verify() if args.action == 'verify' else cleanup()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print(f'실패: {error}\n기존 상태 파일은 보존됩니다. 필요하면 cleanup으로 정리하세요.', file=sys.stderr)
        sys.exit(1)

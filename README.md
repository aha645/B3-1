# 1. IAM->정책->정책생성
정책 편집기에서 (JSON으로 선택후) 아래내용 붙여넣음
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadEC2AndVPC",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "ec2:GetConsoleOutput",
        "ec2:GetConsoleScreenshot"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "ap-northeast-2"
        }
      }
    },
    {
      "Sid": "AllowWebLabManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateVpc",
        "ec2:DeleteVpc",
        "ec2:CreateSubnet",
        "ec2:DeleteSubnet",
        "ec2:ModifySubnetAttribute",
        "ec2:CreateInternetGateway",
        "ec2:AttachInternetGateway",
        "ec2:DetachInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:CreateRouteTable",
        "ec2:DeleteRouteTable",
        "ec2:CreateRoute",
        "ec2:DeleteRoute",
        "ec2:AssociateRouteTable",
        "ec2:DisassociateRouteTable",
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupEgress",
        "ec2:CreateKeyPair",
        "ec2:DeleteKeyPair",
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:CreateTags",
        "ec2:DeleteVolume"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "ap-northeast-2"
        }
      }
    }
  ]
}
```
JSON을 입력한 다음
1. 다음(Next) 버튼을 클릭합니다.
2. 정책 이름에 web-lab-policy를 입력합니다.
3. 설명에 AWS EC2 VPC Web Lab Permissions를 입력합니다.
4. 정책 생성(Create policy)을 클릭합니다.

# 2. IAM->IAM 사용자->그룹생성
IAM > IAM 사용자 > 사용자 생성 에서 그룹생성 버튼을 눌러서 사용자 그룹을 생성한다
![IAM 사용자그룹생성 이미지](images/IAM사용자그룹생성.png)
사용자 그룹이름은 web-lab-group 으로 입력하고 
권한정책은 검색창에 web-lab으로 입력한 후 정책생성버튼의 동그라미형태의 Refresh버튼을 누르고
web-lab-policy 정책이 화면에 보이면 체크박스를 선택한다.
그리고 사용자 그룹 생성 버튼을 클릭한다.
![IAM 사용자 그룹 생성 결과](images/IAM_IAM사용자_그룹생성결과화면.png) 
![IAM 사용자 사용자생성 검토및생성 화면](images/IAM_IAM사용자_사용자생성_검토및생성.png)
![IAM 사용자 사용자생성 암호검색 화면](images/IAM_IAM사용자_사용자생성_암호검색.png)

# 3. VPC생성
위에서 생성된 IAM 사용자 로그인 URL을 확인하고 보관합니다.
## STEP 1. 새로운 IAM 사용자로 로그인
1. 현재 AWS 콘솔에서 로그아웃합니다.
2. IAM 사용자 로그인 페이지로 이동합니다.
3. 다음 정보를 입력합니다.
항목	입력
계정 ID	본인 AWS 계정의 12자리 ID
IAM 사용자 이름	web-lab-user
암호	사용자 생성 시 설정한 암호

## STEP 2. 서울 리전 선택
AWS 콘솔 오른쪽 위의 리전 선택 메뉴에서 다음을 선택합니다.

아시아 태평양(서울) ap-northeast-2

IAM 화면에서는 글로벌이라고 표시될 수 있지만, VPC를 만드는 화면에서는 서울 리전이어야 합니다.

## STEP 3. VPC 생성
AWS 콘솔 상단 검색창에 VPC 입력

VPC → Your VPCs(VPC) → Create VPC(VPC 생성) 선택

다음과 같이 입력합니다.
항목	설정값
생성할 리소스	VPC만(VPC only)
이름 태그	web-lab-vpc
IPv4 CIDR	10.0.0.0/16
IPv6 CIDR	IPv6 CIDR 블록 없음
테넌시	기본값(Default)

VPC 생성 후의 상태
VPC: web-lab-vpc

10.0.0.0/16
아직 Subnet과 EC2를 생성하지 않은 상태

마지막으로 VPC 생성(Create VPC) 버튼을 클릭합니다.

VPC가 정상적으로 생성되면 상태가 Available로 나타납니다.
![VPC생성 화면](/images/VPC_VPC_VPC생성.png)
---

# 4. Public Subnet 생성 (다음에 수행할 작업)

> **진행 상태: 미검증 / 아직 완료 처리하지 않음**
>
> 앞에서 생성한 VPC 정보: 이름 `web-lab-vpc`, ID `vpc-0c62583f604f44241`, IPv4 CIDR `10.0.0.0/16`, 리전 `ap-northeast-2`.
>
> 다음 절차의 실제 완료 여부는 AWS 콘솔에서 확인 후 체크한다. 스크린샷은 본인이 촬영한 것만 추가한다.

## STEP 1. 서브넷 생성

AWS 콘솔(서울 리전) → **VPC → 서브넷(Subnets) → 서브넷 생성(Create subnet)**으로 이동한다.

| 항목 | 입력값 |
|---|---|
| VPC ID | `web-lab-vpc` (`vpc-0c62583f604f44241`) |
| 서브넷 이름 | `web-lab-public-subnet` |
| 가용 영역 | `ap-northeast-2a` (선택 가능한 영역 확인) |
| IPv4 서브넷 CIDR | `10.0.1.0/24` |
| 태그 키 / 값 | `Name` / `web-lab-public-subnet` |

**왜 이 주소를 사용하는가?** VPC `10.0.0.0/16` 안에서 서브넷 `10.0.1.0/24`라는 더 작은 네트워크를 나눈 것이다. 서브넷을 생성하는 것만으로 인터넷에 공개되는 것은 아니다.

**생성 후 작업:** 서브넷 선택 → **작업(Actions) → 서브넷 설정 편집(Edit subnet settings)** → **퍼블릭 IPv4 자동 할당(Enable auto-assign public IPv4 address)** 활성화 후 저장. 이 설정과 함께 EC2 생성 시 자동 할당 옵션도 확인한다. 공인 IPv4는 과금될 수 있다.

**확인 및 증빙:** 서브넷 ID, VPC ID, CIDR, 자동 할당 설정 화면을 캡처해서 `images/04-subnet.png`로 저장한다.

### 실제 AWS 화면 확인 (2026-11-05)

| 확인 항목 | 스크린샷에서 확인된 값 |
|---|---|
| 서브넷 이름 | `web-lab-public-subnet` |
| 서브넷 ID | `subnet-0c1774cc3cf2af370` |
| VPC ID | `vpc-0c62583f604f44241` |
| IPv4 CIDR | `10.0.1.0/24` |
| 가용 영역 | `ap-northeast-2a` (`apne2-az1`) |
| 서브넷 상태 | `Available` |
| 퍼블릭 IPv4 자동 할당 | **예 (2026-11-05 화면으로 확인)** |

**현재까지 검증된 사항:** 서브넷 생성과 VPC 연결은 정상이다. 추가 스크린샷에서 **퍼블릭 IPv4 자동 할당: 예**로 변경되었음을 확인했다. 이제 IGW 및 Route Table 구성을 진행한다.

실제 스크린샷 파일 `04-subnet.png`를 받았다. GitHub의 `images/04-subnet.png`에 별도 업로드가 필요하다 (README만 수정해도 이미지 파일이 업로드되는 것은 아니다).

- [x] 서브넷 생성 완료
- [x] 퍼블릭 IPv4 자동 할당 설정 확인
- [ ] 스크린샷 저장

# 5. Internet Gateway 생성과 VPC 연결

1. **VPC → 인터넷 게이트웨이(Internet gateways) → 인터넷 게이트웨이 생성**을 선택한다.
2. 이름 태그: `web-lab-igw` 입력 후 생성한다.
3. 생성한 IGW를 선택해 **작업 → VPC에 연결(Attach to VPC)**을 선택한다.
4. 연결할 VPC로 `web-lab-vpc`를 선택한다.
5. 연결 상태가 **Attached**인지 확인한다.

**왜 필요한가?** Internet Gateway는 인터넷과 VPC 간에 왕복 통신이 가능하도록 연결하는 관문이다. 단, IGW 연결만으로 외부 접속이 보장되지는 않는다. 라우팅과 보안 그룹도 맞아야 한다.

**증빙:** VPC에 연결된 IGW 화면을 `images/05-igw.png`로 저장한다.

- [ ] IGW 생성
- [ ] `web-lab-vpc`에 연결
- [ ] 스크린샷 저장

# 6. Public Route Table 생성과 서브넷 연결

1. **VPC → 라우팅 테이블(Route tables) → 라우팅 테이블 생성**으로 이동한다.
2. 이름: `web-lab-public-rt`, VPC: `web-lab-vpc`를 선택한다.
3. 생성한 테이블 → **라우팅(Routes) → 라우팅 편집(Edit routes)**을 선택한다.
4. `0.0.0.0/0` 목적지의 대상(Target)을 앞에서 만든 `web-lab-igw`로 설정하여 추가한다.
5. **서브넷 연결(Subnet associations) → 명시적 서브넷 연결 편집**에서 `web-lab-public-subnet`을 선택하고 저장한다.

기대하는 라우팅 규칙:

| 목적지(Destination) | 대상(Target) | 의미 |
|---|---|---|
| `10.0.0.0/16` | `local` | VPC 내부 네트워크 |
| `0.0.0.0/0` | `igw-...` | 나머지 IPv4 주소로 향하는 인터넷 트래픽 |

**왜 필요한가?** IGW를 만들더라도 서브넷에서 사용하는 라우팅 테이블에 인터넷 기본 경로가 없으면 EC2가 이 경로로 인터넷에 나갈 수 없다. 이 연결이 있어야 서브넷을 Public Subnet으로 사용할 수 있다.

**증빙:** Routes 탭과 Subnet associations 탭을 `images/06-routes.png`와 `images/07-subnet-association.png`로 캡처한다.

- [ ] 라우팅 테이블 생성
- [ ] `0.0.0.0/0 → IGW` 설정
- [ ] Public Subnet 연결
- [ ] 스크린샷 저장

# 7. Security Group 생성

1. **EC2 → 보안 그룹(Security Groups) → 보안 그룹 생성**으로 이동한다.
2. 이름: `web-lab-sg`, 설명: `HTTP 80 public, SSH 22 my IP`, VPC: `web-lab-vpc`.
3. **인바운드 규칙**을 다음과 같이 설정한다.

| 유형 | 프로토콜/포트 | 소스 |
|---|---|---|
| HTTP | TCP / 80 | `0.0.0.0/0` |
| SSH | TCP / 22 | **내 IP(My IP)**, 즉 `실제공인IP/32` |

아웃바운드는 이번 실습에서는 기본 허용 규칙(인터넷 요청용)을 사용한다.

- `0.0.0.0/0`은 모든 IPv4 주소를 뜻한다. 웹 공개용 **HTTP 80**에서만 사용한다.
- SSH는 자신의 공인 IP만 허용한다. **SSH 22를 `0.0.0.0/0`으로 열지 않는다.**
- 인바운드에 전체 포트(0~65535)를 공개하는 규칙을 생성하지 않는다.
- **Security Group은 EC2 네트워크 접근 제어, IAM은 AWS 리소스 생성/삭제 권한 제어**이다.

**증빙:** 보안 그룹 인바운드 규칙 화면을 `images/08-security-group.png`로 저장한다. 자신의 공인 IP 등 민감할 수 있는 정보를 외부에 공개할지 검토한다.

- [ ] HTTP 80 전체 허용
- [ ] SSH 22 내 IP만 허용
- [ ] 전체 포트 공개 규칙 없음
- [ ] 스크린샷 저장

# 8. EC2 인스턴스 생성

AWS 콘솔 → **EC2 → 인스턴스(Instances) → 인스턴스 시작(Launch instances)**.

| 항목 | 설정 |
|---|---|
| 이름 | `web-lab-ec2` |
| AMI | Ubuntu Server LTS (선택한 버전 기록) |
| 인스턴스 유형 | 계정에 표시된 프리 티어/크레딧 조건 확인 후 micro 계열 1대 |
| 키페어 | 새 키페어 `web-lab-key` 생성, `.pem` 안전 보관 |
| VPC | `web-lab-vpc` |
| Subnet | `web-lab-public-subnet` |
| 퍼블릭 IP 자동 할당 | 활성화 |
| 기존 보안 그룹 | `web-lab-sg` |
| 루트 EBS | gp3 8~10 GiB |
| 종료 시 삭제(Delete on termination) | 활성화 |

**주의:** AWS 계정 생성 시점 및 혜택에 따라 무료 범위가 다르며, 자동 할당 공인 IPv4도 별도 비용 항목이 될 수 있다. 실습 종료 후 반드시 제거한다.

생성 후 **Running**, 상태 검사 통과, **Public IPv4 address 존재**, VPC/Subnet/SG 일치를 확인한다. 공인 IP와 인스턴스 ID는 README의 '실제 검증 결과'에 기록한다(스크린샷에서는 필요한 정보만 공개).

**증빙:** EC2 요약을 `images/09-ec2-running.png`로 저장한다.

- [ ] EC2 실행 중
- [ ] 퍼블릭 IPv4 존재
- [ ] VPC / Subnet / SG 일치
- [ ] 스크린샷 저장

# 9. SSH 접속 및 Nginx 설치

## STEP 1. 내 컴퓨터(macOS/Linux)의 터미널에서 SSH 접속

키페어를 `~/Downloads/web-lab-key.pem`에 저장했다고 가정한다. 실제 파일 위치를 사용한다.

```bash
chmod 400 ~/Downloads/web-lab-key.pem
ssh -i ~/Downloads/web-lab-key.pem ubuntu@<PUBLIC_IP>
```

- `chmod 400`: 개인 키를 소유자만 읽도록 제한한다.
- `ssh -i`: 지정한 키로 원격 EC2에 접속한다.
- `ubuntu`: Ubuntu AMI에서 사용하는 일반적인 로그인 계정명이다.
- `<PUBLIC_IP>`: EC2 화면의 실제 Public IPv4로 교체한다. 꺾쇠까지 입력하지 않는다.

처음 접속할 때 호스트 키 지문을 확인한 후 승인한다.

## STEP 2. SSH로 접속한 EC2 Ubuntu 터미널에서 실행

```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl enable --now nginx
sudo systemctl status nginx
```

- `apt update`: 패키지 목록을 갱신한다.
- `apt install -y nginx`: 웹 서버를 설치한다.
- `systemctl enable --now nginx`: 지금 시작하고 부팅 시 자동 시작을 설정한다.
- `systemctl status nginx`: `active (running)` 여부를 확인한다.

HTTP 200 응답을 확인한다.

```bash
curl -i http://localhost
```

**성공 조건:** 실제 응답 상태 줄에 `HTTP/1.1 200 OK` 등의 200 응답이 표시된다.

EC2에서 외부 인터넷으로 나가는지도 확인한다.

```bash
curl -I https://example.com
```

**성공 조건:** DNS 및 HTTPS 연결에 성공하고 HTTP 응답 헤더를 수신한다. 이 테스트는 EC2의 **아웃바운드** 통신 검증이다.

**증빙:** `images/10-nginx-localhost.png`, `images/11-outbound.png`.

- [ ] SSH 접속 성공
- [ ] Nginx running 확인
- [ ] localhost HTTP 200 확인
- [ ] 아웃바운드 HTTPS 통신 성공
- [ ] 스크린샷 저장

# 10. 웹페이지 배포 및 외부 접속 확인

## STEP 1. EC2에서 테스트 페이지 만들기

```bash
sudo tee /var/www/html/index.html >/dev/null <<'EOF'
<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><title>AWS Web Lab</title></head>
<body><h1>Hello Cloud</h1><p>EC2 + Nginx 웹 서비스</p></body>
</html>
EOF
```

`tee`는 입력을 웹 루트의 HTML 파일에 저장하고, `EOF`는 여러 줄 입력의 시작과 끝을 구분한다.

정적 HTML/CSS/JavaScript 웹사이트가 이미 있다면 로컬 컴퓨터에서 `scp`로 전송한 다음, EC2에서 `/var/www/html/`에 복사할 수 있다. React/Vite라면 먼저 빌드한 산출물을 올려야 하며 백엔드 웹서비스는 별도 실행/프록시 설정이 필요하다.

## STEP 2. health 응답 만들기 (제출 방식 B)

```bash
echo OK | sudo tee /var/www/html/health
curl -i http://localhost/health
```

## STEP 3. EC2 외부의 **내 컴퓨터 터미널**에서 확인

```bash
curl -i http://<PUBLIC_IP>/health
```

- **방법 B 선택:** HTTP 상태가 `200 OK`이고 응답 본문이 `OK`이면 성공.
- 브라우저에서 `http://<PUBLIC_IP>`를 열어 `Hello Cloud`가 표시되는 방법 A로도 확인할 수 있다.
- **주의:** localhost 테스트만으로는 외부 공개를 증명할 수 없다. 반드시 EC2와 다른 컴퓨터/네트워크에서 확인한다.

**외부 접속 증빙:** URL을 포함한 명령과 응답 화면 또는 브라우저 주소창과 페이지를 `images/12-external-health.png`로 저장한다. 실제 성공 전에는 결과를 '성공'이라고 기록하지 않는다.

- [ ] EC2 내부 `/health` 정상
- [ ] 외부 PC의 `/health` 200 및 OK 확인
- [ ] 스크린샷 저장

## 실제 검증 결과 기록 (직접 수행 후 입력)

| 항목 | 실제 확인 결과 |
|---|---|
| 검증 방식 | B: `GET /health` (예정) |
| EC2 Public IPv4 | 미확인 |
| 공개 URL | 미확인 |
| Nginx 상태 | 미검증 |
| `curl -i http://localhost` | 미검증 |
| `curl -I https://example.com` | 미검증 |
| 외부 `curl -i http://<PUBLIC_IP>/health` | 미검증 |
| 검증 일시 (KST) | 미기록 |

> EC2를 삭제하면 URL은 더 이상 접속되지 않는다. 삭제 전에 외부 접속 증빙을 확보한다.

# 11. 제출 산출물 만들기

과제의 필수 제출 파일은 다음과 같다. 현재 없는 파일을 실제로 만들기 전까지는 완료로 표시하지 않는다.

```text
README.md
docs/architecture.png
docs/troubleshooting.md
docs/cleanup-checklist.md
images/12-external-health.png
```

## 11-1. 아키텍처 다이어그램

`docs/architecture.png`에는 아래 요소와 HTTP 요청 흐름을 포함한다.

```text
외부 사용자 --HTTP 80--> Internet
                                |
                                v
                          Internet Gateway
                                |
     +------ VPC 10.0.0.0/16 ---+------------------------+
     |                                                   |
     | Route Table: 0.0.0.0/0 -> IGW                     |
     |  +----- Public Subnet 10.0.1.0/24 --------------+  |
     |  |                                             |  |
     |  | EC2 (Public IPv4, Nginx, HTTP 80)           |  |
     |  | SG: HTTP 80 = 0.0.0.0/0                     |  |
     |  |     SSH 22 = 내 공인 IP/32                   |  |
     |  +---------------------------------------------+  |
     +---------------------------------------------------+
```

이 그림은 **논리적 구성도**이다. Route Table과 SG는 물리적인 중간 장비가 아니라 각각 라우팅 설정과 EC2 네트워크 접근 규칙을 나타낸다. draw.io 등으로 PNG로 만들어 제출한다.

## 11-2. 트러블슈팅 기록

`docs/troubleshooting.md`에 본인이 실제 경험한 문제 1건 이상을 **증상 → 가설 → 검증 → 조치 → 결과 → 재발 방지** 순서로 기록한다.

기록 예시: `ec2:AssociateVpcCidrBlock` 권한 부족으로 CIDR 추가 실패. 하지만 실제 검증 결과 및 최종 조치는 본인이 수행한 내용에 맞춰 작성한다. 다른 VPC를 새로 만든 것은 기존 기본 CIDR을 변경하는 것과 다르다는 점도 명확히 구분한다.

## 11-3. IAM 최소 권한 검토

현재 README의 IAM JSON은 서울 리전과 EC2 관련 API 작업을 제한하지만, `Resource: "*"`이므로 **리전 내 다른 리소스에도 허용 동작을 수행할 수 있는 초기 실습용 정책**이다. 과제의 엄격한 최소 권한을 충족한다고 단정하면 안 된다. 실제 정책에서 가능한 작업을 태그/리소스 ARN 등으로 추가 제한하고, 필요하지 않은 권한은 줄인다. 또한 운영하는 계정에 다른 정책이 부여되지 않았는지 확인한다.

# 12. 실습 종료 후 리소스 정리 (필수)

**외부 접속 증빙을 확보한 후** 리소스를 정리한다. AWS 콘솔 리전이 **서울**인지 다시 확인한다. 우선 각 리소스 ID를 기록하고 삭제 결과를 `docs/cleanup-checklist.md`에 남긴다.

- [ ] EC2 `web-lab-ec2` **Terminate** 후 Terminated 확인 (Stop만으로는 부족)
- [ ] EBS Volumes에서 실습 볼륨이 남았는지 확인 후 삭제
- [ ] Elastic IP가 있으면 연결 해제 및 **Release** (미생성 시 '미생성')
- [ ] 추가 생성한 NAT Gateway / ELB·ALB / RDS가 있으면 삭제 (없으면 '미생성')
- [ ] 실습용 Security Group 삭제
- [ ] 실습용 Route Table의 연결 해제 후 삭제
- [ ] Internet Gateway를 VPC에서 **Detach**한 후 삭제
- [ ] Public Subnet 삭제
- [ ] **실습용** VPC 삭제 (기존 기본 VPC는 삭제하지 않음)
- [ ] AWS의 실습용 Key Pair 정리 및 로컬 개인 키 안전하게 보관/삭제 결정
- [ ] Billing Dashboard 확인 및 정리 결과/일시 기록

**삭제 시 유의사항:** 리소스 간 의존성이 있어 일부 삭제 작업이 차단될 수 있다. 삭제 오류 메시지가 발생하면 연결 리소스를 먼저 정리한다. 자동 할당 퍼블릭 IPv4, EBS 등은 계정 혜택과 사용량에 따라 과금될 수 있다. 삭제 이후에도 청구 내역의 반영에는 시간이 걸릴 수 있으므로 '요금 0원'을 추정해 기재하지 않는다.

# 13. 다음 단계 실행 요약

**지금 바로 할 일: 4번 Public Subnet 생성부터 시작.** 진행할 때 AWS 화면 캡처를 보내주면 설정값을 확인하고, 실제 촬영한 스크린샷을 `images/`에 올린 뒤 README의 해당 이미지 링크를 연결하면 된다. 이 문서에서 **체크되지 않은 항목은 미완료/미검증**을 의미한다.

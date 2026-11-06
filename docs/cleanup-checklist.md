# 리소스 정리 체크리스트

대상 리전: 서울 (`ap-northeast-2`). 외부 접속 검증 후 EC2부터 VPC까지 정리했다. 정확한 작업 일시는 미기록이다. 아래에서 캡처로 확인된 상태와 사용자 확인에 따른 완료 기록을 구분한다.

| 완료 | 항목 | 대상 | 확인 결과 | 근거 |
|---|---|---|---|---|
| [x] | EC2 종료 | `i-0490197b568459dd8` | 종료됨 화면 확인 | [캡처](../images/12-instance-terminated_result.png) |
| [x] | EBS 잔존 확인 | 서울 리전 볼륨 목록 | 볼륨 없음 확인 | [캡처](../images/12-elasticBlockStore-check.png) |
| [x] | Elastic IP 잔존 확인 | 서울 리전 탄력적 IP 목록 | 주소 없음 확인 | [캡처](../images/12-elasticIP-check.png) |
| [x] | Subnet 삭제 | `subnet-0c1774cc3cf2af370` | 완료: 사용자 확인 / 캡처는 확인 팝업 | [캡처](../images/12-vpc-subnet-remove_popup.png) |
| [x] | Route Table 삭제 | `rtb-01d574886538f56d6` | 완료: 사용자 확인 / 기본 테이블은 VPC와 정리 | [캡처](../images/12-vpc-routingTable-remove_popup.png) |
| [x] | Security Group 삭제 | `sg-0ab95537414997679` | 완료: 사용자 확인 / 기본 그룹은 VPC와 정리 | [캡처](../images/12-vpc-securityGroup-remove_popup.png) |
| [x] | IGW 분리 및 삭제 | `igw-0b643cdd8ed2935a5` | Detached 화면 확인 / 삭제 완료는 사용자 확인 | [캡처](../images/12-vcp-igw-remove.png) |
| [x] | VPC 삭제 | `vpc-0c62583f604f44241` | 완료: 사용자 확인 / 캡처는 확인 팝업 | [캡처](../images/12-vpc-vpc-remove_popup.png) |

전체 작업 화면은 [README의 정리 과정](../README.md#12-실습-종료-후-리소스-정리)에 메뉴 선택 → 확인 팝업 순서로 수록했다.


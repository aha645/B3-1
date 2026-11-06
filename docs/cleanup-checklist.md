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

## 작업 중 확인 사항

- 서브넷 삭제 팝업에는 `ram:GetResourceShareAssociations` 조회 권한 경고가 있었다. 권한 추가 여부는 확인되지 않았으며, 삭제 완료는 사용자 확인을 근거로 기록했다.
- 기본 Route Table과 기본 Security Group은 개별 삭제가 제한되어 VPC 삭제 시 함께 정리하는 대상으로 구분했다.
- EBS와 Elastic IP는 목록에 잔존 리소스가 없음을 확인했다. 별도 볼륨 삭제나 Elastic IP 릴리스를 수행한 것으로 기록하지 않는다.

## 추가 확인 항목

- [ ] NAT Gateway·ELB/ALB·RDS 생성 여부와 잔존 여부 확인 (현재 증빙 없음)
- [ ] 직접 생성한 EBS 스냅샷 잔존 여부 확인
- [ ] AWS 키페어 `web-lab-key` 정리 및 로컬 개인 키 보관/삭제 결정
- [ ] Billing Dashboard에서 발생 비용 확인 (삭제 후에도 반영 지연 및 기존 사용 요금 가능)

위 추가 항목은 미확인이다. 주요 리소스 정리 완료를 계정 전체 리소스 부재 또는 청구 금액 0원으로 확대 해석하지 않는다.

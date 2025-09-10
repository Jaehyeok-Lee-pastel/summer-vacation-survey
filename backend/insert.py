import random
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector

fake = Faker('ko_KR')

# MySQL 연결 정보
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',        # MySQL 비밀번호
    'database': 'summer_vacation_db',
    'charset': 'utf8mb4'
}

# 연령대, 성별, 휴가 유형 등
age_groups = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
genders = ["남성", "여성"]
vacation_types = ['해수욕, 물놀이', '등산, 캠핑', '문화생활', '도시 관광', '휴양·힐링', '맛집 투어', '친척·지인 방문', '기타']
location_types = ['국내', '해외']
transportations = ['자가용', '대중교통', '비행기', '기차', '버스']
durations = ['1박2일', '2박3일', '3박4일', '4박5일', '1주일 이상']
companions = ['혼자', '친구', '가족', '연인', '기타']
costs = ['10만원 이하', '10~30만원', '30~50만원', '50~100만원', '100만원 이상']
satisfactions = [1,2,3,4,5]
next_vacation_types = vacation_types

# MySQL 연결
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# auth_user에 존재하는 user_id 가져오기
cursor.execute("SELECT id FROM auth_user")
user_ids = [row[0] for row in cursor.fetchall()]
if not user_ids:
    raise Exception("auth_user 테이블에 사용자 데이터가 없습니다. 먼저 유저를 생성하세요.")

base_time = datetime.now()

for age in age_groups:
    for i in range(100):  # 연령대별 100개
        gender = random.choice(genders)
        vacation_type = random.choice(vacation_types)
        location_type = random.choice(location_types)
        domestic_location = fake.city() if location_type == '국내' else None
        overseas_location = fake.city() if location_type == '해외' else None
        transportation = random.choice(transportations)
        duration = random.choice(durations)
        companion = random.choice(companions)
        cost = random.choice(costs)
        satisfaction = random.choice(satisfactions)
        next_vacation_type = random.choice(next_vacation_types)
        created_at = (base_time + timedelta(seconds=i)).strftime('%Y-%m-%d %H:%M:%S')
        user_id = random.choice(user_ids)  # 실제 존재하는 user_id 사용

        sql = """INSERT INTO surveys_survey
(age_group, gender, vacation_type, location_type, domestic_location, overseas_location,
 transportation, duration, companion, cost, satisfaction, next_vacation_type, created_at, user_id)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

        values = (
            age, gender, vacation_type, location_type,
            domestic_location, overseas_location,
            transportation, duration, companion, cost, satisfaction,
            next_vacation_type, created_at, user_id
        )

        cursor.execute(sql, values)

# 커밋
conn.commit()
print("총 데이터 삽입 완료: 600개")

# 연결 종료
cursor.close()
conn.close()

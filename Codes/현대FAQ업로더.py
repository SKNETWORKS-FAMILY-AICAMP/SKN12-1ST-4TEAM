from mysql import connector

args = {
  'host' : 'localhost',
  'user' : 'root',
  'password' : 'password',
  'port' : 3306
}

try:
    conn = connector.connect(**args)
    cursor = conn.cursor()

    #데이터 베이스 생성 및 선택
    cursor.execute("create database if not exists faq_db")
    cursor.execute("use faq_db")
    
    #테이블 생성
    sql = '''
        create table if not exists faq_hyundai(
        id int auto_increment primary key,
        category varchar(100),
        question varchar(1000),
        answer TEXT
    )
    '''
    cursor.execute(sql)
    
    #데이터 삽입
    for category_list, question_list, answer_list in zip(total_categories, total_questions, total_answers):
        for c, q, a in zip(category_list, question_list, answer_list):
            insert_sql = 'insert into faq_hyundai values (null, %s, %s, %s)'
            cursor.execute(insert_sql, (c, q, a))
    conn.commit()
except Exception as e:
  print(f'error {e}')
finally:
    cursor.close()
    conn.close()
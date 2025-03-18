from mysql import connector
args = {
    'host': "localhost",         
    'user': "root",              
    'password': "password", 
    'port': 3306
}
try:
    conn = connector.connect(**args)
    cursor = conn.cursor()
    cursor.execute("create database if not exists faq_db")
    cursor.execute("use faq_db")
    cursor.execute("""
    create table if not exists faq_kia(
    id int auto_increment primary key,
    category varchar(100),
    question varchar(1000),
    answer TEXT;
     """)
    sql = 'insert into faq_kia values(null, %s, %s, %s)'
    for data in result:
        cursor.execute(sql,(data['category'], data['question'], data['answer']) )
        print(data['category'], data['question'], data['answer'])
    conn.commit()
except Exception as e:
  print(f'error {e}')
finally:
    cursor.close()
    conn.close()
import sqlite3
import json

def count_event(db_path, file_directory=r'D:\test', registry_directory='HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'):
    # Kết nối tới cơ sở dữ liệu SQLite
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        sqlCommand = f"""
        SELECT OBject, Action FROM Config
        """
        cursor.execute(sqlCommand)
        operations = {}

        for line in cursor:
            if line == ('Registry', 'Add'):
                operations['Create Registry'] = 0
            else:
                event_name = f'{line[1]} {line[0]}'
                operations[event_name] = 0 

        if operations:
            for key, value in operations.items():

                sqlCommand = f"""
                SELECT * FROM Logs WHERE NAME="{key}"
                """
                cursor.execute(sqlCommand)
                data = cursor.fetchall()

                file_names = set()
                for row in data:
                    json_data = json.loads(row[3])  
                    action, object = row[1].split(' ')
                    if object == 'File':
                        file_path = json_data.get("fields", {}).get("file_path", "")
                        file_name = json_data.get("fields",{}).get("file_name","")
                        if file_path.startswith(file_directory) and file_name.endswith('.exe') and file_name not in file_names:
                            operations[f'{action} {object}'] +=1
                            file_names.add(file_name)
                    elif object == 'Process':
                        cmd_line = json_data.get("fields", {}).get("command_line", "")
                        print(cmd_line)
                        if cmd_line.endswith('calc.exe'):
                            operations[f'{action} {object}'] +=1
                    elif object == 'Registry':
                        image_path = json_data.get("fields", {}).get("image_path", "")
                        key = json_data.get("fields", {}).get("key", "")
                        print(f'Image={image_path}, Key={key}')
                        if image_path.endswith('python.exe') and key == registry_directory:
                            operations[f'{action} {object}'] +=1
            return operations
if __name__ == "__main__":
    print(count_event(r'D:\My Project\Agent_Hunting\data.db'))

    